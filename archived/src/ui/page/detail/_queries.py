"""Database queries and data-fetching helpers for the detail pages."""
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.db import get_conn
from src.service.archived.match_detail import fetch_match_time
from src.service.archived.match_odds_history import fetch_odds_history
from src.service.archived.match_odds_list import fetch_match_odds_list

from ._formatters import _f, _p, _parse_year

_WH_COMPANY_ID = 115   # William Hill（用于历史 URL 参数）


# ── Basic match info ───────────────────────────────────────────────────────────

def _query_match(mid: int) -> dict | None:
    conn = get_conn()
    r = conn.execute("""
        SELECT m.schedule_id, m.match_time, m.status,
               m.home_score, m.away_score, m.home_half_score, m.away_half_score,
               m.home_rank, m.away_rank,
               ht.team_name_cn, at.team_name_cn,
               COALESCE(l.league_name_cn, m.league_abbr, '') AS league
        FROM matches m
        LEFT JOIN teams ht ON m.home_team_id = ht.team_id
        LEFT JOIN teams at ON m.away_team_id = at.team_id
        LEFT JOIN leagues l  ON m.league_abbr = l.league_abbr
        WHERE m.schedule_id = ?
    """, (mid,)).fetchone()
    if not r:
        return None
    hs, as_, hhs, ahs = r[3], r[4], r[5], r[6]
    return {
        'schedule_id':     r[0],
        'match_time':      r[1],
        'status':          r[2],
        'home_score':      hs,
        'away_score':      as_,
        'home_half_score': hhs,
        'away_half_score': ahs,
        'home_rank':       r[7],
        'away_rank':       r[8],
        'home_team':       r[9] or '',
        'away_team':       r[10] or '',
        'league':          r[11] or '',
    }


# ── Head-to-head ───────────────────────────────────────────────────────────────

def _query_h2h(mid: int) -> dict:
    conn = get_conn()
    team_row = conn.execute(
        "SELECT home_team_id, away_team_id FROM matches WHERE schedule_id = ?", (mid,)
    ).fetchone()
    if not team_row:
        return {'rows': [], 'win': 0, 'draw': 0, 'loss': 0}
    h_id = team_row[0]

    rows = conn.execute("""
        SELECT h.home_name, h.away_name, h.home_id,
               h.home_ft, h.away_ft,
               wo.cur_win, wo.cur_draw, wo.cur_lose
        FROM match_h2h h
        LEFT JOIN odds_wh wo ON wo.schedule_id = h.match_id
        WHERE h.schedule_id = ?
        ORDER BY h.date DESC
        LIMIT 6
    """, (mid,)).fetchall()

    result_rows, win, draw, loss = [], 0, 0, 0
    for r in rows:
        home_name, away_name, home_id = r[0], r[1], r[2]
        home_ft, away_ft = r[3], r[4]
        side = '主' if home_id == h_id else '客'
        if home_ft is not None and away_ft is not None:
            focus_win  = (home_ft > away_ft) if home_id == h_id else (away_ft > home_ft)
            focus_loss = (home_ft < away_ft) if home_id == h_id else (away_ft < home_ft)
            if focus_win:    win  += 1
            elif focus_loss: loss += 1
            else:            draw += 1
        score = f"{home_ft}:{away_ft}" if home_ft is not None else '-'
        result_rows.append({
            'side':      side,
            'home_name': home_name or '',
            'away_name': away_name or '',
            'score':     score,
            'cur_odds':  f"{_f(r[5])}/{_f(r[6])}/{_f(r[7])}",
        })
    return {'rows': result_rows, 'win': win, 'draw': draw, 'loss': loss}


# ── Recent matches (per team) ──────────────────────────────────────────────────

def _query_recent_matches(mid: int) -> dict:
    conn = get_conn()
    rows = conn.execute("""
        SELECT
            mr.side, mr.match_id,
            mr.home_name, mr.away_name, mr.home_ft, mr.away_ft,
            wo.cur_win, wo.cur_draw, wo.cur_lose,
            h30.win,    h30.draw,    h30.lose
        FROM match_recent mr
        LEFT JOIN odds_wh wo ON wo.schedule_id = mr.match_id
        LEFT JOIN (
            SELECT oh.schedule_id, oh.win, oh.draw, oh.lose,
                   ROW_NUMBER() OVER (
                       PARTITION BY oh.schedule_id
                       ORDER BY oh.change_time DESC
                   ) AS rn
            FROM odds_wh_history oh
            LEFT JOIN matches      m   ON oh.schedule_id = m.schedule_id
            LEFT JOIN match_recent mr2 ON oh.schedule_id = mr2.match_id
                                      AND mr2.schedule_id = ?
                                      AND mr2.match_time IS NOT NULL AND mr2.match_time != ''
            WHERE oh.is_opening = 0
              AND oh.change_time <= datetime(
                      COALESCE(m.match_time, mr2.match_time),
                      '-30 minutes')
        ) h30 ON h30.schedule_id = mr.match_id AND h30.rn = 1
        WHERE mr.schedule_id = ?
        ORDER BY mr.side, mr.id
    """, (mid, mid)).fetchall()

    result: dict = {'home': [], 'away': []}
    for r in rows:
        side = r[0]
        home_ft, away_ft = r[4], r[5]
        score = f"{home_ft}:{away_ft}" if home_ft is not None else '-'
        result[side].append({
            'home_name': r[2] or '',
            'away_name': r[3] or '',
            'score':     score,
            'h30_odds':  f"{_f(r[9])}/{_f(r[10])}/{_f(r[11])}",
            'cur_odds':  f"{_f(r[6])}/{_f(r[7])}/{_f(r[8])}",
        })
    return result


