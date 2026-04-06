"""
Repository: match_h2h

Writes head-to-head match history rows from v_data (match detail page).
Strategy: INSERT OR REPLACE on UNIQUE(schedule_id, match_id).
"""
import sqlite3


def upsert_h2h_matches(conn: sqlite3.Connection, schedule_id: int, records: list[dict]) -> int:
    """Insert or replace H2H rows for a single match.

    `records` is the list returned by _parse_recent_matches(html, 'v_data').
    Returns the number of rows written.
    """
    if not records:
        return 0

    rows = [
        (
            schedule_id,
            _int(r.get("match_id")),
            r.get("date"),
            r.get("league"),
            _int(r.get("home_id")),
            r.get("home_name"),
            _int(r.get("away_id")),
            r.get("away_name"),
            _int(r.get("home_ft")),
            _int(r.get("away_ft")),
            r.get("ht_score"),
            r.get("handicap"),
            _int(r.get("hc_result")),
        )
        for r in records
        if r.get("match_id")
    ]

    with conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO match_h2h (
                schedule_id, match_id,
                date, league,
                home_id, home_name,
                away_id, away_name,
                home_ft, away_ft,
                ht_score, handicap, hc_result
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
    return len(rows)


def _int(val) -> int | None:
    try:
        v = str(val).strip()
        return int(v) if v else None
    except (TypeError, ValueError):
        return None
