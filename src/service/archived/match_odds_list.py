"""
Match European odds fetcher for 1x2.titan007.com

Data source: https://1x2d.titan007.com/{match_id}.js
The JS file is UTF-8 encoded. Actual odds rows are injected dynamically from this
file rather than being present in the page HTML.

Extracts from the `game` array (pipe-delimited, 27 fields per entry):
  - Company info: company_id, company_name
  - Opening odds: open_win, open_draw, open_lose + probabilities + payout_rate
  - Current odds: cur_win, cur_draw, cur_lose + probabilities + payout_rate
  - Kelly index (净胜率指数): kelly_win, kelly_draw, kelly_lose
  - Historical Kelly: hist_kelly_win, hist_kelly_draw, hist_kelly_lose
  - change_time, label
"""
import csv
import re
from pathlib import Path

import requests

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://1x2.titan007.com/",
}

# Field index → name mapping for the pipe-delimited game[] entries
_FIELDS = {
    0:  "company_id",        # 博彩公司 ID
    1:  "record_id",         # 赔率记录 ID
    2:  "company_name",      # 博彩公司名称
    3:  "open_win",          # 初始主胜赔率
    4:  "open_draw",         # 初始平局赔率
    5:  "open_lose",         # 初始客胜赔率
    6:  "open_win_prob",     # 初始主胜概率 (%)
    7:  "open_draw_prob",    # 初始平局概率 (%)
    8:  "open_lose_prob",    # 初始客胜概率 (%)
    9:  "open_payout_rate",  # 初始返还率 (%)
    10: "cur_win",           # 即时主胜赔率
    11: "cur_draw",          # 即时平局赔率
    12: "cur_lose",          # 即时客胜赔率
    13: "cur_win_prob",      # 即时主胜概率 (%)
    14: "cur_draw_prob",     # 即时平局概率 (%)
    15: "cur_lose_prob",     # 即时客胜概率 (%)
    16: "cur_payout_rate",   # 即时返还率 (%)
    17: "kelly_win",         # 凯利指数（主胜）
    18: "kelly_draw",        # 凯利指数（平局）
    19: "kelly_lose",        # 凯利指数（客胜）
    20: "change_time",       # 最近一次赔率变动时间
    21: "label",             # 联赛分类标签
    22: "flag1",             # 标志位 1（是否显示等）
    23: "flag2",             # 标志位 2
    24: "hist_kelly_win",    # 历史凯利指数（主胜）
    25: "hist_kelly_draw",   # 历史凯利指数（平局）
    26: "hist_kelly_lose",   # 历史凯利指数（客胜）
}


def _fetch_js(mid: str | int, save_dir: Path | None = None) -> str:
    url = f"https://1x2d.titan007.com/{mid}.js"
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    js = resp.content.decode("utf-8", errors="replace")
    if save_dir is not None:
        save_dir.mkdir(parents=True, exist_ok=True)
        (save_dir / f"{mid}_odds.js").write_text(js, encoding="utf-8")
    return js


def _safe(row: list[str], i: int) -> str:
    try:
        return row[i]
    except IndexError:
        return ""


def _parse_odds(js: str) -> list[dict]:
    """Parse the `game` array from the odds JS file.

    Each element is a pipe-delimited string quoted inside Array(...).
    Note: label values contain parentheses (e.g. "36*(英国)"), so we cannot
    use [^)]* to match the Array block. Instead, locate the Array start and
    extract all quoted entries directly from that position.
    """
    # Find the game Array block. Label values contain parentheses like "36*(英国)",
    # so we cannot use [^)]* to match the Array boundary. Instead, locate the
    # Array start then find the closing ");" which does not appear in any data value.
    m = re.search(r"var\s+game\s*=\s*Array\s*\(", js)
    if not m:
        return []

    tail = js[m.end():]
    # The Array ends at the first ");" (closing-quote + semicolon sequence)
    end = tail.find(");")
    block = tail[:end] if end != -1 else tail
    entries = re.findall(r'"([^"]*)"', block)

    indices = sorted(_FIELDS)
    result = []
    for entry in entries:
        parts = entry.split("|")
        record = {_FIELDS[i]: _safe(parts, i) for i in indices}
        result.append(record)

    return result


def _fetch_and_parse(mid: str | int, save_dir: Path | None = None) -> list[dict]:
    """Fetch and parse European odds for a given match ID."""
    js = _fetch_js(mid, save_dir=save_dir)
    return _parse_odds(js)


def _save_to_db(conn, schedule_id: int, records: list[dict]) -> dict:
    """Persist odds for a single match to SQLite.

    Writes in dependency order: companies → odds.
    Returns a dict with inserted/replaced counts per table.
    """
    from src.db.repo.companies import upsert_companies
    from src.db.repo.odds import upsert_odds

    return {
        "companies": upsert_companies(conn, records),
        "odds":      upsert_odds(conn, schedule_id, records),
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


def fetch_match_odds_list(schedule_id: str | int) -> dict:
    """Fetch, parse, and persist European odds for a given match to SQLite.

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

    target_id = "2921107"
    docs_dir = Path(__file__).parent.parent.parent / "docs"
    print(f"Fetching odds for match {target_id} ...")
    records = _fetch_and_parse(target_id, save_dir=docs_dir)
    print(f"Total companies : {len(records)}")

    if records:
        first = records[0]
        print(f"company_name    : {first.get('company_name')}")
        print(f"open  W/D/L     : {first.get('open_win')} / {first.get('open_draw')} / {first.get('open_lose')}")
        print(f"cur   W/D/L     : {first.get('cur_win')} / {first.get('cur_draw')} / {first.get('cur_lose')}")
        print(f"kelly W/D/L     : {first.get('kelly_win')} / {first.get('kelly_draw')} / {first.get('kelly_lose')}")

    conn = get_conn()
    counts = _save_to_db(conn, int(target_id), records)
    print(f"DB written : {counts}")

    out = Path(__file__).parent.parent.parent / "docs" / "match_odds_list.csv"
    _export_csv(records, out)
    print(f"CSV saved  -> {out}")