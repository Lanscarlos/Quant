"""
Match odds history fetcher for 1x2.titan007.com

Data source: https://1x2.titan007.com/OddsHistory.aspx?id={record_id}&sid={match_id}&cid={company_id}&l=0
Page is UTF-8 encoded. All history rows are server-side rendered — no JS loading needed.

Extracts from the odds history table inside <span id='odds'>:
  - Odds at each change: win, draw, lose
  - Implied probabilities: win_prob, draw_prob, lose_prob
  - payout_rate, kelly_win, kelly_draw, kelly_lose
  - change_time, is_opening (初盘标记)
  - change_dir: direction of each odds change (up / down / unchanged)
"""
import csv
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://1x2.titan007.com/",
}

# Font color → change direction
_COLOR_DIR = {
    "green": "up",
    "red":   "down",
}


def fetch_html(rid: str | int, mid: str | int, cid: str | int) -> str:
    url = (
        f"https://1x2.titan007.com/OddsHistory.aspx"
        f"?id={rid}&sid={mid}&cid={cid}&l=0"
    )
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.content.decode("utf-8", errors="replace")


def _cell_text(td) -> str:
    return td.get_text(strip=True)


def _cell_dir(td) -> str:
    """Return 'up' / 'down' / 'unchanged' based on font color of the first <font> tag."""
    font = td.find("font")
    if font:
        color = (font.get("color") or "").lower()
        return _COLOR_DIR.get(color, "unchanged")
    return "unchanged"


def parse_history(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    odds_span = soup.find(id="odds")
    if not odds_span:
        return []

    table = odds_span.find("table")
    if not table:
        return []

    rows = table.find_all("tr")[1:]  # skip header row
    result = []
    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 11:
            continue

        time_text = _cell_text(tds[10])
        is_opening = time_text.endswith("(初盘)")
        change_time = re.sub(r"\(初盘\)$", "", time_text).strip()

        record = {
            "win":          _cell_text(tds[0]),   # 本次变动后主胜赔率
            "draw":         _cell_text(tds[1]),   # 本次变动后平局赔率
            "lose":         _cell_text(tds[2]),   # 本次变动后客胜赔率
            "win_prob":     _cell_text(tds[3]),   # 主胜隐含概率 (%)
            "draw_prob":    _cell_text(tds[4]),   # 平局隐含概率 (%)
            "lose_prob":    _cell_text(tds[5]),   # 客胜隐含概率 (%)
            "payout_rate":  _cell_text(tds[6]),   # 返还率 (%)
            "kelly_win":    _cell_text(tds[7]),   # 凯利指数（主胜）
            "kelly_draw":   _cell_text(tds[8]),   # 凯利指数（平局）
            "kelly_lose":   _cell_text(tds[9]),   # 凯利指数（客胜）
            "change_time":  change_time,           # 赔率变动时间
            "is_opening":   "1" if is_opening else "0",  # 是否为初盘（最早一条）
            "win_dir":      _cell_dir(tds[0]),    # 主胜赔率变动方向：up/down/unchanged
            "draw_dir":     _cell_dir(tds[1]),    # 平局赔率变动方向：up/down/unchanged
            "lose_dir":     _cell_dir(tds[2]),    # 客胜赔率变动方向：up/down/unchanged
        }
        result.append(record)

    return result


def fetch_odds_history(
    rid: str | int,
    mid: str | int,
    cid: str | int,
) -> list[dict]:
    """Fetch and parse odds change history for a given company + match."""
    html = fetch_html(rid, mid, cid)
    return parse_history(html)


def save_to_db(
    conn,
    record_id: int,
    schedule_id: int,
    company_id: int,
    records: list[dict],
    match_year: int,
) -> int:
    """Persist odds history for a single company + match to SQLite.

    Args:
        record_id:   match_odds.record_id — FK to parent odds row.
        schedule_id: match schedule_id for fast per-match queries.
        company_id:  company_id for fast per-company filters.
        records:     raw output of fetch_odds_history().
        match_year:  year of the match, used to complete "MM-DD HH:MM" timestamps.
    Returns the number of rows written.
    """
    from src.db.repo.odds_history import upsert_odds_history
    return upsert_odds_history(conn, record_id, schedule_id, company_id, records, match_year)


def export_csv(data: list[dict], out_path: Path) -> None:
    """Write records to a UTF-8 CSV file (with BOM for Excel compatibility)."""
    if not data:
        return
    fieldnames = list(data[0].keys())
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    import io, sys, datetime
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.db import get_conn, init_db
    conn = get_conn()
    init_db()

    target_cid = "115"
    target_rid = "151025873"
    target_mid = "2921107"

    print(f"Fetching odds history: match={target_mid} company={target_cid} record={target_rid} ...")
    records = fetch_odds_history(target_rid, target_mid, target_cid)
    print(f"Total changes : {len(records)}")

    if records:
        opening = next((r for r in records if r["is_opening"] == "1"), None)
        latest  = records[0]
        if opening:
            print(f"Opening W/D/L : {opening['win']} / {opening['draw']} / {opening['lose']}")
        print(f"Latest  W/D/L : {latest['win']} / {latest['draw']} / {latest['lose']}  @ {latest['change_time']}")

    count = save_to_db(
        conn,
        record_id=int(target_rid),
        schedule_id=int(target_mid),
        company_id=int(target_cid),
        records=records,
        match_year=datetime.date.today().year,
    )
    print(f"DB written : {count} rows")

    out = Path(__file__).parent.parent.parent / "docs" / "match_odds_history.csv"
    export_csv(records, out)
    print(f"CSV saved  -> {out}")