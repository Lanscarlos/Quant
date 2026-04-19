"""
Repository: odds_wh_history / odds_coral_history

European odds change history for William Hill and Coral.
Strategy: INSERT OR IGNORE on UNIQUE(schedule_id, change_time) — history is immutable.
"""
import sqlite3


def upsert_wh_history(
    conn: sqlite3.Connection,
    schedule_id: int,
    records: list[dict],
    match_year: int,
) -> int:
    """Insert William Hill odds history rows for one match."""
    return _upsert(conn, "odds_wh_history", schedule_id, records, match_year)


def upsert_coral_history(
    conn: sqlite3.Connection,
    schedule_id: int,
    records: list[dict],
    match_year: int,
) -> int:
    """Insert Coral odds history rows for one match."""
    return _upsert(conn, "odds_coral_history", schedule_id, records, match_year)


def upsert_365_history(
    conn: sqlite3.Connection,
    schedule_id: int,
    records: list[dict],
    match_year: int,
) -> int:
    """Insert Bet365 European odds history rows for one match."""
    return _upsert(conn, "odds_365_history", schedule_id, records, match_year)


def _upsert(
    conn: sqlite3.Connection,
    table: str,
    schedule_id: int,
    records: list[dict],
    match_year: int,
) -> int:
    rows = []
    for r in records:
        raw_time = (r.get("change_time") or "").strip()
        change_time = _complete_time(raw_time, match_year)
        if not change_time:
            continue
        rows.append((
            schedule_id,
            _float(r.get("win")),
            _float(r.get("draw")),
            _float(r.get("lose")),
            _float(r.get("win_prob")),
            _float(r.get("draw_prob")),
            _float(r.get("lose_prob")),
            _float(r.get("payout_rate")),
            _float(r.get("kelly_win")),
            _float(r.get("kelly_draw")),
            _float(r.get("kelly_lose")),
            change_time,
            int(r.get("is_opening") or 0),
            r.get("win_dir") or None,
            r.get("draw_dir") or None,
            r.get("lose_dir") or None,
        ))

    if not rows:
        return 0

    with conn:
        conn.executemany(
            f"""
            INSERT OR IGNORE INTO {table} (
                schedule_id,
                win, draw, lose,
                win_prob, draw_prob, lose_prob, payout_rate,
                kelly_win, kelly_draw, kelly_lose,
                change_time, is_opening,
                win_dir, draw_dir, lose_dir
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
    return len(rows)


def _complete_time(raw: str, year: int) -> str | None:
    """Prepend year to "MM-DD HH:MM" timestamps from odds history pages.

    Raw: "03-07 07:18"  →  "2026-03-07 07:18"
    """
    if not raw:
        return None
    return f"{year}-{raw}"


def _float(val) -> float | None:
    try:
        v = str(val).strip().rstrip('%')
        return float(v) if v else None
    except (TypeError, ValueError):
        return None
