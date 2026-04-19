"""Database queries and data-fetching helpers for the conclusion page."""
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.db import get_conn
from src.service.match_detail import fetch_match_time
from src.service.euro_odds_history import fetch_euro_odds_history
from src.service.euro_odds import fetch_euro_odds

from .formatters import fmt_float, fmt_percent, parse_year

_WH_COMPANY_ID = 115   # William Hill（用于历史 URL 参数）


# ── Basic match info ───────────────────────────────────────────────────────────

def query_match(mid: int) -> dict | None:
    conn = get_conn()
    r = conn.execute("""
        SELECT m.schedule_id, m.match_time, m.status,
               m.home_score, m.away_score, m.home_half_score, m.away_half_score,
               COALESCE(sh.rank, m.home_rank) AS home_rank,
               COALESCE(sa.rank, m.away_rank) AS away_rank,
               ht.team_name_cn, at.team_name_cn,
               COALESCE(m.league_name_cn, '') AS league
        FROM matches m
        LEFT JOIN teams   ht ON m.home_team_id = ht.team_id
        LEFT JOIN teams   at ON m.away_team_id = at.team_id
        -- 优先取详情页联赛排名（ft/total），兜底用赛事列表快照
        LEFT JOIN match_standings sh
               ON sh.schedule_id = m.schedule_id
              AND sh.side = 'home' AND sh.period = 'ft' AND sh.scope = 'total'
        LEFT JOIN match_standings sa
               ON sa.schedule_id = m.schedule_id
              AND sa.side = 'away' AND sa.period = 'ft' AND sa.scope = 'total'
        WHERE m.schedule_id = ?
    """, (mid,)).fetchone()
    if not r:
        return None
    return {
        'schedule_id':     r[0],
        'match_time':      r[1],
        'status':          r[2],
        'home_score':      r[3],
        'away_score':      r[4],
        'home_half_score': r[5],
        'away_half_score': r[6],
        'home_rank':       r[7],
        'away_rank':       r[8],
        'home_team':       r[9] or '',
        'away_team':       r[10] or '',
        'league':          r[11] or '',
    }


# ── Head-to-head ───────────────────────────────────────────────────────────────

def query_h2h(mid: int) -> dict:
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
               wo.cur_win, wo.cur_draw, wo.cur_lose,
               h.home_rank, h.away_rank
        FROM match_h2h h
        LEFT JOIN odds_wh wo ON wo.schedule_id = h.match_id
        WHERE h.schedule_id = ?
        ORDER BY h.date DESC
        LIMIT 8
    """, (mid,)).fetchall()

    result_rows, win, draw, loss = [], 0, 0, 0
    for r in rows:
        home_name, away_name, home_id = r[0] or '', r[1] or '', r[2]
        home_ft, away_ft = r[3], r[4]
        home_rank, away_rank = r[8], r[9]
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
            'home_name': f"[{home_rank}] {home_name}" if home_rank else home_name,
            'away_name': f"[{away_rank}] {away_name}" if away_rank else away_name,
            'score':     score,
            'cur_odds':  f"{fmt_float(r[5])}/{fmt_float(r[6])}/{fmt_float(r[7])}",
        })
    return {'rows': result_rows, 'win': win, 'draw': draw, 'loss': loss}


# ── Recent matches (per team) ──────────────────────────────────────────────────

def query_recent_matches(mid: int) -> dict:
    conn = get_conn()
    rows = conn.execute("""
        SELECT
            mr.side, mr.match_id,
            mr.home_name, mr.away_name, mr.home_ft, mr.away_ft,
            wo.cur_win, wo.cur_draw, wo.cur_lose,
            h30.win,    h30.draw,    h30.lose,
            mr.home_rank, mr.away_rank
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
        home_name = r[2] or ''
        away_name = r[3] or ''
        home_rank, away_rank = r[12], r[13]
        result[side].append({
            'home_name': f"[{home_rank}] {home_name}" if home_rank else home_name,
            'away_name': f"[{away_rank}] {away_name}" if away_rank else away_name,
            'score':     score,
            'h30_odds':  f"{fmt_float(r[9])}/{fmt_float(r[10])}/{fmt_float(r[11])}",
            'cur_odds':  f"{fmt_float(r[6])}/{fmt_float(r[7])}/{fmt_float(r[8])}",
        })
    return result


