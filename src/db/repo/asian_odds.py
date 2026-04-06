"""
Repository: asian_odds_365

Writes Bet365 Asian handicap odds snapshots.
Strategy: INSERT OR REPLACE on schedule_id (PRIMARY KEY).
"""
import sqlite3


def upsert_365(conn: sqlite3.Connection, schedule_id: int, r: dict) -> bool:
    """Insert or replace a Bet365 Asian handicap snapshot for one match.

    Returns False if the match record does not exist yet (FK guard).
    """
    if not conn.execute(
        "SELECT 1 FROM matches WHERE schedule_id = ?", (schedule_id,)
    ).fetchone():
        return False  # caller should persist the match record first

    with conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO asian_odds_365 (
                schedule_id,
                open_handicap, open_home, open_away,
                cur_handicap,  cur_home,  cur_away
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                schedule_id,
                r.get("open_handicap") or None,
                _float(r.get("open_home")),
                _float(r.get("open_away")),
                r.get("cur_handicap") or None,
                _float(r.get("cur_home")),
                _float(r.get("cur_away")),
            ),
        )
    return True


def _float(val) -> float | None:
    try:
        v = str(val).strip()
        return float(v) if v else None
    except (TypeError, ValueError):
        return None
