"""
Match detail data fetcher for zq.titan007.com

Data source: https://zq.titan007.com/analysis/{match_id}sb.htm
Page is UTF-8 encoded.

Extracts from each match detail page:
  - Basic match info (from inline JS vars)
  - League standings for both teams: full-time & half-time,
    split by total / home / away / last-6 (from #porlet_5 tables)
  - Recent 6 matches for both teams (from h_data / a_data JS arrays)

JS array field index mapping (h_data / a_data):
  [0]  date         YY-MM-DD
  [1]  league_id    int
  [2]  league_name  str
  [3]  color        hex color string
  [4]  home_id      int
  [5]  home_html    HTML with team name and rank
  [6]  away_id      int
  [7]  away_html    HTML with team name and rank
  [8]  home_ft      int  full-time home goals
  [9]  away_ft      int  full-time away goals
  [10] ht_score     str  half-time score "H-A"
  [11] handicap     str  Asian handicap value
  [12] result       int  1=focus-team won, 0=draw, -1=focus-team lost
                        (already flipped by the site to focus-team perspective)
  [13] hc_result    int  -2=no data, -1=loss, 0=push, 1=win (handicap)
  [14] extra        int  (reserved, typically unused -2)
  [15] match_id     int
  [16] home_rank    str
  [17] away_rank    str
  [18] league_url   str
  [19] extra_time   int  (0=normal, 1=extra/penalty)
  [20] home_corners str  (present in newer data)
  [21] away_corners str  (present in newer data)
"""
import ast
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


def _fetch_html(match_id: str | int) -> str:
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


# --- Recent matches parser (h_data / a_data JS arrays) ---

def _strip_team_html(html_str: str) -> str:
    """Strip HTML tags from team name span, returning plain text.

    Removes <span class=hp> elements (handicap markers) before extracting text.
    """
    soup = BeautifulSoup(str(html_str), "html.parser")
    for hp in soup.find_all("span", class_="hp"):
        hp.decompose()
    return soup.get_text(strip=True)


def _parse_recent_matches(html: str, data_var: str, limit: int = 6) -> list[dict]:
    """
    Parse recent match history from h_data or a_data inline JS arrays.

    Returns a list of up to *limit* most-recent matches (entries are already
    in reverse-chronological order in the source).

    Each dict contains:
      date       str   YY-MM-DD
      league     str   league name
      home_id    int   home team ID
      home_name  str   home team name (HTML stripped)
      away_id    int   away team ID
      away_name  str   away team name (HTML stripped)
      home_ft    int   full-time home goals
      away_ft    int   full-time away goals
      ft_score   str   "H-A" full-time score
      ht_score   str   "H-A" half-time score
      handicap   str   Asian handicap value
      result     int   1=focus-team won, 0=draw, -1=focus-team lost
      hc_result  int   handicap result (-2=no data, -1=loss, 0=push, 1=win)
      match_id   int
    """
    m = re.search(rf"var {data_var}\s*=\s*(\[.*?\]);", html, re.DOTALL)
    if not m:
        return []

    try:
        entries = ast.literal_eval(m.group(1))
    except (ValueError, SyntaxError):
        return []

    results = []
    for entry in entries:
        if len(entry) < 16:
            continue
        home_ft = int(entry[8]) if entry[8] != "" else 0
        away_ft = int(entry[9]) if entry[9] != "" else 0
        results.append({
            "date":      entry[0],
            "league":    entry[2],
            "home_id":   int(entry[4]),
            "home_name": _strip_team_html(entry[5]),
            "away_id":   int(entry[6]),
            "away_name": _strip_team_html(entry[7]),
            "home_ft":   home_ft,
            "away_ft":   away_ft,
            "ft_score":  f"{home_ft}-{away_ft}",
            "ht_score":  entry[10],
            "handicap":  entry[11],
            "result":    int(entry[12]),   # 1=focus won, 0=draw, -1=focus lost
            "hc_result": int(entry[13]),   # -2=no data, -1=loss, 0=push, 1=win
            "match_id":  int(entry[15]),
        })
        if len(results) >= limit:
            break

    return results


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


