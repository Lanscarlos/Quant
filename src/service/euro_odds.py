"""
欧赔快照抓取 — 1x2d.titan007.com/{mid}.js

UTF-8 编码的 JS 文件，从 game[] 数组提取各博彩公司的欧赔数据。
仅持久化威廉希尔 (115) 和立博 (82)。
"""
import re

import requests

COMPANY_WH    = 115  # William Hill 威廉希尔
COMPANY_CORAL = 82   # Ladbrokes/Coral 立博

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://1x2.titan007.com/",
}

_FIELDS = {
    0:  "company_id",
    1:  "record_id",
    2:  "company_name",
    3:  "open_win",
    4:  "open_draw",
    5:  "open_lose",
    6:  "open_win_prob",
    7:  "open_draw_prob",
    8:  "open_lose_prob",
    9:  "open_payout_rate",
    10: "cur_win",
    11: "cur_draw",
    12: "cur_lose",
    13: "cur_win_prob",
    14: "cur_draw_prob",
    15: "cur_lose_prob",
    16: "cur_payout_rate",
    17: "kelly_win",
    18: "kelly_draw",
    19: "kelly_lose",
    20: "change_time",
    21: "label",
    22: "flag1",
    23: "flag2",
    24: "hist_kelly_win",
    25: "hist_kelly_draw",
    26: "hist_kelly_lose",
}


def _safe(row: list[str], i: int) -> str:
    try:
        return row[i]
    except IndexError:
        return ""


def _fetch_and_parse(mid: str | int) -> list[dict]:
    url = f"https://1x2d.titan007.com/{mid}.js"
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    js = resp.content.decode("utf-8", errors="replace")

    m = re.search(r"var\s+game\s*=\s*Array\s*\(", js)
    if not m:
        return []

    tail = js[m.end():]
    end = tail.find(");")
    block = tail[:end] if end != -1 else tail
    entries = re.findall(r'"([^"]*)"', block)

    indices = sorted(_FIELDS)
    return [
        {_FIELDS[i]: _safe(parts, i) for i in indices}
        for entry in entries
        for parts in [entry.split("|")]
    ]


def _get_record_ids(records: list[dict]) -> dict[int, int]:
    """从解析结果中提取 {company_id: record_id}，用于变赔历史 URL。"""
    result = {}
    for r in records:
        try:
            cid = int(r.get("company_id", 0))
            rid = int(r.get("record_id", 0))
        except (TypeError, ValueError):
            continue
        if cid in (COMPANY_WH, COMPANY_CORAL) and rid:
            result[cid] = rid
    return result


def _save_to_db(conn, schedule_id: int, records: list[dict]) -> dict:
    from src.db.repo.odds import upsert_wh, upsert_coral

    result = {"wh": False, "coral": False}
    for r in records:
        try:
            cid = int(r.get("company_id", 0))
        except (TypeError, ValueError):
            continue
        if cid == COMPANY_WH:
            result["wh"] = upsert_wh(conn, schedule_id, r)
        elif cid == COMPANY_CORAL:
            result["coral"] = upsert_coral(conn, schedule_id, r)
    return result


# ── 公开 API ─────────────────────────────────────────────────────────────────

def fetch_euro_odds(schedule_id: str | int) -> dict:
    """抓取并持久化威廉/立博欧赔快照。

    Returns: {'wh': bool, 'coral': bool}
    """
    from src.db import get_conn

    conn = get_conn()
    records = _fetch_and_parse(schedule_id)
    return _save_to_db(conn, int(schedule_id), records)


def fetch_euro_odds_with_record_ids(schedule_id: str | int) -> dict[int, int]:
    """抓取并持久化欧赔快照，同时返回 {company_id: record_id}。

    返回值用于后续拉取变赔历史。
    """
    from src.db import get_conn

    conn = get_conn()
    records = _fetch_and_parse(schedule_id)
    _save_to_db(conn, int(schedule_id), records)
    return _get_record_ids(records)
