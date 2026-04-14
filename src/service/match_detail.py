"""
赛事详情页抓取 — zq.titan007.com/analysis/{mid}sb.htm

UTF-8 编码的 HTML 页面，一次请求提取:
  - 基本信息 (内联 JS 变量)
  - 联赛排名 (#porlet_5 表格: 全场/半场 × 总/主/客/近6)
  - 近 6 场 (h_data / a_data JS 数组)
  - 交手记录 (v_data JS 数组)
  - 比赛时间 (strTime)
"""
import ast
import re

import requests
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://zq.titan007.com/",
}

_STAT_COLS = ["played", "W", "D", "L", "GF", "GA", "GD", "pts", "rank", "win_rate"]


def _parse_title_league(html: str) -> str:
    """从 <title> 提取联赛中文名。

    title 格式：'主队 VS 客队(YYYY-YYYY赛季{联赛名})-数据分析-...'
    提取括号内内容并去掉赛季前缀，如 '2025-2026赛季欧冠杯' → '欧冠杯'。
    """
    m = re.search(r"<title>[^<]*?\((.+?)\)", html)
    if not m:
        return ""
    raw = m.group(1).strip()
    return re.sub(r"^\d{4}-\d{4}(赛季)?", "", raw).strip()
_ROW_LABELS = ["total", "home", "away", "last6"]

# 表格第一列文字 → scope 名，用于按标签定位数据行（免受表头行数影响）
_SCOPE_LABEL_MAP = {'总': 'total', '主': 'home', '客': 'away', '近6': 'last6'}


def _fetch_html(match_id: str | int) -> str:
    url = f"https://zq.titan007.com/analysis/{match_id}sb.htm"
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.content.decode("utf-8", errors="replace")


# ── JS 变量提取 ──────────────────────────────────────────────────────────────

def _js_str(html: str, var: str) -> str:
    m = re.search(rf"var {var}\s*=\s*'([^']*)'", html)
    if not m:
        m = re.search(rf'var {var}\s*=\s*"([^"]*)"', html)
    return m.group(1) if m else ""


def _js_int(html: str, var: str) -> str:
    m = re.search(rf"var {var}\s*=\s*(-?\d+)", html)
    return m.group(1) if m else ""


# ── 近期/交手记录解析 (h_data / a_data / v_data) ────────────────────────────

def _strip_team_html(html_str: str) -> str:
    soup = BeautifulSoup(str(html_str), "html.parser")
    for hp in soup.find_all("span", class_="hp"):
        hp.decompose()
    return soup.get_text(strip=True)


def _parse_team_html(html_str: str) -> tuple[str, int | None]:
    """从队名 HTML 中提取队名和排名。

    title 属性格式:
      同联赛赛事: "格拉茨风暴  排名:1"
      跨联赛赛事: "阿森纳  排名:英超1"  （联赛名前缀 + 排名数字）
    """
    soup = BeautifulSoup(str(html_str), "html.parser")
    rank = None
    span = soup.find("span", attrs={"title": True})
    if span:
        # [^\d]* 跳过可能的联赛名前缀，取末尾数字
        m = re.search(r"排名[:：][^\d]*(\d+)", span["title"])
        if m:
            rank = int(m.group(1))
    for hp in soup.find_all("span", class_="hp"):
        hp.decompose()
    name = soup.get_text(strip=True)
    return name, rank


def _parse_match_array(html: str, data_var: str, limit: int = 6) -> list[dict]:
    """解析 h_data / a_data / v_data 内联 JS 数组。"""
    m = re.search(rf"var {data_var}\s*=\s*(\[.*?\]);", html, re.DOTALL)
    if not m:
        return []
    try:
        entries = ast.literal_eval(m.group(1))
    except (ValueError, SyntaxError):
        return []

    results = []
    for entry in entries:
        if len(entry) < 16:
            continue
        home_ft = int(entry[8]) if entry[8] != "" else 0
        away_ft = int(entry[9]) if entry[9] != "" else 0
        home_name, home_rank = _parse_team_html(entry[5])
        away_name, away_rank = _parse_team_html(entry[7])
        results.append({
            "date":      entry[0],
            "league":    entry[2],
            "home_id":   int(entry[4]),
            "home_name": home_name,
            "home_rank": home_rank,
            "away_id":   int(entry[6]),
            "away_name": away_name,
            "away_rank": away_rank,
            "home_ft":   home_ft,
            "away_ft":   away_ft,
            "ft_score":  f"{home_ft}-{away_ft}",
            "ht_score":  entry[10],
            "handicap":  entry[11],
            "result":    int(entry[12]),
            "hc_result": int(entry[13]),
            "match_id":  int(entry[15]),
        })
        if len(results) >= limit:
            break
    return results


# ── 排名表格解析 ─────────────────────────────────────────────────────────────

