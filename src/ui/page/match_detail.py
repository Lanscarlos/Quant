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

_PERIOD_LABEL = {'ft': '全场', 'ht': '半场'}
_SCOPE_LABEL  = {'total': '总', 'home': '主', 'away': '客', 'last6': '近6'}


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


def _query_standings(mid: int) -> dict:
    """Returns nested dict: standings[side][period][scope] = {stat: value}"""
    conn = get_conn()
    rows = conn.execute("""
        SELECT side, period, scope,
               played, win, draw, loss,
               goals_for, goals_against, goal_diff,
               points, rank, win_rate
        FROM match_standings WHERE schedule_id = ?
    """, (mid,)).fetchall()
    result: dict = {}
    for r in rows:
        side, period, scope = r[0], r[1], r[2]
        result.setdefault(side, {}).setdefault(period, {})[scope] = {
            'played': r[3], 'win': r[4],  'draw': r[5], 'loss': r[6],
            'gf':     r[7], 'ga':  r[8],  'gd':   r[9],
            'points': r[10], 'rank': r[11],
            'win_rate': f"{r[12] * 100:.0f}%" if r[12] is not None else '-',
        }
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
        with ui.column().classes('w-full items-center gap-2 p-4'):
            ui.label(match['league']).classes('text-xs text-slate-400')
            with ui.row().classes('w-full items-center justify-center gap-4'):
                with ui.column().classes('items-end gap-0.5 flex-1 min-w-0'):
                    ui.label(match['home_team']) \
                        .classes('text-xl font-bold text-slate-800 text-right truncate w-full')
                    if match['home_rank']:
                        ui.label(f"第 {match['home_rank']} 名") \
                            .classes('text-xs text-slate-400')
                with ui.column().classes('items-center gap-0 flex-shrink-0'):
                    score_cls = ('text-3xl font-bold text-green-600' if is_live
                                 else 'text-3xl font-bold text-slate-700')
                    ui.label(match['score']).classes(score_cls)
                    if match['half_score']:
                        ui.label(match['half_score']).classes('text-xs text-slate-400')
                with ui.column().classes('items-start gap-0.5 flex-1 min-w-0'):
                    ui.label(match['away_team']) \
                        .classes('text-xl font-bold text-slate-800 truncate w-full')
                    if match['away_rank']:
                        ui.label(f"第 {match['away_rank']} 名") \
                            .classes('text-xs text-slate-400')
            ui.label(match['match_time']).classes('text-xs text-slate-400')


def _render_standings(standings: dict, match: dict):
    with ui.column().classes('w-full gap-2'):
        ui.label('联赛数据').classes('text-sm font-semibold text-slate-600 px-1')
        if not standings:
            _no_data_hint()
            return
        for period in ('ft', 'ht'):
            with ui.card().classes('w-full').props('flat bordered'):
                with ui.column().classes('w-full gap-2 p-3'):
                    ui.label(_PERIOD_LABEL[period]) \
                        .classes('text-xs font-semibold text-blue-600')
                    with ui.row().classes('w-full gap-3 items-start'):
                        for side, team_key in [('home', 'home_team'), ('away', 'away_team')]:
                            period_data = standings.get(side, {}).get(period, {})
                            _render_team_standings_table(match[team_key], period_data)


def _render_team_standings_table(team_name: str, period_data: dict):
    rows = []
    for scope in ('total', 'home', 'away', 'last6'):
        s = period_data.get(scope, {})
        rows.append({
            'scope':  _SCOPE_LABEL[scope],
            'played': _d(s.get('played')), 'win':  _d(s.get('win')),
            'draw':   _d(s.get('draw')),   'loss': _d(s.get('loss')),
            'gf':     _d(s.get('gf')),     'ga':   _d(s.get('ga')),
            'pts':    _d(s.get('points')), 'rank': _d(s.get('rank')),
            'wr':     s.get('win_rate', '-'),
        })
    cols = [
        {'name': 'scope', 'label': team_name, 'field': 'scope',  'align': 'left'},
        {'name': 'played','label': '赛',       'field': 'played', 'align': 'center'},
        {'name': 'win',   'label': '胜',       'field': 'win',    'align': 'center'},
        {'name': 'draw',  'label': '平',       'field': 'draw',   'align': 'center'},
        {'name': 'loss',  'label': '负',       'field': 'loss',   'align': 'center'},
        {'name': 'gf',    'label': '得',       'field': 'gf',     'align': 'center'},
        {'name': 'ga',    'label': '失',       'field': 'ga',     'align': 'center'},
        {'name': 'pts',   'label': '积分',     'field': 'pts',    'align': 'center'},
        {'name': 'rank',  'label': '排名',     'field': 'rank',   'align': 'center'},
        {'name': 'wr',    'label': '胜率',     'field': 'wr',     'align': 'center'},
    ]
    ui.table(columns=cols, rows=rows) \
        .classes('flex-1 text-xs min-w-0') \
        .props('dense flat bordered')


def _render_odds(odds_rows: list[dict]):
    with ui.column().classes('w-full gap-2'):
        ui.label('欧赔数据').classes('text-sm font-semibold text-slate-600 px-1')
        if not odds_rows:
            _no_data_hint()
            return
        cols = [
            {'name': 'company',     'label': '公司',    'field': 'company',     'align': 'left'},
            {'name': 'open_win',    'label': '初-胜',   'field': 'open_win',    'align': 'center'},
            {'name': 'open_draw',   'label': '初-平',   'field': 'open_draw',   'align': 'center'},
            {'name': 'open_lose',   'label': '初-负',   'field': 'open_lose',   'align': 'center'},
            {'name': 'open_payout', 'label': '返还率',  'field': 'open_payout', 'align': 'center'},
            {'name': 'cur_win',     'label': '即-胜',   'field': 'cur_win',     'align': 'center'},
            {'name': 'cur_draw',    'label': '即-平',   'field': 'cur_draw',    'align': 'center'},
            {'name': 'cur_lose',    'label': '即-负',   'field': 'cur_lose',    'align': 'center'},
            {'name': 'cur_payout',  'label': '返还率',  'field': 'cur_payout',  'align': 'center'},
            {'name': 'kelly_win',   'label': '凯-胜',   'field': 'kelly_win',   'align': 'center'},
            {'name': 'kelly_draw',  'label': '凯-平',   'field': 'kelly_draw',  'align': 'center'},
            {'name': 'kelly_lose',  'label': '凯-负',   'field': 'kelly_lose',  'align': 'center'},
        ]
        ui.table(columns=cols, rows=odds_rows) \
            .classes('w-full text-xs') \
            .props('dense flat bordered')


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
                standings = _query_standings(mid)
                odds_rows = _query_odds(mid)

                with ui.column().classes('w-full gap-4 p-4'):
                    _render_match_header(match)
                    _render_standings(standings, match)
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