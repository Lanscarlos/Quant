"""
赛事列表抓取 — bf.titan007.com/VbsXml/bfdata.js

GBK 编码的 JS 文件，每条 A[i] 是 caret(^) 分隔的字符串。
解析后写入 leagues / teams / matches 三张表。
"""
import re
from datetime import date

import requests

_DATA_URL = "https://bf.titan007.com/VbsXml/bfdata.js?r=007"
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://bf.titan007.com/",
}

_FIELDS = {
    0:  "scheduleID",
    1:  "league_color",
    2:  "league_name_cn",
    3:  "league_name_tc",
    4:  "league_abbr",
    5:  "home_team_cn",
    6:  "home_team_tc",
    7:  "home_team_en",
    8:  "away_team_cn",
    9:  "away_team_tc",
    10: "away_team_en",
    11: "match_time",
    13: "status",
    14: "home_score",
    15: "away_score",
    16: "home_half_score",
    17: "away_half_score",
    18: "home_red_cards",
    19: "away_red_cards",
    20: "home_yellow_cards",
    21: "away_yellow_cards",
    22: "home_rank",
    23: "away_rank",
    37: "home_team_id",
    38: "away_team_id",
    40: "country_id",
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

_HTML_TAG = re.compile(r"<[^>]+>")


def _safe(row: list[str], i: int) -> str:
    try:
        return _HTML_TAG.sub("", row[i]).strip()
    except IndexError:
        return ""


def _fetch_and_parse(url: str = _DATA_URL) -> tuple[str, list[dict]]:
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    js = resp.content.decode("gbk", errors="replace")

    md = re.search(r'var matchdate="([^"]+)"', js)
    raw_date = md.group(1) if md else ""
    if len(raw_date) == 8:
        date_prefix = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
    else:
        date_prefix = date.today().strftime("%Y-%m-%d")

    indices = sorted(_FIELDS)
    result = []
    for m in re.finditer(r'A\[\d+]="([^"]+)"\.split\(', js):
        row = m.group(1).split("^")
        record = {_FIELDS[i]: _safe(row, i) for i in indices}
        record["status_label"] = _STATUS_LABEL.get(record["status"], record["status"])
        if date_prefix and record.get("match_time"):
            record["match_time"] = f"{date_prefix} {record['match_time']}"
        result.append(record)

    return date_prefix, result


def fetch_match_list() -> dict:
    """抓取、解析并持久化赛事列表。

    Returns: {'leagues': int, 'teams': int, 'matches': int} 各表写入行数
    """
    from src.db import get_conn
    from src.db.repo.leagues import upsert_leagues
    from src.db.repo.teams import upsert_teams
    from src.db.repo.matches import upsert_matches

    conn = get_conn()
    _, records = _fetch_and_parse()
    return {
        "leagues": upsert_leagues(conn, records),
        "teams":   upsert_teams(conn, records),
        "matches": upsert_matches(conn, records),
    }
