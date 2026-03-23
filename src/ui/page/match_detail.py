"""
Match detail page.

Displays league standings and European odds for a selected match.
External API:
  load(match_id) — call before navigating to this page
  render(on_back) — registered with the Router
"""
from nicegui import ui, run

from src.db import get_conn
from src.service.match_detail import fetch_match_detail
from src.service.match_odds_list import fetch_match_odds_list
from src.sync.coordinator import should_fetch_detail, should_fetch_odds

_state: dict = {'match_id': None}
_refresh_fn: list = [None]

_WH_COMPANY_ID = 115  # William Hill


def load(match_id: int | str) -> None:
    """Set current match and trigger page refresh."""
    _state['match_id'] = int(match_id)
    if _refresh_fn[0]:
        _refresh_fn[0]()


# ── DB queries ────────────────────────────────────────────────────────────────

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
        'score':           f"{hs}  :  {as_}" if hs is not None else "-  :  -",
        'half_score':      f"({hhs} : {ahs})" if hhs is not None else "",
    }


def _query_recent_matches(mid: int) -> dict:
    """Returns recent match history for home/away sides with William Hill odds.

    Joins match_recent with:
    - match_odds (company 115) for 最终赔率
    - odds_history (company 115, last entry ≤ match_time−30min) for 赛前半小时赔率
    """
    conn = get_conn()
    rows = conn.execute("""
        SELECT
            mr.side, mr.match_id,
            mr.home_name, mr.away_name, mr.home_ft, mr.away_ft,
            wo.cur_win, wo.cur_draw, wo.cur_lose,
            h30.win,    h30.draw,    h30.lose
        FROM match_recent mr
        LEFT JOIN match_odds wo
            ON wo.schedule_id = mr.match_id AND wo.company_id = ?
        LEFT JOIN (
            SELECT oh.schedule_id, oh.win, oh.draw, oh.lose,
                   ROW_NUMBER() OVER (
                       PARTITION BY oh.schedule_id
                       ORDER BY oh.change_time DESC
                   ) AS rn
            FROM odds_history oh
            LEFT JOIN matches m ON oh.schedule_id = m.schedule_id
            WHERE oh.company_id = ?
              AND oh.is_opening = 0
              AND (m.match_time IS NULL
                   OR oh.change_time <= datetime(m.match_time, '-30 minutes'))
        ) h30 ON h30.schedule_id = mr.match_id AND h30.rn = 1
        WHERE mr.schedule_id = ?
        ORDER BY mr.side, mr.id
    """, (_WH_COMPANY_ID, _WH_COMPANY_ID, mid)).fetchall()

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


_FEATURED_COMPANY_IDS = (115, 82)  # William Hill, Ladbrokes

def _query_odds(mid: int) -> list[dict]:
    conn = get_conn()
    rows = conn.execute("""
        SELECT c.company_name,
               o.open_win, o.open_draw, o.open_lose, o.open_payout_rate,
               o.cur_win, o.cur_draw, o.cur_lose, o.cur_payout_rate,
               o.kelly_win, o.kelly_draw, o.kelly_lose
        FROM match_odds o
        JOIN companies c ON o.company_id = c.company_id
        WHERE o.schedule_id = ? AND o.company_id IN (115, 82)
        ORDER BY c.company_name
    """, (mid,)).fetchall()
    return [{
        'company':     r[0],
        'open_win':    _f(r[1]),  'open_draw':  _f(r[2]),  'open_lose':  _f(r[3]),
        'open_payout': _p(r[4]),
        'cur_win':     _f(r[5]),  'cur_draw':   _f(r[6]),  'cur_lose':   _f(r[7]),
        'cur_payout':  _p(r[8]),
        'kelly_win':   _f(r[9]),  'kelly_draw': _f(r[10]), 'kelly_lose': _f(r[11]),
    } for r in rows]


def _f(v) -> str: return f"{v:.2f}" if v is not None else '-'
def _p(v) -> str: return f"{v:.1f}%" if v is not None else '-'
def _d(v) -> str: return str(v) if v is not None else '-'


# ── UI renderers ──────────────────────────────────────────────────────────────

