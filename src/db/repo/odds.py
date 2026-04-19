"""
Repository: odds_wh / odds_coral

European odds snapshots for William Hill and Coral.
Strategy: INSERT OR REPLACE on schedule_id (PRIMARY KEY).
"""
import re
import sqlite3


def upsert_wh(conn: sqlite3.Connection, schedule_id: int, r: dict) -> bool:
    """Insert or replace a William Hill odds snapshot for one match."""
    return _upsert(conn, "odds_wh", schedule_id, r)


def upsert_coral(conn: sqlite3.Connection, schedule_id: int, r: dict) -> bool:
    """Insert or replace a Coral odds snapshot for one match."""
    return _upsert(conn, "odds_coral", schedule_id, r)


def upsert_365(conn: sqlite3.Connection, schedule_id: int, r: dict) -> bool:
    """Insert or replace a Bet365 European odds snapshot for one match."""
    return _upsert(conn, "odds_365", schedule_id, r)


def _upsert(conn: sqlite3.Connection, table: str, schedule_id: int, r: dict) -> bool:
    rid = None
    try:
        rid = int(r.get("record_id", 0)) or None
    except (TypeError, ValueError):
        pass
    row = (
        schedule_id,
        rid,
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
    )
    with conn:
        conn.execute(
            f"""
            INSERT OR REPLACE INTO {table} (
                schedule_id, record_id,
                open_win, open_draw, open_lose,
                open_win_prob, open_draw_prob, open_lose_prob, open_payout_rate,
                cur_win, cur_draw, cur_lose,
                cur_win_prob, cur_draw_prob, cur_lose_prob, cur_payout_rate,
                kelly_win, kelly_draw, kelly_lose,
                hist_kelly_win, hist_kelly_draw, hist_kelly_lose,
                change_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            row,
        )
    return True


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


def _float(val) -> float | None:
    try:
        v = str(val).strip()
        return float(v) if v else None
    except (TypeError, ValueError):
        return None
