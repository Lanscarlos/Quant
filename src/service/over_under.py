"""
大小球快照抓取 — vip.titan007.com/OverDown_n.aspx

GB2312 编码的 HTML 页面，服务端渲染。
从大小球赔率表格提取各公司数据，仅持久化 Bet365 (company_id=8)。
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

_DETAIL_HREF_RE = re.compile(r"changeDetail/overunder", re.IGNORECASE)
_COMPANY_ID_RE  = re.compile(r"companyID=(\d+)", re.IGNORECASE)


def _td_text(td) -> str:
    return td.get_text(strip=True) if td is not None else ""


def _fetch_and_parse(mid: str | int) -> list[dict]:
    url = f"https://vip.titan007.com/OverDown_n.aspx?id={mid}&l=0"
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

        # td 带 title 属性的三格为开盘赔率：大球/盘口/小球
        open_tds = [td for td in tds if td.get("title")]
        while len(open_tds) < 3:
            open_tds.append(None)

        # oddstype="wholeOdds" 的三格为即时赔率
        cur_tds = [td for td in tds if td.get("oddstype") == "wholeOdds"]
        while len(cur_tds) < 3:
            cur_tds.append(None)

        result.append({
            "company_id":   m.group(1),
            "company_name": company_name,
            "open_over":    _td_text(open_tds[0]),
            "open_goals":   open_tds[1].get("goals", "") if open_tds[1] else "",
            "open_under":   _td_text(open_tds[2]),
            "cur_over":     _td_text(cur_tds[0]),
            "cur_goals":    cur_tds[1].get("goals", "") if cur_tds[1] else "",
            "cur_under":    _td_text(cur_tds[2]),
        })

    return result


# ── 公开 API ─────────────────────────────────────────────────────────────────

def fetch_over_under(schedule_id: str | int, tracker=None) -> bool:
    """抓取并持久化 Bet365 大小球快照。

    Bet365 可能有多行（主盘 + 副盘），取第一行（主盘）。
    Returns: True 表示写入成功，False 表示未找到 Bet365 数据
    """
    from contextlib import nullcontext
    from src.db import get_conn
    from src.db.repo.over_under import upsert_over_under_365

    def _t(key, label):
        return tracker.task(key, label) if tracker else nullcontext()

    conn = get_conn()

    with _t('fetch', '下载大小球页面'):
        records = _fetch_and_parse(schedule_id)

    with _t('save', '保存 Bet365 大小球'):
        r365 = next(
            (r for r in records if r.get("company_id") == str(COMPANY_365)),
            None,
        )
        if r365 is None:
            return False
        return upsert_over_under_365(conn, int(schedule_id), r365)