def _render_match_header(match: dict):
    is_live = match['status'] in (1, 3)
    with ui.card().classes('w-full').props('flat bordered'):
        with ui.column().classes('w-full items-center gap-2 p-4 bg-blue-50 rounded-lg'):
            ui.label(match['league']).classes(
                'text-xs font-medium text-blue-600 bg-white px-3 py-0.5 '
                'rounded-full border border-blue-200'
            )
            with ui.row().classes('w-full items-center justify-center gap-4 mt-1'):
                with ui.column().classes('items-end gap-1 flex-1 min-w-0'):
                    ui.label(match['home_team']) \
                        .classes('text-xl font-bold text-blue-700 text-right truncate w-full')
                    if match['home_rank']:
                        ui.label(f"第 {match['home_rank']} 名") \
                            .classes('text-xs text-slate-400')
                with ui.column().classes('items-center gap-0 flex-shrink-0'):
                    score_cls = ('text-3xl font-bold text-green-600' if is_live
                                 else 'text-3xl font-bold text-slate-700')
                    ui.label(match['score']).classes(score_cls)
                    if match['half_score']:
                        ui.label(match['half_score']).classes('text-xs text-slate-400')
                with ui.column().classes('items-start gap-1 flex-1 min-w-0'):
                    ui.label(match['away_team']) \
                        .classes('text-xl font-bold text-red-600 truncate w-full')
                    if match['away_rank']:
                        ui.label(f"第 {match['away_rank']} 名") \
                            .classes('text-xs text-slate-400')
            ui.label(match['match_time']).classes('text-xs text-slate-400 mt-1')


_RECENT_COLS = [
    {'name': 'home',  'label': '主场',   'field': 'home_name', 'align': 'left'},
    {'name': 'away',  'label': '客场',   'field': 'away_name', 'align': 'left'},
    {'name': 'score', 'label': '比分',   'field': 'score',     'align': 'center'},
    {'name': 'h30',   'label': '前30分钟(胜/平/负)', 'field': 'h30_odds', 'align': 'center'},
    {'name': 'cur',   'label': '最终(胜/平/负)',     'field': 'cur_odds', 'align': 'center'},
]


def _render_recent_matches(recent: dict, match: dict):
    with ui.column().classes('w-full gap-2'):
        ui.label('联赛数据').classes('text-sm font-semibold text-slate-600 px-1')
        has_data = any(recent.get(s) for s in ('home', 'away'))
        if not has_data:
            _no_data_hint()
            return
        with ui.card().classes('w-full').props('flat bordered'):
            with ui.column().classes('w-full gap-3 p-3'):
                for side, team_key, is_home in [
                    ('home', 'home_team', True),
                    ('away', 'away_team', False),
                ]:
                    rows = recent.get(side, [])
                    color_cls   = 'text-blue-700' if is_home else 'text-red-600'
                    badge_color = 'blue' if is_home else 'red'
                    side_label  = '主' if is_home else '客'
                    with ui.column().classes('w-full gap-1'):
                        with ui.row().classes('items-center gap-1'):
                            ui.badge(side_label, color=badge_color).classes('text-xs')
                            ui.label(match[team_key]).classes(
                                f'text-sm font-bold {color_cls} truncate')
                            ui.label('近6场').classes('text-xs text-slate-400')
                        if rows:
                            ui.table(columns=_RECENT_COLS, rows=rows) \
                                .classes('w-full text-xs') \
                                .props('dense flat bordered')
                        else:
                            _no_data_hint()


_ODDS_COLS = [
    {'name': 'type',   'label': '',      'field': 'type',   'align': 'left'},
    {'name': 'win',    'label': '胜',    'field': 'win',    'align': 'center'},
    {'name': 'draw',   'label': '平',    'field': 'draw',   'align': 'center'},
    {'name': 'lose',   'label': '负',    'field': 'lose',   'align': 'center'},
    {'name': 'payout', 'label': '返还率', 'field': 'payout', 'align': 'center'},
]


def _render_odds(odds_rows: list[dict]):
    with ui.column().classes('w-full gap-2'):
        ui.label('欧赔数据').classes('text-sm font-semibold text-slate-600 px-1')
        if not odds_rows:
            _no_data_hint()
            return

        company_map = {r['company']: r for r in odds_rows}

        with ui.row().classes('w-full gap-4'):
            for company_name, label, color in [
                ('William Hill', '威廉希尔', 'blue'),
                ('Ladbrokes',    '立博',     'red'),
            ]:
                row = company_map.get(company_name)
                with ui.column().classes('flex-1 gap-1'):
                    with ui.row().classes('items-center gap-2'):
                        ui.badge(label, color=color).classes('text-xs')
                        ui.label(company_name).classes('text-xs text-slate-500')
                    if row:
                        table_rows = [
                            {'type': '初盘', 'win': row['open_win'],  'draw': row['open_draw'],
                             'lose': row['open_lose'],  'payout': row['open_payout']},
                            {'type': '即时', 'win': row['cur_win'],   'draw': row['cur_draw'],
                             'lose': row['cur_lose'],   'payout': row['cur_payout']},
                            {'type': '凯利', 'win': row['kelly_win'], 'draw': row['kelly_draw'],
                             'lose': row['kelly_lose'], 'payout': '-'},
                        ]
                        ui.table(columns=_ODDS_COLS, rows=table_rows) \
                            .classes('w-full text-xs') \
                            .props('dense flat bordered')
                    else:
                        _no_data_hint()


