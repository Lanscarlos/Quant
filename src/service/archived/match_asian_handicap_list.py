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
    "Referer": "https://vip.titan007.com/",
}

_DETAIL_HREF_RE = re.compile(r"changeDetail/handicap", re.IGNORECASE)
_COMPANY_ID_RE  = re.compile(r"companyID=(\d+)", re.IGNORECASE)


def _fetch_html(mid: str | int, save_dir: Path | None = None) -> str:
    url = f"https://vip.titan007.com/AsianOdds_n.aspx?id={mid}"
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    # vip.titan007.com pages are typically served as GB2312; fall back gracefully.
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

    Selectors used:
      - Opening odds  → tds with a `title` attribute (timestamp)
      - Current odds  → tds with oddstype="wholeOdds"
      - Company name  → tds[1].get_text()
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

        # Company name always in td[1]
        company_name = _td_text(tds[1]) if len(tds) > 1 else ""

        # Opening odds: the 3 tds that carry a `title` timestamp attribute
        open_tds = [td for td in tds if td.get("title")]
        while len(open_tds) < 3:
            open_tds.append(None)

        # Current odds: the 3 tds with oddstype="wholeOdds" (visible, non-hidden)
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


def _ensure_companies(conn, records: list[dict]) -> None:
    """Guarantee every company_id in records exists in the companies table.

    If company_name was not extractable from the page (empty), falls back to using
    the company_id string as a placeholder name so the FK constraint is satisfied.
    """
    rows = []
    for r in records:
        cid = r.get("company_id", "").strip()
        if not cid:
            continue
        name = r.get("company_name", "").strip() or cid  # fallback: id as name
        rows.append((int(cid), name))

    if rows:
        with conn:
            conn.executemany(
                "INSERT OR IGNORE INTO companies (company_id, company_name) VALUES (?, ?)",
                rows,
            )


def _save_to_db(conn, schedule_id: int, records: list[dict]) -> dict:
    """Persist Asian handicap odds for a single match to SQLite.

    Writes in dependency order: companies → asian_odds.
    Returns a dict with inserted/replaced counts per table.
    """
    from src.db.repo.companies import upsert_companies
    from src.db.repo.asian_odds import upsert_asian_odds

    companies_written = upsert_companies(conn, records)
    # Fallback: if company_name was not parsed, register company_id with id-as-name
    # to avoid FK constraint failures in match_asian_odds.
    _ensure_companies(conn, records)

    return {
        "companies":  companies_written,
        "asian_odds": upsert_asian_odds(conn, schedule_id, records),
    }


def _export_csv(data: list[dict], out_path: Path) -> None:
    """Write records to a UTF-8 CSV file (with BOM for Excel compatibility)."""
    if not data:
        return
    fieldnames = list(data[0].keys())
    with out_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)


def fetch_match_asian_handicap_list(schedule_id: str | int) -> dict:
    """Fetch, parse, and persist Asian handicap odds for a given match to SQLite.

    Returns a dict with inserted/replaced counts per table.
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
    # save_dir dumps raw HTML to docs/ for structure inspection if parsing fails
    html = _fetch_html(target_id, save_dir=docs_dir)
    records = _parse_list(html)
    print(f"Total companies : {len(records)}")

    if records:
        first = records[0]
        print(f"company_name    : {first.get('company_name')}")
        print(f"open  H/HC/A    : {first.get('open_home')} / {first.get('open_handicap')} / {first.get('open_away')}")
        print(f"cur   H/HC/A    : {first.get('cur_home')} / {first.get('cur_handicap')} / {first.get('cur_away')}")

    conn = get_conn()
    match_exists = conn.execute(
        "SELECT 1 FROM matches WHERE schedule_id = ?", (int(target_id),)
    ).fetchone()
    if match_exists:
        counts = _save_to_db(conn, int(target_id), records)
        print(f"DB written : {counts}")
    else:
        print(f"[SKIP] Match {target_id} not in 'matches' table — DB write skipped.")
        print("       Run match_list fetch first, then retry.")

    out = Path(__file__).parent.parent.parent / "docs" / "match_asian_handicap_list.csv"
    _export_csv(records, out)
    print(f"CSV saved  -> {out}")
