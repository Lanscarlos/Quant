"""
Match detail data fetcher for zq.titan007.com

Data source: https://zq.titan007.com/analysis/{match_id}sb.htm
Page is UTF-8 encoded.

Extracts from each match detail page:
  - Basic match info (from inline JS vars)
  - League standings for both teams: full-time & half-time,
    split by total / home / away / last-6 (from #porlet_5 tables)
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
    "Referer": "https://zq.titan007.com/",
}

# Ordered stat column names matching the table columns (after the row-label cell)
_STAT_COLS = ["played", "W", "D", "L", "GF", "GA", "GD", "pts", "rank", "win_rate"]
# Four data row labels inside each inner table
_ROW_LABELS = ["total", "home", "away", "last6"]


def fetch_html(match_id: str | int) -> str:
    url = f"https://zq.titan007.com/analysis/{match_id}sb.htm"
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.content.decode("utf-8", errors="replace")


# --- JS variable extractors ---

def _js_str(html: str, var: str) -> str:
    m = re.search(rf"var {var}\s*=\s*'([^']*)'", html)
    if not m:
        m = re.search(rf'var {var}\s*=\s*"([^"]*)"', html)
    return m.group(1) if m else ""


def _js_int(html: str, var: str) -> str:
    m = re.search(rf"var {var}\s*=\s*(-?\d+)", html)
    return m.group(1) if m else ""


# --- HTML table parser ---

def _parse_stats_table(table) -> dict:
    """
    Parse a single team-stats inner table.

    Table structure (rows):
      0  team header  (team name + rank, colspan=11)
      1  column header (全场/半场, 赛, 胜, 平, 负, 得, 失, 净, 积分, 排名, 胜率)
      2  总 (total)   data row
      3  主 (home)    data row
      4  客 (away)    data row
      5  近6 (last6)  data row

    Each data row: cells[0]=row label, cells[1..10]=stat values.
    """
    rows = table.find_all("tr")
    result = {}
    for i, label in enumerate(_ROW_LABELS):
        row = rows[2 + i] if (2 + i) < len(rows) else None
        cells = row.find_all("td") if row else []
        for j, col in enumerate(_STAT_COLS):
            cell = cells[j + 1] if (j + 1) < len(cells) else None
            result[f"{label}_{col}"] = cell.get_text(strip=True) if cell else ""
    return result


def parse_detail(html: str) -> dict:
    record: dict = {}

    # Basic match info from inline JS
    record["schedule_id"] = _js_int(html, "scheduleID")
    record["match_state"]  = _js_int(html, "matchState")
    record["home_team_id"] = _js_int(html, "h2h_home")
    record["away_team_id"] = _js_int(html, "h2h_away")
    record["home_team"]    = _js_str(html, "hometeam")
    record["away_team"]    = _js_str(html, "guestteam")
    record["match_time"]   = _js_str(html, "strTime")

    # League standings tables from #porlet_5
    soup = BeautifulSoup(html, "html.parser")
    porlet5 = soup.find("div", id="porlet_5")
    if not porlet5:
        return record

    outer_table = porlet5.find("table")
    if not outer_table:
        return record

    # BS4 may inject <tbody>; handle both cases
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

    return record


def save_to_db(conn, record: dict) -> int:
    """Persist standings from a single match detail record to SQLite.

    Returns the number of rows written (16 rows per match: 2 sides × 2 periods × 4 scopes).
    """
    from src.db.repo.standings import upsert_standings
    return upsert_standings(conn, record)


def export_csv(data: list[dict], out_path: Path) -> None:
    """Write records to a UTF-8 CSV (with BOM for Excel compatibility)."""
    if not data:
        return
    # Union of all keys to handle any missing fields gracefully
    fieldnames = list(data[0].keys())
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.db import get_conn, init_db
    conn = get_conn()
    init_db()

    row = conn.execute("SELECT schedule_id FROM matches LIMIT 1").fetchone()
    if not row:
        print("No matches in DB — run match_list.py first.")
        sys.exit(1)
    match_id = str(row[0])
    print(f"Fetching match detail for {match_id} ...")
    html = fetch_html(match_id)
    record = parse_detail(html)

    print(f"schedule_id : {record.get('schedule_id')}")
    print(f"home_team   : {record.get('home_team')}  (id={record.get('home_team_id')})")
    print(f"away_team   : {record.get('away_team')}  (id={record.get('away_team_id')})")
    print(f"match_time  : {record.get('match_time')}")
    print(f"home FT total rank : {record.get('home_ft_total_rank')}")
    print(f"away FT total rank : {record.get('away_ft_total_rank')}")

    count = save_to_db(conn, record)
    print(f"DB written : {count} rows")

    out = Path(__file__).parent.parent.parent / "docs" / "match_detail.csv"
    export_csv([record], out)
    print(f"CSV saved  -> {out}")