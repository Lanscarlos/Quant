"""
Repository: match_standings

Writes league standing rows from match_detail results.
Each match produces 16 rows: 2 sides × 2 periods × 4 scopes.
Strategy: INSERT OR REPLACE on UNIQUE(schedule_id, side, period, scope).
"""
import sqlite3

_SIDES   = ("home", "away")
_PERIODS = ("ft", "ht")
_SCOPES  = ("total", "home", "away", "last6")

# Flat-dict key suffix → DB column name
_COL_MAP = {
    "played":   "played",
    "W":        "win",
    "D":        "draw",
    "L":        "loss",
    "GF":       "goals_for",
    "GA":       "goals_against",
    "GD":       "goal_diff",
    "pts":      "points",
    "rank":     "rank",
    "win_rate": "win_rate",
}


def upsert_standings(conn: sqlite3.Connection, record: dict) -> int:
    """Insert or replace standing rows from a single match_detail record.

    `record` is the raw output of match_detail.parse_detail() — a flat dict
    with keys like "home_ft_total_W", "away_ht_last6_win_rate", etc.
    Returns the number of rows written.
    """
    schedule_id = _int(record.get("schedule_id"))
    if not schedule_id:
        return 0

    rows = []
    for side in _SIDES:
        for period in _PERIODS:
            for scope in _SCOPES:
                prefix = f"{side}_{period}_{scope}_"
                row = [schedule_id, side, period, scope]
                for src_col in _COL_MAP:
                    raw = record.get(f"{prefix}{src_col}", "")
                    if src_col == "win_rate":
                        row.append(_win_rate(raw))
                    else:
                        row.append(_int(raw))
                rows.append(tuple(row))

    with conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO match_standings (
                schedule_id, side, period, scope,
                played, win, draw, loss,
                goals_for, goals_against, goal_diff,
                points, rank, win_rate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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


def _win_rate(val) -> float | None:
    """Convert "20.0%" → 0.20, empty string → None."""
    try:
        v = str(val).strip().rstrip("%")
        return round(float(v) / 100, 6) if v else None
    except (TypeError, ValueError):
        return None