def _no_data_hint():
    with ui.row().classes('w-full items-center gap-2 py-3 justify-center'):
        ui.icon('info_outline').classes('text-slate-300 text-lg')
        ui.label('暂无数据，请点击「抓取数据」').classes('text-xs text-slate-400')


# ── Main render ───────────────────────────────────────────────────────────────

def render(on_back: callable = None):
    with ui.column().classes('w-full h-full gap-0'):

        # ── 顶部工具栏 ────────────────────────────────────────────────
        with ui.row().classes('w-full items-center gap-2 px-4 py-3 bg-white border-b border-slate-200'):
            back_btn = ui.button(icon='arrow_back') \
                .props('unelevated round size=sm') \
                .classes('!bg-slate-100 !text-slate-500')
            if on_back:
                back_btn.on_click(on_back)
            ui.icon('analytics').classes('text-xl text-blue-600')
            title_label = ui.label('比赛详情') \
                .classes('text-lg font-bold text-slate-700 flex-1 truncate')
            spinner   = ui.spinner(size='sm').classes('hidden')
            err_label = ui.label('').classes('text-xs text-red-500')
            fetch_btn = ui.button('抓取数据', icon='download') \
                .props('unelevated size=sm') \
                .classes('!bg-blue-600 !text-white')

        # ── 内容区域 ──────────────────────────────────────────────────
        with ui.scroll_area().classes('w-full flex-1'):

            @ui.refreshable
            def detail_content():
                mid = _state.get('match_id')
                if not mid:
                    with ui.column().classes('w-full items-center py-20 gap-3'):
                        ui.icon('sports_soccer').classes('text-5xl text-slate-300')
                        ui.label('请从赛事列表选择一场比赛').classes('text-slate-400 text-sm')
                    return

                match = _query_match(mid)
                if not match:
                    with ui.column().classes('w-full items-center py-20'):
                        ui.label('未找到比赛数据').classes('text-slate-400 text-sm')
                    return

                title_label.set_text(f"{match['home_team']}  vs  {match['away_team']}")
                recent    = _query_recent_matches(mid)
                odds_rows = _query_odds(mid)

                with ui.column().classes('w-full gap-4 p-4'):
                    _render_match_header(match)
                    ui.separator().classes('my-1')
                    _render_recent_matches(recent, match)
                    ui.separator().classes('my-1')
                    _render_odds(odds_rows)

                # Auto-fetch if data is stale
                async def _auto_fetch():
                    need_detail = should_fetch_detail(mid)
                    need_odds   = should_fetch_odds(mid)
                    if not (need_detail or need_odds):
                        return
                    spinner.classes(remove='hidden')
                    fetch_btn.disable()
                    try:
                        if need_detail:
                            await run.io_bound(fetch_match_detail, mid)
                        if need_odds:
                            await run.io_bound(fetch_match_odds_list, mid)
                        detail_content.refresh()
                    except Exception:
                        pass
                    finally:
                        spinner.classes(add='hidden')
                        fetch_btn.enable()

                ui.timer(0, _auto_fetch, once=True)

            _refresh_fn[0] = detail_content.refresh
            detail_content()

    # ── 手动抓取 ──────────────────────────────────────────────────────
    async def _on_fetch():
        mid = _state.get('match_id')
        if not mid:
            return
        err_label.set_text('')
        spinner.classes(remove='hidden')
        fetch_btn.disable()
        try:
            await run.io_bound(fetch_match_detail, mid)
            await run.io_bound(fetch_match_odds_list, mid)
            detail_content.refresh()
        except Exception as exc:
            err_label.set_text(f'抓取失败：{exc}')
        finally:
            spinner.classes(add='hidden')
            fetch_btn.enable()

    fetch_btn.on_click(_on_fetch)
