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
_ROW_LABELS = ["total", "home", "away", "last6"]


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
        results.append({
            "date":      entry[0],
            "league":    entry[2],
            "home_id":   int(entry[4]),
            "home_name": _strip_team_html(entry[5]),
            "away_id":   int(entry[6]),
            "away_name": _strip_team_html(entry[7]),
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

def _parse_stats_table(table) -> dict:
    rows = table.find_all("tr")
    result = {}
    for i, label in enumerate(_ROW_LABELS):
        row = rows[2 + i] if (2 + i) < len(rows) else None
        cells = row.find_all("td") if row else []
        for j, col in enumerate(_STAT_COLS):
            cell = cells[j + 1] if (j + 1) < len(cells) else None
            result[f"{label}_{col}"] = cell.get_text(strip=True) if cell else ""
    return result


# ── 主解析 ───────────────────────────────────────────────────────────────────

def _parse_detail(html: str) -> dict:
    record: dict = {}
    record["schedule_id"]  = _js_int(html, "scheduleID")
    record["match_state"]  = _js_int(html, "matchState")
    record["home_team_id"] = _js_int(html, "h2h_home")
    record["away_team_id"] = _js_int(html, "h2h_away")
    record["home_team"]    = _js_str(html, "hometeam")
    record["away_team"]    = _js_str(html, "guestteam")
    record["match_time"]   = _js_str(html, "strTime")

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
        if len(tds) < 2:
            continue
        for side, td in zip(["home", "away"], tds):
            inner_table = td.find("table")
            if not inner_table:
                continue
            stats = _parse_stats_table(inner_table)
            for k, v in stats.items():
                record[f"{side}_{period}_{k}"] = v

    record["home_recent"] = _parse_match_array(html, "h_data")
    record["away_recent"] = _parse_match_array(html, "a_data")

    return record


# ── 公开 API ─────────────────────────────────────────────────────────────────

def fetch_match_all(match_id: str | int) -> dict:
    """一次 HTTP 请求抓取并持久化: 排名 + 近期 + 交手。

    Returns: {'match_time': str, 'match_year': int}
    """
    from datetime import datetime
    from src.db import get_conn
    from src.db.repo.standings import upsert_standings
    from src.db.repo.recent_matches import upsert_recent_matches
    from src.db.repo.h2h_matches import upsert_h2h_matches

    conn = get_conn()
    html = _fetch_html(match_id)
    record = _parse_detail(html)

    upsert_standings(conn, record)
    upsert_recent_matches(conn, record)

    h2h_records = _parse_match_array(html, "v_data", limit=20)
    upsert_h2h_matches(conn, int(match_id), h2h_records)

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