# ── Header extras (pts, wdl) ───────────────────────────────────────────────────

def query_header_extras(mid: int) -> dict:
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

def query_odds(mid: int) -> dict:
    """Return {company_name: {'open': row, 'history': [up to 5 rows before kick-off]}}."""
    conn = get_conn()
    mt_row = conn.execute("SELECT match_time FROM matches WHERE schedule_id = ?", (mid,)).fetchone()
    match_time = mt_row[0] if mt_row else None

    result = {}
    for company, snap_tbl, hist_tbl in [
        ('William Hill', 'odds_wh',    'odds_wh_history'),
        ('Ladbrokes',    'odds_coral', 'odds_coral_history'),
        ('Bet365',       'odds_365',   'odds_365_history'),
    ]:
        snap = conn.execute(f"""
            SELECT s.open_win, s.open_draw, s.open_lose, s.open_payout_rate,
                   oh.change_time
            FROM {snap_tbl} s
            LEFT JOIN {hist_tbl} oh ON oh.schedule_id = s.schedule_id AND oh.is_opening = 1
            WHERE s.schedule_id = ?
        """, (mid,)).fetchone()
        if not snap:
            continue

        open_row = {
            'win':    fmt_float(snap[0]),
            'draw':   fmt_float(snap[1]),
            'lose':   fmt_float(snap[2]),
            'payout': fmt_percent(snap[3]),
            'time':   snap[4] or '-',
        }

        hist_rows = conn.execute(f"""
            SELECT win, draw, lose, payout_rate, change_time, win_dir, draw_dir, lose_dir
            FROM {hist_tbl}
            WHERE schedule_id = ? AND is_opening = 0
              AND (? IS NULL OR change_time < ?)
            ORDER BY change_time DESC
            LIMIT 5
        """, (mid, match_time, match_time)).fetchall()

        result[company] = {
            'open': open_row,
            'history': [{
                'win':      fmt_float(r[0]),
                'draw':     fmt_float(r[1]),
                'lose':     fmt_float(r[2]),
                'payout':   fmt_percent(r[3]),
                'time':     r[4] or '-',
                'win_dir':  r[5] or '',
                'draw_dir': r[6] or '',
                'lose_dir': r[7] or '',
            } for r in reversed(hist_rows)],
        }

    return result


# ── Asian handicap odds ────────────────────────────────────────────────────────

def query_asian_odds(mid: int) -> dict | None:
    """Return {'open': row, 'history': [up to 3 rows before kick-off]}, or None."""
    conn = get_conn()
    mt_row = conn.execute("SELECT match_time FROM matches WHERE schedule_id = ?", (mid,)).fetchone()
    match_time = mt_row[0] if mt_row else None

    snap = conn.execute("""
        SELECT a.open_handicap, a.open_home, a.open_away,
               oh.change_time
        FROM asian_odds_365 a
        LEFT JOIN asian_odds_365_history oh
            ON oh.schedule_id = a.schedule_id AND oh.is_opening = 1
        WHERE a.schedule_id = ?
    """, (mid,)).fetchone()
    if not snap:
        return None

    hist_rows = conn.execute("""
        SELECT home_odds, handicap, away_odds, change_time, home_dir, away_dir
        FROM asian_odds_365_history
        WHERE schedule_id = ? AND is_opening = 0
          AND (? IS NULL OR change_time < ?)
        ORDER BY change_time DESC
        LIMIT 3
    """, (mid, match_time, match_time)).fetchall()

    return {
        'open': {
            'hc':   snap[0] or '-',
            'home': fmt_float(snap[1]),
            'away': fmt_float(snap[2]),
            'time': snap[3] or '-',
        },
        'history': [{
            'hc':       r[1] or '-',
            'home':     fmt_float(r[0]),
            'away':     fmt_float(r[2]),
            'time':     r[3] or '-',
            'home_dir': r[4] or '',
            'away_dir': r[5] or '',
        } for r in reversed(hist_rows)],
    }


