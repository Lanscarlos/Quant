"""
亚盘快照抓取 — vip.titan007.com/AsianOdds_n.aspx

GB2312 编码的 HTML 页面，服务端渲染。
从亚盘赔率表格提取各公司数据，仅持久化 Bet365 (company_id=8)。
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

_DETAIL_HREF_RE = re.compile(r"changeDetail/handicap", re.IGNORECASE)
_COMPANY_ID_RE  = re.compile(r"companyID=(\d+)", re.IGNORECASE)


def _td_text(td) -> str:
    return td.get_text(strip=True) if td is not None else ""


def _fetch_and_parse(mid: str | int) -> list[dict]:
    url = f"https://vip.titan007.com/AsianOdds_n.aspx?id={mid}"
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    encoding = resp.encoding or "gb2312"
    if encoding.lower() in ("iso-8859-1", "windows-1252"):
        encoding = "gb2312"
    html = resp.content.decode(encoding, errors="replace")

    soup = BeautifulSoup(html, "html.parser")
    result = []

    for row in soup.find_all("tr"):
        link = row.find("a", href=_DETAIL_HREF_RE)
        if not link:
            continue

        tds = row.find_all("td")
        if len(tds) < 4:
            continue

        m = _COMPANY_ID_RE.search(link.get("href", ""))
        if not m:
            continue

        company_name = _td_text(tds[1]) if len(tds) > 1 else ""

        open_tds = [td for td in tds if td.get("title")]
        while len(open_tds) < 3:
            open_tds.append(None)

        cur_tds = [td for td in tds if td.get("oddstype") == "wholeOdds"]
        while len(cur_tds) < 3:
            cur_tds.append(None)

        result.append({
            "company_id":    m.group(1),
            "company_name":  company_name,
            "open_home":     _td_text(open_tds[0]),
            "open_handicap": _td_text(open_tds[1]),
            "open_away":     _td_text(open_tds[2]),
            "cur_home":      _td_text(cur_tds[0]),
            "cur_handicap":  _td_text(cur_tds[1]),
            "cur_away":      _td_text(cur_tds[2]),
        })

    return result


# ── 公开 API ─────────────────────────────────────────────────────────────────

def fetch_asian_odds(schedule_id: str | int) -> bool:
    """抓取并持久化 Bet365 亚盘快照。

    Returns: True 表示写入成功，False 表示未找到 Bet365 数据
    """
    from src.db import get_conn
    from src.db.repo.asian_odds import upsert_365

    conn = get_conn()
    records = _fetch_and_parse(schedule_id)

    r365 = next(
        (r for r in records if r.get("company_id") == str(COMPANY_365)),
        None,
    )
    if r365 is None:
        return False
    return upsert_365(conn, int(schedule_id), r365)