# ── Header extras (pts, wdl) ───────────────────────────────────────────────────

def _query_header_extras(mid: int) -> dict:
    conn = get_conn()
    pts_rows = conn.execute("""
        SELECT side, points FROM match_standings
        WHERE schedule_id = ? AND period = 'ft' AND scope = 'total'
    """, (mid,)).fetchall()
    pts = {r[0]: r[1] for r in pts_rows}

    wdl_rows = conn.execute("""
        SELECT side,
               SUM(CASE WHEN result =  1 THEN 1 ELSE 0 END),
               SUM(CASE WHEN result =  0 THEN 1 ELSE 0 END),
               SUM(CASE WHEN result = -1 THEN 1 ELSE 0 END)
        FROM match_recent WHERE schedule_id = ?
        GROUP BY side
    """, (mid,)).fetchall()
    wdl = {r[0]: (int(r[1] or 0), int(r[2] or 0), int(r[3] or 0)) for r in wdl_rows}

    return {
        'home_pts': pts.get('home'),
        'away_pts': pts.get('away'),
        'home_wdl': wdl.get('home'),
        'away_wdl': wdl.get('away'),
    }


# ── European odds ──────────────────────────────────────────────────────────────

def _query_odds(mid: int) -> list[dict]:
    conn = get_conn()
    rows = conn.execute("""
        SELECT 'William Hill' AS company,
               open_win, open_draw, open_lose, open_payout_rate,
               cur_win, cur_draw, cur_lose, cur_payout_rate,
               kelly_win, kelly_draw, kelly_lose
        FROM odds_wh WHERE schedule_id = ?
        UNION ALL
        SELECT 'Ladbrokes' AS company,
               open_win, open_draw, open_lose, open_payout_rate,
               cur_win, cur_draw, cur_lose, cur_payout_rate,
               kelly_win, kelly_draw, kelly_lose
        FROM odds_coral WHERE schedule_id = ?
        ORDER BY company
    """, (mid, mid)).fetchall()
    return [{
        'company':     r[0],
        'open_win':    _f(r[1]),  'open_draw':  _f(r[2]),  'open_lose':  _f(r[3]),
        'open_payout': _p(r[4]),
        'cur_win':     _f(r[5]),  'cur_draw':   _f(r[6]),  'cur_lose':   _f(r[7]),
        'cur_payout':  _p(r[8]),
        'kelly_win':   _f(r[9]),  'kelly_draw': _f(r[10]), 'kelly_lose': _f(r[11]),
    } for r in rows]


# ── Asian handicap odds ────────────────────────────────────────────────────────

def _query_asian_odds(mid: int) -> dict | None:
    r = get_conn().execute("""
        SELECT open_handicap, open_home, open_away,
               cur_handicap,  cur_home,  cur_away
        FROM asian_odds_365
        WHERE schedule_id = ?
    """, (mid,)).fetchone()
    if not r:
        return None
    return {
        'open_handicap': r[0] or '-',
        'open_home':     _f(r[1]),
        'open_away':     _f(r[2]),
        'cur_handicap':  r[3] or '-',
        'cur_home':      _f(r[4]),
        'cur_away':      _f(r[5]),
    }


# ── Aggregate all sections ─────────────────────────────────────────────────────

def _query_all_sections(mid: int) -> dict:
    return {
        'extras':      _query_header_extras(mid),
        'recent':      _query_recent_matches(mid),
        'h2h':         _query_h2h(mid),
        'odds':        _query_odds(mid),
        'asian_odds':  _query_asian_odds(mid),
        'detail_fetched': get_conn().execute(
            "SELECT 1 FROM match_standings WHERE schedule_id = ? LIMIT 1", (mid,)
        ).fetchone() is not None,
    }


# ── Fetch recent match odds (background helper) ────────────────────────────────

def _fetch_recent_odds(mid: int) -> None:
    conn = get_conn()
    rows = conn.execute(
        "SELECT match_id, MAX(date), MAX(match_time) FROM match_recent WHERE schedule_id = ? GROUP BY match_id",
        (mid,)
    ).fetchall()

    def _process_one(match_id, date_str, existing_time):
        c = get_conn()
        has_odds = c.execute(
            "SELECT 1 FROM odds_wh WHERE schedule_id = ? LIMIT 1", (match_id,)
        ).fetchone()
        if not has_odds:
            try:
                fetch_match_odds_list(match_id)
            except Exception:
                return
        has_history = c.execute(
            "SELECT 1 FROM odds_wh_history WHERE schedule_id = ? LIMIT 1", (match_id,)
        ).fetchone()
        if not has_history:
            odds_row = c.execute(
                "SELECT record_id FROM odds_wh WHERE schedule_id = ?", (match_id,)
            ).fetchone()
            if odds_row and odds_row[0]:
                try:
                    fetch_odds_history(odds_row[0], match_id, _WH_COMPANY_ID, _parse_year(date_str))
                except Exception:
                    pass
        if existing_time is None:
            mt = fetch_match_time(match_id)
            with c:
                c.execute(
                    "UPDATE match_recent SET match_time = ? WHERE schedule_id = ? AND match_id = ?",
                    (mt or "", mid, match_id)
                )

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(_process_one, r[0], r[1], r[2]) for r in rows]
        for f in as_completed(futures):
            try:
                f.result()
            except Exception:
                pass
