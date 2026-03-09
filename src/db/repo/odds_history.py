"""
Repository: odds_history

Writes per-company odds change history from match_odds_history results.
Strategy: INSERT OR IGNORE on UNIQUE(record_id, change_time) — history is immutable.
"""
import sqlite3


def upsert_odds_history(
    conn: sqlite3.Connection,
    record_id: int,
    schedule_id: int,
    company_id: int,
    records: list[dict],
    match_year: int,
) -> int:
    """Insert odds history rows for a single company + match.

    Args:
        record_id:   match_odds.record_id — FK to parent row.
        schedule_id: redundantly stored for fast per-match queries.
        company_id:  redundantly stored for fast per-company filters.
        records:     raw output of match_odds_history.parse_history().
        match_year:  year of the match, used to complete change_time strings
                     which come as "MM-DD HH:MM" without a year.
    Returns the number of rows written.
    """
    rows = []
    for r in records:
        raw_time = (r.get("change_time") or "").strip()
        change_time = _complete_time(raw_time, match_year)
        if not change_time:
            continue
        rows.append((
            record_id,
            schedule_id,
            company_id,
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
            """
            INSERT OR IGNORE INTO odds_history (
                record_id, schedule_id, company_id,
                win, draw, lose,
                win_prob, draw_prob, lose_prob, payout_rate,
                kelly_win, kelly_draw, kelly_lose,
                change_time, is_opening,
                win_dir, draw_dir, lose_dir
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        v = str(val).strip()
        return float(v) if v else None
    except (TypeError, ValueError):
        return None