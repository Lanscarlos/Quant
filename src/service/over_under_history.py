"""
大小球变盘历史抓取 — vip.titan007.com/changeDetail/overunder.aspx

GB2312 编码的 HTML 页面，服务端渲染。仅抓取 Bet365 (company_id=8)。
通过 font 颜色判断涨跌方向 (green=up, red=down)。
"""
import requests
from bs4 import BeautifulSoup

COMPANY_365 = 8  # Bet365

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://vip.titan007.com/",
}

_COLOR_DIR = {"green": "up", "red": "down"}


def _cell_text(td) -> str:
    return td.get_text(strip=True)


def _cell_dir(td) -> str:
    font = td.find("font")
    if font:
        color = (font.get("color") or "").lower()
        return _COLOR_DIR.get(color, "unchanged")
    return "unchanged"


def _find_history_table(soup: BeautifulSoup):
    """找数据表：行中 tds[2] 可转 float 的第一张表。"""
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            tds = row.find_all("td")
            if len(tds) < 6:
                continue
            try:
                float(tds[2].get_text(strip=True))
                return table
            except ValueError:
                continue
    return None


def _fetch_and_parse(mid: str | int) -> list[dict]:
    url = (
        f"https://vip.titan007.com/changeDetail/overunder.aspx"
        f"?id={mid}&companyID={COMPANY_365}&l=0"
    )
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    encoding = resp.encoding or "gb2312"
    if encoding.lower() in ("iso-8859-1", "windows-1252"):
        encoding = "gb2312"
    html = resp.content.decode(encoding, errors="replace")

    soup = BeautifulSoup(html, "html.parser")
    table = _find_history_table(soup)
    if not table:
        return []

    # 列顺序：tds[0]=比赛分钟 tds[1]=比分 tds[2]=大球赔率
    #          tds[3]=进球线   tds[4]=小球赔率 tds[5]=变化时间 tds[6]=状态
    result = []
    for row in table.find_all("tr"):
        tds = row.find_all("td")
        if len(tds) < 6:
            continue
        try:
            float(tds[2].get_text(strip=True))
        except ValueError:
            continue  # 跳过表头行

        change_time = _cell_text(tds[5])
        if not change_time:
            continue

        result.append({
            "change_time": change_time,
            "score":       _cell_text(tds[1]),
            "over_odds":   _cell_text(tds[2]),
            "goals_line":  _cell_text(tds[3]),
            "under_odds":  _cell_text(tds[4]),
            "is_opening":  "0",
            "over_dir":    _cell_dir(tds[2]),
            "under_dir":   _cell_dir(tds[4]),
        })

    # 最后一条（最早时间戳）为开盘赔率
    if result:
        result[-1]["is_opening"] = "1"

    return result


# ── 公开 API ─────────────────────────────────────────────────────────────────

def fetch_over_under_history(mid: str | int, match_year: int, tracker=None) -> int:
    """抓取并持久化 Bet365 大小球变盘历史。

    Args:
        mid:        赛事 schedule_id
        match_year: 赛事年份，用于补全 "MM-DD HH:MM" 时间戳
        tracker:    可选 ProgressTracker，用于上报子步骤进度
    Returns: 写入行数
    """
    from contextlib import nullcontext
    from src.db import get_conn
    from src.db.repo.over_under_history import upsert_over_under_365_history

    def _t(key, label):
        return tracker.task(key, label) if tracker else nullcontext()

    conn = get_conn()

    with _t('fetch', '下载 Bet365 大小球变盘历史'):
        records = _fetch_and_parse(mid)

    with _t('save', f'保存变盘历史 ({len(records)} 条)'):
        return upsert_over_under_365_history(conn, int(mid), records, match_year)
