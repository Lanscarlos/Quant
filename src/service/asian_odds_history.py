"""
亚盘变盘历史抓取 — vip.titan007.com/changeDetail/handicap.aspx

GB2312 编码的 HTML 页面，服务端渲染。仅抓取 Bet365 (company_id=8)。
通过 font 颜色判断涨跌方向 (green=up, red=down)。
"""
import re

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
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        data_rows = [r for r in rows if r.find_all("td")]
        if not data_rows:
            continue
        tds = data_rows[0].find_all("td")
        if len(tds) < 5:
            continue
        try:
            float(tds[2].get_text(strip=True))
            return table
        except ValueError:
            continue
    return None


def _fetch_and_parse(mid: str | int) -> list[dict]:
    url = (
        f"https://vip.titan007.com/changeDetail/handicap.aspx"
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

    result = []
    for row in table.find_all("tr")[1:]:
        tds = row.find_all("td")
        if len(tds) < 5:
            continue

        time_text = _cell_text(tds[0])
        is_opening = time_text.endswith("(初盘)")
        change_time = re.sub(r"\(初盘\)$", "", time_text).strip()

        if not is_opening and len(tds) >= 6:
            is_opening = _cell_text(tds[5]) == "开"

        if not change_time:
            continue

        result.append({
            "change_time": change_time,
            "score":       _cell_text(tds[1]),
            "home_odds":   _cell_text(tds[2]),
            "handicap":    _cell_text(tds[3]),
            "away_odds":   _cell_text(tds[4]),
            "is_opening":  "1" if is_opening else "0",
            "home_dir":    _cell_dir(tds[2]),
            "away_dir":    _cell_dir(tds[4]),
        })

    return result


# ── 公开 API ─────────────────────────────────────────────────────────────────

def fetch_asian_odds_history(mid: str | int, match_year: int, tracker=None) -> int:
    """抓取并持久化 Bet365 亚盘变盘历史。

    Args:
        mid:        赛事 schedule_id
        match_year: 赛事年份，用于补全 "MM-DD HH:MM" 时间戳
        tracker:    可选 ProgressTracker，用于上报子步骤进度
    Returns: 写入行数
    """
    from contextlib import nullcontext
    from src.db import get_conn
    from src.db.repo.asian_odds_history import upsert_365_history

    def _t(key, label):
        return tracker.task(key, label) if tracker else nullcontext()

    conn = get_conn()

    with _t('fetch', '下载 Bet365 亚盘变盘历史'):
        records = _fetch_and_parse(mid)

    with _t('save', f'保存变盘历史 ({len(records)} 条)'):
        return upsert_365_history(conn, int(mid), records, match_year)
