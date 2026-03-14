"""
Repository: match_asian_odds

Writes Asian handicap odds snapshots from match_asian_handicap_list results.
Strategy: INSERT OR REPLACE on UNIQUE(schedule_id, company_id).
"""
import sqlite3


def upsert_asian_odds(conn: sqlite3.Connection, schedule_id: int, records: list[dict]) -> int:
    """Insert or replace Asian handicap odds rows for a single match.

    Each dict is the output of match_asian_handicap_list._parse_list().
    Returns the number of rows written, or 0 if the match is not yet in the DB.
    """
    # FK pre-check: match_asian_odds.schedule_id → matches.schedule_id
    if not conn.execute(
        "SELECT 1 FROM matches WHERE schedule_id = ?", (schedule_id,)
    ).fetchone():
        return 0  # caller should persist the match record first

    rows = []
    for r in records:
        cid = _int(r.get("company_id"))
        if not cid:
            continue
        rows.append((
            schedule_id,
            cid,
            r.get("open_handicap") or None,
            _float(r.get("open_home")),
            _float(r.get("open_away")),
            r.get("cur_handicap") or None,
            _float(r.get("cur_home")),
            _float(r.get("cur_away")),
        ))

    if not rows:
        return 0

    with conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO match_asian_odds (
                schedule_id, company_id,
                open_handicap, open_home, open_away,
                cur_handicap,  cur_home,  cur_away
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
    return len(rows)


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
