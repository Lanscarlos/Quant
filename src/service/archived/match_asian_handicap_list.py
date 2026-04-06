"""
Match Asian handicap odds list fetcher for vip.titan007.com

Data source: https://vip.titan007.com/AsianOdds_n.aspx?id={match_id}
Page is server-side rendered HTML (GB2312 encoded).

Each data row is identified by the presence of a link to changeDetail/handicap.aspx.
Extracts from the odds table (columns in order):
  - company_name    [td 0]
  - open_home       [td 1]  初始主队赔率
  - open_handicap   [td 2]  初始让球数
  - open_away       [td 3]  初始客队赔率
  - cur_home        [td 4]  即时主队赔率
  - cur_handicap    [td 5]  即时让球数
  - cur_away        [td 6]  即时客队赔率
  - company_id is extracted from the href of the changeDetail link in the row.

Only Bet365 (company_id=8) is persisted to asian_odds_365.
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

_DETAIL_HREF_RE = re.compile(r"changeDetail/handicap", re.IGNORECASE)
_COMPANY_ID_RE  = re.compile(r"companyID=(\d+)", re.IGNORECASE)


def _fetch_html(mid: str | int, save_dir: Path | None = None) -> str:
    url = f"https://vip.titan007.com/AsianOdds_n.aspx?id={mid}"
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    encoding = resp.encoding or "gb2312"
    if encoding.lower() in ("iso-8859-1", "windows-1252"):
        encoding = "gb2312"
    html = resp.content.decode(encoding, errors="replace")
    if save_dir is not None:
        save_dir.mkdir(parents=True, exist_ok=True)
        (save_dir / f"{mid}_asian_odds.html").write_text(html, encoding="utf-8")
    return html


def _extract_company_id(href: str) -> str:
    m = _COMPANY_ID_RE.search(href or "")
    return m.group(1) if m else ""


def _td_text(td) -> str:
    return td.get_text(strip=True) if td is not None else ""


def _parse_list(html: str) -> list[dict]:
    """Parse the Asian handicap odds table.

    HTML structure per data row (from inspection of vip.titan007.com):
      td[0]  checkbox (skipped)
      td[1]  company name (plain text + optional <span class="feng">封</span>)
      td[2]  direction indicator <span> (skipped)
      td[3]  open_home      — has title="YYYY-MM-DD HH:MM" attribute
      td[4]  open_handicap  — has title attribute + goals attribute
      td[5]  open_away      — has title attribute
      td[6]  HIDDEN last-odds home      oddstype="wholeLastOdds" display:none
      td[7]  HIDDEN last-odds handicap  oddstype="wholeLastOdds" display:none
      td[8]  HIDDEN last-odds away      oddstype="wholeLastOdds" display:none
      td[9]  cur_home       oddstype="wholeOdds"
      td[10] cur_handicap   oddstype="wholeOdds"
      td[11] cur_away       oddstype="wholeOdds"
      td[12] links (detail / stats / history)
    """
    soup = BeautifulSoup(html, "html.parser")
    result = []

    for row in soup.find_all("tr"):
        link = row.find("a", href=_DETAIL_HREF_RE)
        if not link:
            continue

        tds = row.find_all("td")
        if len(tds) < 4:
            continue

        cid = _extract_company_id(link.get("href", ""))
        if not cid:
            continue

        company_name = _td_text(tds[1]) if len(tds) > 1 else ""

        open_tds = [td for td in tds if td.get("title")]
        while len(open_tds) < 3:
            open_tds.append(None)

        cur_tds = [td for td in tds if td.get("oddstype") == "wholeOdds"]
        while len(cur_tds) < 3:
            cur_tds.append(None)

        result.append({
            "company_id":    cid,
            "company_name":  company_name,
            "open_home":     _td_text(open_tds[0]),
            "open_handicap": _td_text(open_tds[1]),
            "open_away":     _td_text(open_tds[2]),
            "cur_home":      _td_text(cur_tds[0]),
            "cur_handicap":  _td_text(cur_tds[1]),
            "cur_away":      _td_text(cur_tds[2]),
        })

    return result


def _fetch_and_parse(mid: str | int) -> list[dict]:
    """Fetch and parse Asian handicap odds list for a given match ID."""
    html = _fetch_html(mid)
    return _parse_list(html)


def _save_to_db(conn, schedule_id: int, records: list[dict]) -> bool:
    """Persist Bet365 Asian handicap snapshot for a single match to SQLite.

    Filters for company_id=8 (Bet365) and calls upsert_365.
    Returns True if the record was written, False if Bet365 was not found.
    """
    from src.db.repo.asian_odds import upsert_365

    r365 = next(
        (r for r in records if r.get("company_id") == str(COMPANY_365)),
        None,
    )
    if r365 is None:
        return False
    return upsert_365(conn, schedule_id, r365)


def _export_csv(data: list[dict], out_path: Path) -> None:
    """Write records to a UTF-8 CSV file (with BOM for Excel compatibility)."""
    if not data:
        return
    fieldnames = list(data[0].keys())
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)


def fetch_match_asian_handicap_list(schedule_id: str | int) -> bool:
    """Fetch, parse, and persist Bet365 Asian handicap odds for a given match.

    Returns True if the Bet365 record was written, False otherwise.
    """
    from src.db import get_conn

    conn = get_conn()
    records = _fetch_and_parse(schedule_id)
    return _save_to_db(conn, int(schedule_id), records)


if __name__ == "__main__":
    import io, sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.db import get_conn, init_db
    init_db()

    target_id = "2941716"
    docs_dir = Path(__file__).parent.parent.parent / "docs"
    print(f"Fetching Asian handicap odds for match {target_id} ...")
    html = _fetch_html(target_id, save_dir=docs_dir)
    records = _parse_list(html)
    print(f"Total companies parsed : {len(records)}")

    r365 = next((r for r in records if r.get("company_id") == str(COMPANY_365)), None)
    if r365:
        print(f"Bet365 open  H/HC/A : {r365.get('open_home')} / {r365.get('open_handicap')} / {r365.get('open_away')}")
        print(f"Bet365 cur   H/HC/A : {r365.get('cur_home')} / {r365.get('cur_handicap')} / {r365.get('cur_away')}")
    else:
        print("Bet365 : not found in response")

    conn = get_conn()
    match_exists = conn.execute(
        "SELECT 1 FROM matches WHERE schedule_id = ?", (int(target_id),)
    ).fetchone()
    if match_exists:
        written = _save_to_db(conn, int(target_id), records)
        print(f"DB written : {written}")
    else:
        print(f"[SKIP] Match {target_id} not in 'matches' table — DB write skipped.")
        print("       Run match_list fetch first, then retry.")

    out = Path(__file__).parent.parent.parent / "docs" / "match_asian_handicap_list.csv"
    _export_csv(records, out)
    print(f"CSV saved  -> {out}")
