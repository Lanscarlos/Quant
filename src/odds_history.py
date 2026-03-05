import requests
from bs4 import BeautifulSoup

_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
_BASE_URL = "https://1x2.titan007.com/OddsHistory.aspx"

# 列索引（表格固定顺序：主胜/平/客胜/主%/平%/客%/返还率/凯利×3/时间）
_COL_WIN    = 0
_COL_DRAW   = 1
_COL_LOSE   = 2
_COL_RETURN = 6
_COL_TIME   = 10


def fetch_odds_history(record_id: str, match_id: str, company_id: str) -> list[dict]:
    """
    获取指定公司对某场比赛的赔率变化明细。

    参数：
        record_id  — game_df['记录ID']
        match_id   — 比赛 ID（如 2915135，从分析页 URL 中提取）
        company_id — game_df['公司ID']

    返回：list[dict]，字段为 胜/平/负/返还率/时间，与 match_view._BOOK_COLS 对应。
    """
    url = f"{_BASE_URL}?id={record_id}&sid={match_id}&cid={company_id}&l=0"
    resp = requests.get(url, headers=_HEADERS, timeout=10)
    resp.encoding = "utf-8"
    return _parse(resp.text)


def _parse(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    rows = []
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) <= _COL_TIME:
            continue
        texts = [td.get_text(strip=True) for td in tds]
        rows.append({
            '胜':   texts[_COL_WIN],
            '平':   texts[_COL_DRAW],
            '负':   texts[_COL_LOSE],
            '返还率': texts[_COL_RETURN],
            '时间':  texts[_COL_TIME],
        })
    return rows or [{'胜': '-', '平': '-', '负': '-', '返还率': '-', '时间': '-'}]