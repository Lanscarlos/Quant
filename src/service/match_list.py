"""
Match list data fetcher for bf.titan007.com

Data source: https://bf.titan007.com/VbsXml/bfdata.js
The JS file is GBK-encoded. Each A[i] is a caret-delimited string.
Field mapping based on docs/data_schema.md and HTML/JS source analysis.
"""
import csv
import re
from datetime import date
from pathlib import Path

import requests

_DATA_URL = "https://bf.titan007.com/VbsXml/bfdata.js?r=007"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://bf.titan007.com/",
}

# Field indices confirmed from HTML source + empirical inspection
_FIELDS = {
    0:  "scheduleID",        # 比赛 ID
    1:  "league_color",      # 联赛颜色标识
    2:  "league_name_cn",    # 联赛名称（简体）
    3:  "league_name_tc",    # 联赛名称（繁体）
    4:  "league_abbr",       # 联赛英文缩写
    5:  "home_team_cn",      # 主队名称（简体）
    6:  "home_team_tc",      # 主队名称（繁体）
    7:  "home_team_en",      # 主队名称（英文）
    8:  "away_team_cn",      # 客队名称（简体）
    9:  "away_team_tc",      # 客队名称（繁体）
    10: "away_team_en",      # 客队名称（英文）
    11: "match_time",        # 比赛时间
    13: "status",            # 0=未开赛,1=上半场,3=下半场,-1=完场
    14: "home_score",        # 主队全场得分
    15: "away_score",        # 客队全场得分
    16: "home_half_score",   # 主队半场得分
    17: "away_half_score",   # 客队半场得分
    18: "home_red_cards",    # 主队红牌
    19: "away_red_cards",    # 客队红牌
    20: "home_yellow_cards", # 主队黄牌
    21: "away_yellow_cards", # 客队黄牌
    22: "home_rank",         # 主队联赛排名
    23: "away_rank",         # 客队联赛排名
    37: "home_team_id",      # 主队 ID
    38: "away_team_id",      # 客队 ID
    40: "country_id",        # 国家 ID
}

_STATUS_LABEL = {
    "0":   "未开赛",
    "1":   "上半场",
    "3":   "下半场",
    "-1":  "完场",
    "-11": "中断",
    "-12": "腰斩",
    "-14": "推迟",
}


def _fetch_js(url: str) -> str:
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    # titan007 serves JS files in GBK encoding (no Content-Type charset declared)
    return resp.content.decode("gbk", errors="replace")


def _parse_a_array(js: str) -> list[list[str]]:
    rows = []
    for m in re.finditer(r'A\[\d+]="([^"]+)"\.split\(', js):
        rows.append(m.group(1).split("^"))
    return rows


_HTML_TAG = re.compile(r"<[^>]+>")


def _safe(row: list[str], i: int) -> str:
    try:
        return _HTML_TAG.sub("", row[i]).strip()
    except IndexError:
        return ""


def _fetch_and_parse(url: str = _DATA_URL) -> tuple[str, list[dict]]:
    """Fetch and parse match list from bfdata.js.

    Returns (matchdate, records) where records is a list of dicts.
    """
    js = _fetch_js(url)

    md = re.search(r'var matchdate="([^"]+)"', js)
    raw_date = md.group(1) if md else ""
    if len(raw_date) == 8:
        date_prefix = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
    else:
        date_prefix = date.today().strftime("%Y-%m-%d")

    indices = sorted(_FIELDS)
    result = []
    for row in _parse_a_array(js):
        record = {_FIELDS[i]: _safe(row, i) for i in indices}
        record["status_label"] = _STATUS_LABEL.get(record["status"], record["status"])
        if date_prefix and record.get("match_time"):
            record["match_time"] = f"{date_prefix} {record['match_time']}"
        result.append(record)

    return date_str, result


def _save_to_db(conn, records: list[dict]) -> dict:
    """Persist match list records to SQLite.

    Writes in dependency order: leagues → teams → matches.
    Returns a dict with inserted/replaced counts per table.
    """
    from src.db.repo.leagues import upsert_leagues
    from src.db.repo.teams import upsert_teams
    from src.db.repo.matches import upsert_matches

    return {
        "leagues": upsert_leagues(conn, records),
        "teams":   upsert_teams(conn, records),
        "matches": upsert_matches(conn, records),
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


def fetch_match_list() -> dict:
    """Fetch, parse, and persist match list to SQLite.

    Returns a dict with inserted/replaced counts per table.
    """
    from src.db import get_conn

    conn = get_conn()
    _, records = _fetch_and_parse()
    return _save_to_db(conn, records)


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    # --- DB setup (only needed when running this file directly) ---
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.db import get_conn, init_db
    init_db()

    print(f"Fetching {_DATA_URL} ...")
    date_str, records = _fetch_and_parse()
    print(f"Match date : {date_str}")
    print(f"Total rows : {len(records)}")

    conn = get_conn()
    counts = _save_to_db(conn, records)
    print(f"DB written : {counts}")

    out = Path(__file__).parent.parent.parent / "docs" / "match_list.csv"
    _export_csv(records, out)
    print(f"CSV saved  -> {out}")