"""
Match Asian handicap odds history fetcher for vip.titan007.com

Data source:
  https://vip.titan007.com/changeDetail/handicap.aspx?id={match_id}&companyID=8&l=0

Page is server-side rendered HTML (GB2312 encoded). Only Bet365 (company_id=8) is fetched.

Extracts from the history table (columns in order):
  - change_time  [td 0]  变动时间 "MM-DD HH:MM"，尾部可能带 "(初盘)"
  - score        [td 1]  变动时当前比分（如 "0-0"、"1-0"）
  - home_odds    [td 2]  主队赔率（font 颜色标记涨跌）
  - handicap     [td 3]  盘口让球数
  - away_odds    [td 4]  客队赔率（font 颜色标记涨跌）
  - status       [td 5]  "开" 表示初盘（开盘）（可选列）

Direction is derived from the font color of home_odds / away_odds cells:
  green → up, red → down, else → unchanged
"""
import csv
import re
from pathlib import Path

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

_COLOR_DIR = {
    "green": "up",
    "red":   "down",
}


def _fetch_html(mid: str | int) -> str:
    url = (
        f"https://vip.titan007.com/changeDetail/handicap.aspx"
        f"?id={mid}&companyID={COMPANY_365}&l=0"
    )
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    encoding = resp.encoding or "gb2312"
    if encoding.lower() in ("iso-8859-1", "windows-1252"):
        encoding = "gb2312"
    return resp.content.decode(encoding, errors="replace")


def _cell_text(td) -> str:
    return td.get_text(strip=True)


def _cell_dir(td) -> str:
    """Return 'up' / 'down' / 'unchanged' based on the first <font> tag color."""
    font = td.find("font")
    if font:
        color = (font.get("color") or "").lower()
        return _COLOR_DIR.get(color, "unchanged")
    return "unchanged"


def _find_history_table(soup: BeautifulSoup):
    """Find the odds history table.

    Looks for any <table> whose first data row has 5+ cells and whose 3rd cell
    (home_odds) contains a numeric value — this identifies the history table
    regardless of whether it carries an id/class attribute.
    """
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


def _parse_history(html: str) -> list[dict]:
    """Parse the Asian handicap odds change history table.

    Returns one dict per change record, newest first (as rendered by the page).
    """
    soup = BeautifulSoup(html, "html.parser")
    table = _find_history_table(soup)
    if not table:
        return []

    rows = table.find_all("tr")
    result = []
    for row in rows[1:]:  # skip header
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

        record = {
            "change_time": change_time,
            "score":       _cell_text(tds[1]),
            "home_odds":   _cell_text(tds[2]),
            "handicap":    _cell_text(tds[3]),
            "away_odds":   _cell_text(tds[4]),
            "is_opening":  "1" if is_opening else "0",
            "home_dir":    _cell_dir(tds[2]),
            "away_dir":    _cell_dir(tds[4]),
        }
        result.append(record)

    return result


def _fetch_and_parse(mid: str | int) -> list[dict]:
    """Fetch and parse Bet365 Asian handicap odds history for a given match."""
    html = _fetch_html(mid)
    return _parse_history(html)


def _save_to_db(
    conn,
    schedule_id: int,
    records: list[dict],
    match_year: int,
) -> int:
    """Persist Bet365 Asian handicap history for a single match to SQLite.

    Returns the number of rows written.
    """
    from src.db.repo.asian_odds_history import upsert_365_history
    return upsert_365_history(conn, schedule_id, records, match_year)


def _export_csv(data: list[dict], out_path: Path) -> None:
    """Write records to a UTF-8 CSV file (with BOM for Excel compatibility)."""
    if not data:
        return
    fieldnames = list(data[0].keys())
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)


def fetch_asian_handicap_history(mid: str | int, match_year: int) -> int:
    """Fetch, parse, and persist Bet365 Asian handicap history for a given match.

    Args:
        mid:        match schedule_id.
        match_year: year of the match, used to complete "MM-DD HH:MM" timestamps.
    Returns the number of rows written.
    """
    from src.db import get_conn

    conn = get_conn()
    records = _fetch_and_parse(mid)
    return _save_to_db(conn, int(mid), records, match_year)


if __name__ == "__main__":
    import io, sys, datetime
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.db import get_conn, init_db
    init_db()

    target_mid = "2941716"

    print(f"Fetching Bet365 Asian handicap history: match={target_mid} ...")
    records = _fetch_and_parse(target_mid)
    print(f"Total changes : {len(records)}")

    if records:
        opening = next((r for r in records if r["is_opening"] == "1"), None)
        latest  = records[0]
        if opening:
            print(f"Opening H/HC/A : {opening['home_odds']} / {opening['handicap']} / {opening['away_odds']}")
        print(f"Latest  H/HC/A : {latest['home_odds']} / {latest['handicap']} / {latest['away_odds']}  @ {latest['change_time']}")

    conn = get_conn()
    count = _save_to_db(
        conn,
        schedule_id=int(target_mid),
        records=records,
        match_year=datetime.date.today().year,
    )
    print(f"DB written : {count} rows")

    out = Path(__file__).parent.parent.parent / "docs" / "match_asian_handicap_history.csv"
    _export_csv(records, out)
    print(f"CSV saved  -> {out}")