def _parse_stats_from_rows(rows) -> dict:
    """从行列表中按第一列标签提取各 scope 统计，跳过表头行。"""
    result = {}
    for row in rows:
        cells = row.find_all("td")
        if not cells:
            continue
        scope = _SCOPE_LABEL_MAP.get(cells[0].get_text(strip=True))
        if scope is None:
            continue
        for j, col in enumerate(_STAT_COLS):
            cell = cells[j + 1] if (j + 1) < len(cells) else None
            result[f"{scope}_{col}"] = cell.get_text(strip=True) if cell else ""
    return result


def _parse_stats_table(table) -> dict:
    """按标签提取排名表格，兼容表头行数不同的布局。"""
    return _parse_stats_from_rows(table.find_all("tr"))


def _split_stacked_standings(inner_table) -> list[tuple[str, list]]:
    """将主客堆叠在同一 td 内的表格拆分为两方数据行。

    欧战等跨联赛赛事的全场排名区只有 1 个 td，主客数据纵向堆叠：
      [单格行] 队名分隔 → 之后的数据行属于该队
    Returns: [('home', row_list), ('away', row_list)]
    """
    all_rows = inner_table.find_all("tr")
    # 恰好只有 1 个 td 的行作为队名分隔行
    dividers = [i for i, r in enumerate(all_rows) if len(r.find_all("td")) == 1]
    sections = []
    for idx, start in enumerate(dividers):
        end = dividers[idx + 1] if idx + 1 < len(dividers) else len(all_rows)
        sections.append(all_rows[start:end])
    return list(zip(["home", "away"], sections))


# ── 主解析 ───────────────────────────────────────────────────────────────────

def _parse_detail(html: str) -> dict:
    record: dict = {}
    record["schedule_id"]   = _js_int(html, "scheduleID")
    record["match_state"]   = _js_int(html, "matchState")
    record["home_team_id"]  = _js_int(html, "h2h_home")
    record["away_team_id"]  = _js_int(html, "h2h_away")
    record["home_team"]     = _js_str(html, "hometeam")
    record["away_team"]     = _js_str(html, "guestteam")
    record["match_time"]    = _js_str(html, "strTime")
    record["league_name_cn"] = _parse_title_league(html)

    soup = BeautifulSoup(html, "html.parser")
    porlet5 = soup.find("div", id="porlet_5")
    if not porlet5:
        return record

    outer_table = porlet5.find("table")
    if not outer_table:
        return record

    container = outer_table.find("tbody") or outer_table
    outer_rows = container.find_all("tr", recursive=False)

    for period, outer_row in zip(["ft", "ht"], outer_rows):
        tds = outer_row.find_all("td", recursive=False)
        if not tds:
            continue

        if len(tds) >= 2:
            # 标准布局：主/客各占一个 td（同联赛赛事常见）
            for side, td in zip(["home", "away"], tds[:2]):
                inner_table = td.find("table")
                if not inner_table:
                    continue
                stats = _parse_stats_table(inner_table)
                for k, v in stats.items():
                    record[f"{side}_{period}_{k}"] = v
        else:
            # 堆叠布局：主/客数据纵向合并在单一 td 内（跨联赛赛事）
            inner_table = tds[0].find("table")
            if not inner_table:
                continue
            for side, rows in _split_stacked_standings(inner_table):
                stats = _parse_stats_from_rows(rows)
                for k, v in stats.items():
                    record[f"{side}_{period}_{k}"] = v

    record["home_recent"] = _parse_match_array(html, "h_data")
    record["away_recent"] = _parse_match_array(html, "a_data")

    return record


# ── 公开 API ─────────────────────────────────────────────────────────────────

