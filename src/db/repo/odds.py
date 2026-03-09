"""
Repository: match_odds

Writes European odds snapshots from match_odds_list results.
Strategy: INSERT OR REPLACE on UNIQUE(schedule_id, company_id).
"""
import re
import sqlite3


def upsert_odds(conn: sqlite3.Connection, schedule_id: int, records: list[dict]) -> int:
    """Insert or replace odds rows for a single match.

    `schedule_id` is passed explicitly — it is not present in the raw parsed records.
    Each dict is the output of match_odds_list.parse_odds().
    Returns the number of rows written.
    """
    rows = []
    for r in records:
        rid = _int(r.get("record_id"))
        cid = _int(r.get("company_id"))
        if not (rid and cid):
            continue
        rows.append((
            rid,
            schedule_id,
            cid,
            _float(r.get("open_win")),
            _float(r.get("open_draw")),
            _float(r.get("open_lose")),
            _float(r.get("open_win_prob")),
            _float(r.get("open_draw_prob")),
            _float(r.get("open_lose_prob")),
            _float(r.get("open_payout_rate")),
            _float(r.get("cur_win")),
            _float(r.get("cur_draw")),
            _float(r.get("cur_lose")),
            _float(r.get("cur_win_prob")),
            _float(r.get("cur_draw_prob")),
            _float(r.get("cur_lose_prob")),
            _float(r.get("cur_payout_rate")),
            _float(r.get("kelly_win")),
            _float(r.get("kelly_draw")),
            _float(r.get("kelly_lose")),
            _float(r.get("hist_kelly_win")),
            _float(r.get("hist_kelly_draw")),
            _float(r.get("hist_kelly_lose")),
            _parse_change_time(r.get("change_time", "")),
            _int(r.get("flag1")),
            _int(r.get("flag2")),
        ))

    if not rows:
        return 0

    with conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO match_odds (
                record_id, schedule_id, company_id,
                open_win, open_draw, open_lose,
                open_win_prob, open_draw_prob, open_lose_prob, open_payout_rate,
                cur_win, cur_draw, cur_lose,
                cur_win_prob, cur_draw_prob, cur_lose_prob, cur_payout_rate,
                kelly_win, kelly_draw, kelly_lose,
                hist_kelly_win, hist_kelly_draw, hist_kelly_lose,
                change_time, flag1, flag2
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
    return len(rows)


def _parse_change_time(raw: str) -> str | None:
    """Convert titan007 change_time to ISO format.

    Raw format: "2026,03-1,06,23,30,00"
    Parts after split on [,\\-]: year, month, flag, day, hour, minute, second
    Result: "2026-03-06 23:30:00"
    """
    if not raw:
        return None
    parts = re.split(r"[,\-]", raw)
    if len(parts) < 7:
        return raw or None
    year, month, _flag, day, hour, minute, second = parts[:7]
    try:
        return (
            f"{int(year):04d}-{int(month):02d}-{int(day):02d} "
            f"{int(hour):02d}:{int(minute):02d}:{int(second):02d}"
        )
    except ValueError:
        return raw or None


def _int(val) -> int | None:
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def _float(val) -> float | None:
    try:
        v = str(val).strip()
        return float(v) if v else None
    except (TypeError, ValueError):
        return None