"""
Repository: match_recent

Writes recent-match history rows from match_detail results.
Each match produces up to 12 rows: 2 sides × up to 6 recent matches.
Strategy: INSERT OR REPLACE on UNIQUE(schedule_id, side, match_id).
"""
import sqlite3


def upsert_recent_matches(conn: sqlite3.Connection, record: dict) -> int:
    """Insert or replace recent-match rows from a single match_detail record.

    `record` must contain 'schedule_id', 'home_recent', and 'away_recent'
    as produced by match_detail._parse_detail().
    Returns the number of rows written.
    """
    schedule_id = _int(record.get("schedule_id"))
    if not schedule_id:
        return 0

    rows = []
    for side in ("home", "away"):
        for entry in record.get(f"{side}_recent") or []:
            rows.append((
                schedule_id,
                side,
                _int(entry.get("match_id")),
                entry.get("date"),
                entry.get("league"),
                _int(entry.get("home_id")),
                entry.get("home_name"),
                _int(entry.get("away_id")),
                entry.get("away_name"),
                _int(entry.get("home_ft")),
                _int(entry.get("away_ft")),
                entry.get("ht_score"),
                entry.get("handicap"),
                _int(entry.get("result")),
                _int(entry.get("hc_result")),
            ))

    if not rows:
        return 0

    with conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO match_recent (
                schedule_id, side, match_id,
                date, league,
                home_id, home_name,
                away_id, away_name,
                home_ft, away_ft,
                ht_score, handicap,
                result, hc_result
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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