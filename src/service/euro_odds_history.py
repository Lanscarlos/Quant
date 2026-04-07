"""
欧赔变盘历史抓取 — 1x2.titan007.com/OddsHistory.aspx

UTF-8 编码的 HTML 页面，服务端渲染。
从 <span id='odds'> 表格提取每次赔率变动记录，
通过 font 颜色判断涨跌方向 (green=up, red=down)。
"""
import re

import requests
from bs4 import BeautifulSoup

COMPANY_WH    = 115  # William Hill 威廉希尔
COMPANY_CORAL = 82   # Ladbrokes/Coral 立博

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://1x2.titan007.com/",
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


def _fetch_and_parse(rid: str | int, mid: str | int, cid: str | int) -> list[dict]:
    url = (
        f"https://1x2.titan007.com/OddsHistory.aspx"
        f"?id={rid}&sid={mid}&cid={cid}&l=0"
    )
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    html = resp.content.decode("utf-8", errors="replace")

    soup = BeautifulSoup(html, "html.parser")
    odds_span = soup.find(id="odds")
    if not odds_span:
        return []

    table = odds_span.find("table")
    if not table:
        return []

    result = []
    for row in table.find_all("tr")[1:]:
        tds = row.find_all("td")
        if len(tds) < 11:
            continue

        time_text = _cell_text(tds[10])
        is_opening = time_text.endswith("(初盘)")
        change_time = re.sub(r"\(初盘\)$", "", time_text).strip()

        result.append({
            "win":         _cell_text(tds[0]),
            "draw":        _cell_text(tds[1]),
            "lose":        _cell_text(tds[2]),
            "win_prob":    _cell_text(tds[3]),
            "draw_prob":   _cell_text(tds[4]),
            "lose_prob":   _cell_text(tds[5]),
            "payout_rate": _cell_text(tds[6]),
            "kelly_win":   _cell_text(tds[7]),
            "kelly_draw":  _cell_text(tds[8]),
            "kelly_lose":  _cell_text(tds[9]),
            "change_time": change_time,
            "is_opening":  "1" if is_opening else "0",
            "win_dir":     _cell_dir(tds[0]),
            "draw_dir":    _cell_dir(tds[1]),
            "lose_dir":    _cell_dir(tds[2]),
        })

    return result


# ── 公开 API ─────────────────────────────────────────────────────────────────

def fetch_euro_odds_history(
    rid: str | int,
    mid: str | int,
    cid: str | int,
    match_year: int,
    tracker=None,
) -> int:
    """抓取并持久化某公司的欧赔变盘历史。

    Args:
        rid:        record_id，用于构建 URL（不入库）
        mid:        赛事 schedule_id
        cid:        公司 ID (115=WH, 82=Coral)
        match_year: 赛事年份，用于补全 "MM-DD HH:MM" 时间戳
        tracker:    可选 ProgressTracker，用于上报子步骤进度
    Returns: 写入行数
    """
    from contextlib import nullcontext
    from src.db import get_conn
    from src.db.repo.odds_history import upsert_wh_history, upsert_coral_history

    is_wh = int(cid) == COMPANY_WH
    company = '威廉希尔' if is_wh else '立博'
    prefix  = 'wh' if is_wh else 'coral'

    def _t(key, label):
        return tracker.task(f'{prefix}_{key}', label) if tracker else nullcontext()

    conn = get_conn()

    with _t('fetch', f'下载{company}变盘历史'):
        records = _fetch_and_parse(rid, mid, cid)

    with _t('save', f'保存{company}变盘历史 ({len(records)} 条)'):
        if is_wh:
            return upsert_wh_history(conn, int(mid), records, match_year)
        else:
            return upsert_coral_history(conn, int(mid), records, match_year)
    return 0
