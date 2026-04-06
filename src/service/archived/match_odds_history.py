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

Writes to odds_wh_history (company_id=115) or odds_coral_history (company_id=82).
record_id is required for the HTTP URL but is not stored in the database.
"""
import csv
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Supported companies (must match match_odds_list.py)
COMPANY_WH    = 115  # William Hill 威廉希尔
COMPANY_CORAL = 82   # Ladbrokes/Coral 立博

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


def _fetch_html(rid: str | int, mid: str | int, cid: str | int) -> str:
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


def _parse_history(html: str) -> list[dict]:
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
            "win":          _cell_text(tds[0]),
            "draw":         _cell_text(tds[1]),
            "lose":         _cell_text(tds[2]),
            "win_prob":     _cell_text(tds[3]),
            "draw_prob":    _cell_text(tds[4]),
            "lose_prob":    _cell_text(tds[5]),
            "payout_rate":  _cell_text(tds[6]),
            "kelly_win":    _cell_text(tds[7]),
            "kelly_draw":   _cell_text(tds[8]),
            "kelly_lose":   _cell_text(tds[9]),
            "change_time":  change_time,
            "is_opening":   "1" if is_opening else "0",
            "win_dir":      _cell_dir(tds[0]),
            "draw_dir":     _cell_dir(tds[1]),
            "lose_dir":     _cell_dir(tds[2]),
        }
        result.append(record)

    return result


def _fetch_and_parse(
    rid: str | int,
    mid: str | int,
    cid: str | int,
) -> list[dict]:
    """Fetch and parse odds change history for a given company + match."""
    html = _fetch_html(rid, mid, cid)
    return _parse_history(html)


def _save_to_db(
    conn,
    schedule_id: int,
    company_id: int,
    records: list[dict],
    match_year: int,
) -> int:
    """Persist odds history to the appropriate company table.

    Routes: company_id=115 → odds_wh_history, company_id=82 → odds_coral_history.
    Returns the number of rows written, or 0 for unknown companies.
    """
    from src.db.repo.odds_history import upsert_wh_history, upsert_coral_history

    if company_id == COMPANY_WH:
        return upsert_wh_history(conn, schedule_id, records, match_year)
    elif company_id == COMPANY_CORAL:
        return upsert_coral_history(conn, schedule_id, records, match_year)
    return 0


def _export_csv(data: list[dict], out_path: Path) -> None:
    """Write records to a UTF-8 CSV file (with BOM for Excel compatibility)."""
    if not data:
        return
    fieldnames = list(data[0].keys())
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)


def fetch_odds_history(
    rid: str | int,
    mid: str | int,
    cid: str | int,
    match_year: int,
) -> int:
    """Fetch, parse, and persist odds change history for a given company + match.

    Args:
        rid:        record_id — used to build the OddsHistory URL (not stored in DB).
        mid:        match schedule_id.
        cid:        company_id (115=WH, 82=Coral).
        match_year: year of the match, used to complete "MM-DD HH:MM" timestamps.
    Returns the number of rows written.
    """
    from src.db import get_conn

    conn = get_conn()
    records = _fetch_and_parse(rid, mid, cid)
    return _save_to_db(conn, int(mid), int(cid), records, match_year)


if __name__ == "__main__":
    import io, sys, datetime
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.db import get_conn, init_db
    init_db()

    target_cid = COMPANY_WH       # 115
    target_rid = "151025873"
    target_mid = "2921107"

    print(f"Fetching odds history: match={target_mid} company={target_cid} record={target_rid} ...")
    records = _fetch_and_parse(target_rid, target_mid, target_cid)
    print(f"Total changes : {len(records)}")

    if records:
        opening = next((r for r in records if r["is_opening"] == "1"), None)
        latest  = records[0]
        if opening:
            print(f"Opening W/D/L : {opening['win']} / {opening['draw']} / {opening['lose']}")
        print(f"Latest  W/D/L : {latest['win']} / {latest['draw']} / {latest['lose']}  @ {latest['change_time']}")

    conn = get_conn()
    count = _save_to_db(
        conn,
        schedule_id=int(target_mid),
        company_id=int(target_cid),
        records=records,
        match_year=datetime.date.today().year,
    )
    print(f"DB written : {count} rows")

    out = Path(__file__).parent.parent.parent / "docs" / "match_odds_history.csv"
    _export_csv(records, out)
    print(f"CSV saved  -> {out}")