def fetch_match_all(match_id: str | int, tracker=None) -> dict:
    """一次 HTTP 请求抓取并持久化: 排名 + 近期 + 交手。

    Args:
        tracker: 可选 ProgressTracker，用于向 UI 上报子步骤进度。
    Returns: {'match_time': str, 'match_year': int}
    """
    from contextlib import nullcontext
    from datetime import datetime
    from src.db import get_conn
    from src.db.repo.teams import ensure_team
    from src.db.repo.matches import ensure_match_stub, upsert_match_basics
    from src.db.repo.standings import upsert_standings
    from src.db.repo.recent_matches import upsert_recent_matches
    from src.db.repo.h2h_matches import upsert_h2h_matches

    def _t(key: str, label: str):
        return tracker.task(key, label) if tracker else nullcontext()

    conn = get_conn()

    with _t('html', '下载页面 HTML'):
        html = _fetch_html(match_id)

    with _t('parse', '解析基本信息 + 联赛排名'):
        record = _parse_detail(html)

    # 直接 URL 入口时 matches / teams 表可能尚无此行，需先写入骨架记录
    # 以满足 match_standings / match_recent / match_h2h 的外键约束
    with _t('ensure_base', '确保赛事与球队基础记录'):
        sid  = int(record.get('schedule_id')  or 0)
        htid = int(record.get('home_team_id') or 0)
        atid = int(record.get('away_team_id') or 0)
        if not (sid and htid and atid):
            raise ValueError(f'页面缺少关键字段: schedule_id={sid}, home={htid}, away={atid}')
        ensure_team(conn, htid, record.get('home_team', ''))
        ensure_team(conn, atid, record.get('away_team', ''))
        # 用 upsert_match_basics 代替 ensure_match_stub，额外写入联赛名
        upsert_match_basics(
            conn, sid,
            record.get('match_time', ''),
            htid, atid,
            league_name_cn=record.get('league_name_cn') or None,
        )

    with _t('standings', '保存联赛排名'):
        upsert_standings(conn, record)

    if tracker:
        _h_rank = record.get('home_ft_total_rank', '') or ''
        _a_rank = record.get('away_ft_total_rank', '') or ''
        _t_s = tracker.task('standings_rank', '主赛事球队排名').start()
        if not _h_rank and not _a_rank:
            _t_s.done('未获取到排名数据（源站未提供）')
        else:
            _parts = []
            if _h_rank:
                _parts.append(f'主队第 {_h_rank} 位')
            if _a_rank:
                _parts.append(f'客队第 {_a_rank} 位')
            _t_s.done(' / '.join(_parts))

    with _t('recent', '保存近期比赛'):
        upsert_recent_matches(conn, record)

    if tracker:
        _all_recent = (record.get('home_recent') or []) + (record.get('away_recent') or [])
        _total_r    = len(_all_recent)
        _ranked_r   = sum(
            1 for r in _all_recent
            if r.get('home_rank') is not None or r.get('away_rank') is not None
        )
        _t_r = tracker.task('recent_rank', '近期赛事排名').start()
        if _total_r == 0:
            _t_r.done('无近期赛事数据')
        elif _ranked_r == 0:
            _t_r.done(f'共 {_total_r} 场，均无排名（源站未提供）')
        else:
            _t_r.done(f'{_ranked_r}/{_total_r} 场包含排名')

    with _t('h2h_parse', '解析交手记录'):
        h2h_records = _parse_match_array(html, "v_data", limit=20)

    with _t('h2h_save', f'保存交手记录 ({len(h2h_records)} 场)'):
        upsert_h2h_matches(conn, int(match_id), h2h_records)

    if tracker:
        _total_h    = len(h2h_records)
        _ranked_h   = sum(
            1 for r in h2h_records
            if r.get('home_rank') is not None or r.get('away_rank') is not None
        )
        _t_h = tracker.task('h2h_rank', '交手记录排名').start()
        if _total_h == 0:
            _t_h.done('无交手记录数据')
        elif _ranked_h == 0:
            _t_h.done(f'共 {_total_h} 场，均无排名（源站未提供）')
        else:
            _t_h.done(f'{_ranked_h}/{_total_h} 场包含排名')

    match_time = record.get("match_time", "")
    try:
        match_year = int(match_time[:4])
    except (ValueError, IndexError):
        match_year = datetime.now().year

    return {"match_time": match_time, "match_year": match_year}


def fetch_match_time(match_id: str | int) -> str | None:
    """仅抓取比赛开球时间，如 "2026-03-07 20:45"。"""
    try:
        html = _fetch_html(match_id)
        return _js_str(html, "strTime") or None
    except Exception:
        return None


def fetch_match_basics(match_id: str | int) -> dict | None:
    """轻量抓取赛事基础信息（不写 standings/recent/h2h）。

    适用于列表页首次加载时为缺失赛事填充骨架：
      - matches 表写入 schedule_id / match_time / home/away_team_id / league_name_cn
      - teams   表写入 team_id / team_name_cn（INSERT OR IGNORE）

    Returns:
        {'schedule_id', 'match_time', 'league_name_cn', 'home_team', 'away_team'}
        或 None（网络/解析失败）。
    """
    from src.db import get_conn
    from src.db.repo.teams import ensure_team
    from src.db.repo.matches import upsert_match_basics

    try:
        html = _fetch_html(match_id)
    except Exception:
        return None

    sid   = int(_js_int(html, "scheduleID") or 0)
    htid  = int(_js_int(html, "h2h_home")   or 0)
    atid  = int(_js_int(html, "h2h_away")   or 0)
    if not (sid and htid and atid):
        return None

    mt           = _js_str(html, "strTime")
    home_name    = _js_str(html, "hometeam")
    away_name    = _js_str(html, "guestteam")
    league_name  = _parse_title_league(html) or None

    conn = get_conn()
    ensure_team(conn, htid, home_name)
    ensure_team(conn, atid, away_name)
    upsert_match_basics(conn, sid, mt, htid, atid, league_name_cn=league_name)

    return {
        "schedule_id":    sid,
        "match_time":     mt,
        "league_name_cn": league_name,
        "home_team":      home_name,
        "away_team":      away_name,
    }