# ── Over/Under odds ───────────────────────────────────────────────────────────

def query_over_under(mid: int) -> dict | None:
    """Return {'open': row, 'history': [up to 3 rows before kick-off]}, or None."""
    conn = get_conn()
    mt_row = conn.execute("SELECT match_time FROM matches WHERE schedule_id = ?", (mid,)).fetchone()
    match_time = mt_row[0] if mt_row else None

    snap = conn.execute("""
        SELECT o.open_goals, o.open_over, o.open_under,
               oh.change_time
        FROM over_under_365 o
        LEFT JOIN over_under_365_history oh
            ON oh.schedule_id = o.schedule_id AND oh.is_opening = 1
        WHERE o.schedule_id = ?
    """, (mid,)).fetchone()
    if not snap:
        return None

    hist_rows = conn.execute("""
        SELECT over_odds, goals_line, under_odds, change_time, over_dir, under_dir
        FROM over_under_365_history
        WHERE schedule_id = ? AND is_opening = 0
          AND (? IS NULL OR change_time < ?)
        ORDER BY change_time DESC
        LIMIT 3
    """, (mid, match_time, match_time)).fetchall()

    return {
        'open': {
            'goals': snap[0] or '-',
            'over':  fmt_float(snap[1]),
            'under': fmt_float(snap[2]),
            'time':  snap[3] or '-',
        },
        'history': [{
            'goals':     r[1] or '-',
            'over':      fmt_float(r[0]),
            'under':     fmt_float(r[2]),
            'time':      r[3] or '-',
            'over_dir':  r[4] or '',
            'under_dir': r[5] or '',
        } for r in reversed(hist_rows)],
    }


# ── Aggregate all sections ─────────────────────────────────────────────────────

def query_all_sections(mid: int) -> dict:
    return {
        'extras':      query_header_extras(mid),
        'recent':      query_recent_matches(mid),
        'h2h':         query_h2h(mid),
        'odds':        query_odds(mid),
        'asian_odds':  query_asian_odds(mid),
        'over_under':  query_over_under(mid),
        'detail_fetched': get_conn().execute(
            "SELECT 1 FROM match_standings WHERE schedule_id = ? LIMIT 1", (mid,)
        ).fetchone() is not None,
    }


def query_league_table(mid: int) -> dict:
    """从 league_table_snapshot 读取赛前联赛积分榜（总/主/客场三榜）。

    Returns:
        {'total': [...], 'home': [...], 'away': [...]}
        跨联赛/杯赛赛事时三个列表均为空。
    """
    from src.db.repo.league_table import load_league_table
    conn = get_conn()
    return {
        'total': load_league_table(conn, mid, 'total'),
        'home':  load_league_table(conn, mid, 'home'),
        'away':  load_league_table(conn, mid, 'away'),
    }


def load_all_from_quant(mid: int) -> dict:
    """Load all conclusion data from quant.db into a unified data pack."""
    return {
        'match':        query_match(mid),
        'extras':       query_header_extras(mid),
        'recent':       query_recent_matches(mid),
        'h2h':          query_h2h(mid),
        'odds':         query_odds(mid),
        'asian_odds':   query_asian_odds(mid),
        'over_under':   query_over_under(mid),
        'league_table': query_league_table(mid),
    }


# ── Fetch recent match odds (background helper) ────────────────────────────────

def fetch_recent_odds(mid: int) -> None:
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
                fetch_euro_odds(match_id)
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
                    fetch_euro_odds_history(odds_row[0], match_id, _WH_COMPANY_ID, parse_year(date_str))
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