def _parse_detail(html: str) -> dict:
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

    # Recent 6 matches for each team from h_data / a_data JS arrays
    record["home_recent"] = _parse_recent_matches(html, "h_data")
    record["away_recent"] = _parse_recent_matches(html, "a_data")

    return record


def _save_to_db(conn, record: dict) -> int:
    """Persist standings and recent matches from a single match detail record to SQLite.

    Returns the number of rows written.
    """
    from src.db.repo.standings import upsert_standings
    from src.db.repo.recent_matches import upsert_recent_matches
    return upsert_standings(conn, record) + upsert_recent_matches(conn, record)


def _export_csv(data: list[dict], out_path: Path) -> None:
    """Write records to a UTF-8 CSV (with BOM for Excel compatibility)."""
    if not data:
        return
    # Union of all keys to handle any missing fields gracefully
    fieldnames = list(data[0].keys())
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)


def fetch_match_detail(match_id: str | int) -> int:
    """Fetch, parse, and persist standings + recent matches for a single match.

    Returns the number of rows written.
    """
    from src.db import get_conn

    conn = get_conn()
    record = _parse_detail(_fetch_html(match_id))
    return _save_to_db(conn, record)


def fetch_match_standings(match_id: str | int) -> int:
    """Fetch, parse, and persist only league standings for a single match.

    Returns the number of rows written.
    """
    from src.db import get_conn
    from src.db.repo.standings import upsert_standings

    conn = get_conn()
    record = _parse_detail(_fetch_html(match_id))
    return upsert_standings(conn, record)


def fetch_match_recent(match_id: str | int) -> int:
    """Fetch, parse, and persist only recent-match history (h_data/a_data) for a single match.

    Returns the number of rows written.
    """
    from src.db import get_conn
    from src.db.repo.recent_matches import upsert_recent_matches

    conn = get_conn()
    record = _parse_detail(_fetch_html(match_id))
    return upsert_recent_matches(conn, record)


def fetch_match_h2h(match_id: str | int) -> int:
    """Fetch, parse, and persist head-to-head history (v_data) for a single match.

    Returns the number of rows written.
    """
    from src.db import get_conn
    from src.db.repo.h2h_matches import upsert_h2h_matches

    conn = get_conn()
    html = _fetch_html(match_id)
    records = _parse_recent_matches(html, "v_data", limit=20)
    return upsert_h2h_matches(conn, int(match_id), records)


def fetch_match_time(match_id: str | int) -> str | None:
    """Fetch just the kick-off time for a match from the analysis page.

    Returns a string like "2026-03-07 20:45", or None if unavailable.
    """
    try:
        html = _fetch_html(match_id)
        return _js_str(html, "strTime") or None
    except Exception:
        return None


if __name__ == "__main__":
    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.db import get_conn, init_db
    init_db()

    conn = get_conn()
    row = conn.execute("SELECT schedule_id FROM matches LIMIT 1").fetchone()
    if not row:
        print("No matches in DB — run match_list.py first.")
        sys.exit(1)
    match_id = str(row[0])
    print(f"Fetching match detail for {match_id} ...")
    html = _fetch_html(match_id)
    record = _parse_detail(html)

    print(f"schedule_id : {record.get('schedule_id')}")
    print(f"home_team   : {record.get('home_team')}  (id={record.get('home_team_id')})")
    print(f"away_team   : {record.get('away_team')}  (id={record.get('away_team_id')})")
    print(f"match_time  : {record.get('match_time')}")
    print(f"home FT total rank : {record.get('home_ft_total_rank')}")
    print(f"away FT total rank : {record.get('away_ft_total_rank')}")

    count = _save_to_db(conn, record)
    print(f"DB written : {count} rows")

    out = Path(__file__).parent.parent.parent / "docs" / "match_detail.csv"
    _export_csv([record], out)
    print(f"CSV saved  -> {out}")