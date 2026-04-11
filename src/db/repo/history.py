"""
Repository: saved_matches / saved_snapshots (history.db)

Save, load, and list user-saved match analysis records.
"""
import json
import sqlite3

from src.db import get_conn
from src.db.history_connection import get_history_conn
from src.ui.page.conclusion.queries import (
    query_match, query_header_extras, query_recent_matches,
    query_h2h, query_odds, query_asian_odds,
)


def _fmt(v) -> str:
    return f"{v:.2f}" if v is not None else '-'


def save_match(mid: int) -> int:
    """Read all data for *mid* from quant.db, write to history.db.

    Returns the saved_matches.id. Uses INSERT OR REPLACE on schedule_id,
    so re-saving the same match overwrites.
    """
    # ── Gather data from quant.db ─────────────────────────────────────
    match = query_match(mid)
    if not match:
        raise ValueError(f"赛事 {mid} 在 quant.db 中不存在")

    extras = query_header_extras(mid)
    recent = query_recent_matches(mid)
    h2h = query_h2h(mid)
    odds = query_odds(mid)
    asian_odds = query_asian_odds(mid)

    # ── Read raw odds from quant.db for denormalized columns ──────────
    qconn = get_conn()
    wh = qconn.execute(
        "SELECT open_win, open_draw, open_lose, cur_win, cur_draw, cur_lose "
        "FROM odds_wh WHERE schedule_id = ?", (mid,)
    ).fetchone()
    wh_h30 = qconn.execute("""
        SELECT win, draw, lose FROM odds_wh_history
        WHERE schedule_id = ? AND is_opening = 0
          AND change_time <= datetime(
                (SELECT match_time FROM matches WHERE schedule_id = ?),
                '-30 minutes')
        ORDER BY change_time DESC
        LIMIT 1
    """, (mid, mid)).fetchone()
    coral = qconn.execute(
        "SELECT open_win, open_draw, open_lose, cur_win, cur_draw, cur_lose "
        "FROM odds_coral WHERE schedule_id = ?", (mid,)
    ).fetchone()
    asian = qconn.execute(
        "SELECT open_handicap, open_home, open_away, cur_handicap, cur_home, cur_away "
        "FROM asian_odds_365 WHERE schedule_id = ?", (mid,)
    ).fetchone()

    home_wdl = extras.get('home_wdl')
    away_wdl = extras.get('away_wdl')

    # ── Write to history.db ───────────────────────────────────────────
    hconn = get_history_conn()
    with hconn:
        hconn.execute("""
            INSERT OR REPLACE INTO saved_matches (
                schedule_id, match_time, home_team, away_team, league,
                home_rank, away_rank,
                home_score, away_score, home_half_score, away_half_score,
                wh_open_win, wh_open_draw, wh_open_lose,
                wh_h30_win, wh_h30_draw, wh_h30_lose,
                wh_cur_win, wh_cur_draw, wh_cur_lose,
                coral_open_win, coral_open_draw, coral_open_lose,
                coral_cur_win, coral_cur_draw, coral_cur_lose,
                asian_open_handicap, asian_open_home, asian_open_away,
                asian_cur_handicap, asian_cur_home, asian_cur_away,
                home_pts, away_pts,
                home_wdl_win, home_wdl_draw, home_wdl_loss,
                away_wdl_win, away_wdl_draw, away_wdl_loss
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?, ?
            )
        """, (
            mid, match['match_time'], match['home_team'], match['away_team'], match['league'],
            match['home_rank'], match['away_rank'],
            match['home_score'], match['away_score'], match['home_half_score'], match['away_half_score'],
            wh[0] if wh else None, wh[1] if wh else None, wh[2] if wh else None,
            wh_h30[0] if wh_h30 else None, wh_h30[1] if wh_h30 else None, wh_h30[2] if wh_h30 else None,
            wh[3] if wh else None, wh[4] if wh else None, wh[5] if wh else None,
            coral[0] if coral else None, coral[1] if coral else None, coral[2] if coral else None,
            coral[3] if coral else None, coral[4] if coral else None, coral[5] if coral else None,
            asian[0] if asian else None, asian[1] if asian else None, asian[2] if asian else None,
            asian[3] if asian else None, asian[4] if asian else None, asian[5] if asian else None,
            extras.get('home_pts'), extras.get('away_pts'),
            home_wdl[0] if home_wdl else None, home_wdl[1] if home_wdl else None, home_wdl[2] if home_wdl else None,
            away_wdl[0] if away_wdl else None, away_wdl[1] if away_wdl else None, away_wdl[2] if away_wdl else None,
        ))

        # Get the id (may be new or replaced)
        row = hconn.execute(
            "SELECT id FROM saved_matches WHERE schedule_id = ?", (mid,)
        ).fetchone()
        saved_id = row[0]

        # Snapshot JSON
        snapshot = {
            'match': match,
            'extras': extras,
            'recent': recent,
            'h2h': h2h,
            'odds': odds,
            'asian_odds': asian_odds,
        }
        hconn.execute("""
            INSERT OR REPLACE INTO saved_snapshots (
                saved_match_id, match_json, extras_json,
                recent_json, h2h_json, odds_json, asian_odds_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            saved_id,
            json.dumps(snapshot['match'], ensure_ascii=False),
            json.dumps(snapshot['extras'], ensure_ascii=False),
            json.dumps(snapshot['recent'], ensure_ascii=False),
            json.dumps(snapshot['h2h'], ensure_ascii=False),
            json.dumps(snapshot['odds'], ensure_ascii=False),
            json.dumps(snapshot['asian_odds'], ensure_ascii=False),
        ))

    return saved_id


def load_snapshot(schedule_id: int) -> dict | None:
    """Load a saved match snapshot from history.db.

    Returns a dict with the same structure as load_all_from_quant():
    {match, extras, recent, h2h, odds, asian_odds}
    """
    hconn = get_history_conn()
    row = hconn.execute("""
        SELECT s.match_json, s.extras_json, s.recent_json,
               s.h2h_json, s.odds_json, s.asian_odds_json
        FROM saved_snapshots s
        JOIN saved_matches m ON m.id = s.saved_match_id
        WHERE m.schedule_id = ?
    """, (schedule_id,)).fetchone()
    if not row:
        return None
    return {
        'match':      json.loads(row[0]) if row[0] else None,
        'extras':     json.loads(row[1]) if row[1] else {},
        'recent':     json.loads(row[2]) if row[2] else {'home': [], 'away': []},
        'h2h':        json.loads(row[3]) if row[3] else {'rows': [], 'win': 0, 'draw': 0, 'loss': 0},
        'odds':       json.loads(row[4]) if row[4] else {},
        'asian_odds': json.loads(row[5]) if row[5] else None,
    }


_ODDS_COLS = frozenset({
    'wh_open_win', 'wh_open_draw', 'wh_open_lose',
    'wh_cur_win', 'wh_cur_draw', 'wh_cur_lose',
    'coral_open_win', 'coral_open_draw', 'coral_open_lose',
    'coral_cur_win', 'coral_cur_draw', 'coral_cur_lose',
})


def backfill_h30() -> int:
    """Backfill wh_h30_* columns for existing saved_matches rows that have NULL values.

    Queries quant.db for each affected schedule_id. Silently skips matches
    whose history is no longer in quant.db. Returns the number of rows updated.
    """
    hconn = get_history_conn()
    qconn = get_conn()

    null_rows = hconn.execute(
        "SELECT id, schedule_id FROM saved_matches WHERE wh_h30_win IS NULL"
    ).fetchall()
    if not null_rows:
        return 0

    updated = 0
    for row in null_rows:
        saved_id, mid = row[0], row[1]
        h30 = qconn.execute("""
            SELECT win, draw, lose FROM odds_wh_history
            WHERE schedule_id = ? AND is_opening = 0
              AND change_time <= datetime(
                    (SELECT match_time FROM matches WHERE schedule_id = ?),
                    '-30 minutes')
            ORDER BY change_time DESC
            LIMIT 1
        """, (mid, mid)).fetchone()
        if not h30:
            continue
        with hconn:
            hconn.execute(
                "UPDATE saved_matches SET wh_h30_win=?, wh_h30_draw=?, wh_h30_lose=? WHERE id=?",
                (h30[0], h30[1], h30[2], saved_id),
            )
        updated += 1
    return updated


def list_distinct_leagues() -> list[str]:
    """Return sorted list of distinct league names in saved_matches."""
    hconn = get_history_conn()
    rows = hconn.execute(
        "SELECT DISTINCT league FROM saved_matches WHERE league IS NOT NULL ORDER BY league"
    ).fetchall()
    return [r[0] for r in rows]


def list_distinct_teams() -> list[str]:
    """Return sorted list of distinct team names (home + away combined) in saved_matches."""
    hconn = get_history_conn()
    rows = hconn.execute("""
        SELECT DISTINCT team FROM (
            SELECT home_team AS team FROM saved_matches WHERE home_team IS NOT NULL
            UNION
            SELECT away_team FROM saved_matches WHERE away_team IS NOT NULL
        ) ORDER BY team
    """).fetchall()
    return [r[0] for r in rows]


def list_saved_matches(filters: dict | None = None) -> list[dict]:
    """Query saved matches for the history list page, with optional filtering.

    Supported filter keys:
      time_from  — match_time >= value
      time_to    — match_time <= value + ' 23:59:59'
      league     — list[str], exact IN match
      team       — list[str], exact IN match on home/away (controlled by team_role)
      team_role  — 'home' | 'away' | 'both' (default 'both')
      odds_type  — column name (must be in _ODDS_COLS whitelist)
      odds_min   — odds_type column >= value
      odds_max   — odds_type column <= value
      limit      — LIMIT n
    """
    hconn = get_history_conn()

    conditions: list[str] = []
    params: list = []

    if filters:
        if 'time_from' in filters:
            conditions.append("match_time >= ?")
            params.append(filters['time_from'])
        if 'time_to' in filters:
            conditions.append("match_time <= ?")
            params.append(filters['time_to'] + ' 23:59:59')
        if 'league' in filters:
            vals = filters['league']
            ph = ','.join('?' * len(vals))
            conditions.append(f"league IN ({ph})")
            params.extend(vals)
        if 'team' in filters:
            vals = filters['team']
            ph = ','.join('?' * len(vals))
            role = filters.get('team_role', 'both')
            if role == 'home':
                conditions.append(f"home_team IN ({ph})")
                params.extend(vals)
            elif role == 'away':
                conditions.append(f"away_team IN ({ph})")
                params.extend(vals)
            else:
                conditions.append(f"(home_team IN ({ph}) OR away_team IN ({ph}))")
                params.extend(vals + vals)
        col = filters.get('odds_type')
        if col and col in _ODDS_COLS:
            if 'odds_min' in filters:
                conditions.append(f"{col} >= ?")
                params.append(filters['odds_min'])
            if 'odds_max' in filters:
                conditions.append(f"{col} <= ?")
                params.append(filters['odds_max'])

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    limit = f"LIMIT {int(filters['limit'])}" if filters and 'limit' in filters else ""

    rows = hconn.execute(f"""
        SELECT id, schedule_id, saved_at, match_time,
               home_team, away_team, league,
               wh_open_win, wh_open_draw, wh_open_lose,
               wh_h30_win, wh_h30_draw, wh_h30_lose,
               wh_cur_win, wh_cur_draw, wh_cur_lose,
               asian_cur_handicap, asian_cur_home, asian_cur_away,
               home_score, away_score, analysis_note
        FROM saved_matches
        {where}
        ORDER BY saved_at DESC
        {limit}
    """, params).fetchall()

    result = []
    for i, r in enumerate(rows, 1):
        hs, as_ = r[19], r[20]
        score = f"{hs}:{as_}" if hs is not None and as_ is not None else '-'
        asian_str = '-'
        if r[16] is not None:
            asian_str = f"{_fmt(r[17])} / {r[16]} / {_fmt(r[18])}"
        h30_str = '-'
        if r[10] is not None:
            h30_str = f"{_fmt(r[10])} / {_fmt(r[11])} / {_fmt(r[12])}"
        result.append({
            'idx':        i,
            'id':         r[1],  # schedule_id — used for row click
            'match_time': r[3] or '-',
            'home_team':  r[4] or '',
            'away_team':  r[5] or '',
            'league':     r[6] or '',
            'open_odds':  f"{_fmt(r[7])} / {_fmt(r[8])} / {_fmt(r[9])}",
            'h30_odds':   h30_str,
            'cur_odds':   f"{_fmt(r[13])} / {_fmt(r[14])} / {_fmt(r[15])}",
            'asian':      asian_str,
            'analysis':   r[21] or '',
            'score':      score,
        })
    return result
