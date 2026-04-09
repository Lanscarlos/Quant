"""
Repository: asian_odds_365_history

Writes Bet365 Asian handicap odds change history.
Strategy: INSERT OR IGNORE on UNIQUE(schedule_id, change_time) — history is immutable.
"""
import sqlite3


def upsert_365_history(
    conn: sqlite3.Connection,
    schedule_id: int,
    records: list[dict],
    match_year: int,
) -> int:
    """Insert Bet365 Asian handicap history rows for one match.

    Args:
        schedule_id: match schedule_id.
        records:     raw output of match_asian_handicap_history._parse_history().
        match_year:  year of the match, used to complete "MM-DD HH:MM" timestamps.
    Returns the number of rows written.
    """
    rows = []
    for r in records:
        raw_time = (r.get("change_time") or "").strip()
        change_time = _complete_time(raw_time, match_year)
        if not change_time:
            continue
        rows.append((
            schedule_id,
            change_time,
            r.get("score") or None,
            _float(r.get("home_odds")),
            r.get("handicap") or None,
            _float(r.get("away_odds")),
            int(r.get("is_opening") or 0),
            r.get("home_dir") or None,
            r.get("away_dir") or None,
        ))

    if not rows:
        return 0

    with conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO asian_odds_365_history (
                schedule_id,
                change_time, score,
                home_odds, handicap, away_odds,
                is_opening, home_dir, away_dir
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
    return len(rows)


def _complete_time(raw: str, year: int) -> str | None:
    """Normalize "M-D HH:MM" timestamps from odds history pages to ISO format.

    Raw: "3-19 07:18"  →  "2026-03-19 07:18"
    Raw: "03-07 07:18" →  "2026-03-07 07:18"
    """
    if not raw:
        return None
    try:
        date_part, time_part = raw.strip().split()
        m, d = date_part.split("-")
        return f"{year}-{int(m):02d}-{int(d):02d} {time_part}"
    except (ValueError, AttributeError):
        return f"{year}-{raw}"


def _float(val) -> float | None:
    try:
        v = str(val).strip()
        return float(v) if v else None
    except (TypeError, ValueError):
        return None
