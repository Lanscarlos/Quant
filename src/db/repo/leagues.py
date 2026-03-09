"""
Repository: leagues

Writes league dictionary records extracted from match_list results.
Strategy: INSERT OR IGNORE — league metadata is written once and never overwritten.
"""
import sqlite3


def upsert_leagues(conn: sqlite3.Connection, records: list[dict]) -> int:
    """Insert league rows extracted from match_list records.

    Each dict must contain: league_abbr, league_name_cn, league_color, country_id.
    Skips records with an empty league_abbr.
    Returns the number of rows inserted.
    """
    rows = []
    seen: set[str] = set()
    for r in records:
        abbr = r.get("league_abbr", "").strip()
        if not abbr or abbr in seen:
            continue
        seen.add(abbr)
        rows.append((
            abbr,
            r.get("league_name_cn") or None,
            r.get("league_color") or None,
            _int(r.get("country_id")),
        ))

    if not rows:
        return 0

    with conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO leagues (league_abbr, league_name_cn, league_color, country_id)
            VALUES (?, ?, ?, ?)
            """,
            rows,
        )
    return len(rows)


def _int(val) -> int | None:
    try:
        return int(val)
    except (TypeError, ValueError):
        return None
