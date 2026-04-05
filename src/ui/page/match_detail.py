"""
Match detail page — refactored layout matching 赛事详情-样式图.

Layout:
  [toolbar]
  [主队 name+rank+pts] [比赛类型/时间] [pts+rank+客队 name]
  [主队近六场] | [近六场交手] | [客队近六场]
  [威廉希尔]  | [立博]       | [365亚盘]
  [分析过程 textarea]  [结论 textarea]

External API:
  load(match_id) — call before navigating to this page
  render(on_back) — registered with the Router
"""
import asyncio
import datetime

from nicegui import ui, run

from src.db import get_conn
from src.service.match_asian_handicap_list import fetch_match_asian_handicap_list
from src.service.match_detail import fetch_match_detail, fetch_match_time
from src.service.match_odds_history import fetch_odds_history
from src.service.match_odds_list import fetch_match_odds_list
from src.sync.coordinator import should_fetch_asian_odds, should_fetch_detail, should_fetch_odds

_state: dict = {'match_id': None, 'sections': None, 'auto_fetched': False, 'fetching': False}
_refresh_fn: list = [None]

_WH_COMPANY_ID   = 115  # William Hill
_BET365_COMPANY_ID = 281  # Bet365


def load(match_id: int | str) -> None:
    """Set current match and trigger page refresh."""
    _state['match_id'] = int(match_id)
    _state['sections'] = None
    _state['auto_fetched'] = False
    _state['fetching'] = False
    if _refresh_fn[0]:
        _refresh_fn[0]()


# ── DB queries ─────────────────────────────────────────────────────────────────

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


def _query_h2h(mid: int) -> dict:
    conn = get_conn()
    team_row = conn.execute(
        "SELECT home_team_id, away_team_id FROM matches WHERE schedule_id = ?", (mid,)
    ).fetchone()
    if not team_row:
        return {'rows': [], 'win': 0, 'draw': 0, 'loss': 0}
    h_id, a_id = team_row

    rows = conn.execute("""
        SELECT mr.home_name, mr.away_name, mr.home_id,
               mr.home_ft, mr.away_ft,
               wo.cur_win, wo.cur_draw, wo.cur_lose
        FROM match_recent mr
        LEFT JOIN match_odds wo ON wo.schedule_id = mr.match_id AND wo.company_id = ?
        WHERE (
            (mr.home_id = ? AND mr.away_id = ?)
            OR (mr.home_id = ? AND mr.away_id = ?)
        )
        GROUP BY mr.match_id
        ORDER BY mr.date DESC
        LIMIT 6
    """, (_WH_COMPANY_ID, h_id, a_id, a_id, h_id)).fetchall()

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


def _query_recent_matches(mid: int) -> dict:
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
            LEFT JOIN matches      m   ON oh.schedule_id = m.schedule_id
            LEFT JOIN match_recent mr2 ON oh.schedule_id = mr2.match_id
                                      AND mr2.schedule_id = ?
                                      AND mr2.match_time IS NOT NULL AND mr2.match_time != ''
            WHERE oh.company_id = ?
              AND oh.is_opening = 0
              AND oh.change_time <= datetime(
                      COALESCE(m.match_time, mr2.match_time),
                      '-30 minutes')
        ) h30 ON h30.schedule_id = mr.match_id AND h30.rn = 1
        WHERE mr.schedule_id = ?
        ORDER BY mr.side, mr.id
    """, (_WH_COMPANY_ID, mid, _WH_COMPANY_ID, mid)).fetchall()

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


def _parse_year(date_str: str | None) -> int:
    if date_str:
        try:
            return 2000 + int(str(date_str)[:2])
        except (ValueError, TypeError):
            pass
    return datetime.date.today().year


def _fetch_recent_odds(mid: int) -> None:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    conn = get_conn()
    rows = conn.execute(
        "SELECT match_id, MAX(date), MAX(match_time) FROM match_recent WHERE schedule_id = ? GROUP BY match_id",
        (mid,)
    ).fetchall()

    def _process_one(match_id, date_str, existing_time):
        c = get_conn()
        has_odds = c.execute(
            "SELECT 1 FROM match_odds WHERE schedule_id = ? LIMIT 1", (match_id,)
        ).fetchone()
        if not has_odds:
            try:
                fetch_match_odds_list(match_id)
            except Exception:
                return
        has_history = c.execute(
            "SELECT 1 FROM odds_history WHERE schedule_id = ? AND company_id = ? LIMIT 1",
            (match_id, _WH_COMPANY_ID)
        ).fetchone()
        if not has_history:
            odds_row = c.execute(
                "SELECT record_id FROM match_odds WHERE schedule_id = ? AND company_id = ?",
                (match_id, _WH_COMPANY_ID)
            ).fetchone()
            if odds_row:
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


def _query_asian_odds(mid: int) -> dict | None:
    r = get_conn().execute("""
        SELECT open_handicap, open_home, open_away,
               cur_handicap,  cur_home,  cur_away
        FROM match_asian_odds
        WHERE schedule_id = ? AND company_id = ?
    """, (mid, _BET365_COMPANY_ID)).fetchone()
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


# ── UI helpers ─────────────────────────────────────────────────────────────────

def _no_data_hint():
    with ui.row().classes('w-full items-center gap-1 py-3 justify-center'):
        ui.icon('info_outline').classes('text-slate-300 text-base')
        ui.label('暂无数据，请点击「抓取数据」').classes('text-xs text-slate-400')


def _wdl_badges(win: int, draw: int, loss: int):
    ui.label(f'胜{win}').classes('text-xs font-bold text-green-600')
    ui.label(f'平{draw}').classes('text-xs font-bold text-slate-500')
    ui.label(f'负{loss}').classes('text-xs font-bold text-red-500')


# ── Column definitions ─────────────────────────────────────────────────────────

_RECENT_COLS = [
    {'name': 'home',  'label': '主场',        'field': 'home_name', 'align': 'left'},
    {'name': 'away',  'label': '客场',        'field': 'away_name', 'align': 'left'},
    {'name': 'score', 'label': '比分',        'field': 'score',     'align': 'center'},
    {'name': 'h30',   'label': '赛前半小时赔率', 'field': 'h30_odds', 'align': 'center'},
    {'name': 'cur',   'label': '最终赔率',    'field': 'cur_odds',  'align': 'center'},
]

_H2H_COLS = [
    {'name': 'side',  'label': '主/客', 'field': 'side',      'align': 'center'},
    {'name': 'home',  'label': '主场',   'field': 'home_name', 'align': 'left'},
    {'name': 'away',  'label': '客场',   'field': 'away_name', 'align': 'left'},
    {'name': 'score', 'label': '比分',   'field': 'score',     'align': 'center'},
    {'name': 'cur',   'label': '最终赔率', 'field': 'cur_odds', 'align': 'center'},
]

_ODDS_COLS = [
    {'name': 'win',    'label': '胜',    'field': 'win',    'align': 'center'},
    {'name': 'draw',   'label': '和',    'field': 'draw',   'align': 'center'},
    {'name': 'lose',   'label': '负',    'field': 'lose',   'align': 'center'},
    {'name': 'payout', 'label': '返还率', 'field': 'payout', 'align': 'center'},
    {'name': 'time',   'label': '时间',  'field': 'time',   'align': 'center'},
]

_ASIAN_COLS = [
    {'name': 'home', 'label': '主队',   'field': 'home', 'align': 'center'},
    {'name': 'hc',   'label': '盘口',   'field': 'hc',   'align': 'center'},
    {'name': 'away', 'label': '客队',   'field': 'away', 'align': 'center'},
    {'name': 'time', 'label': '时间',   'field': 'time', 'align': 'center'},
    {'name': 'data', 'label': '对应数据', 'field': 'data', 'align': 'center'},
]


# ── Section renderers ──────────────────────────────────────────────────────────

def _render_recent_section(rows: list, wdl: tuple | None, is_home: bool, border_right: bool = True):
    color_cls  = 'text-blue-700' if is_home else 'text-red-600'
    title      = '主队近六场比赛:' if is_home else '客队近六场比赛:'
    border_cls = 'border-r border-slate-200' if border_right else ''

    with ui.column().classes(f'flex-1 {border_cls} p-2 gap-1 min-w-0'):
        with ui.row().classes('w-full items-center gap-2'):
            ui.label(title).classes(f'text-xs font-semibold {color_cls} flex-1 truncate')
            if wdl:
                _wdl_badges(*wdl)
        if rows:
            ui.table(columns=_RECENT_COLS, rows=rows).classes('w-full text-xs').props('dense flat')
        else:
            _no_data_hint()


def _render_h2h_section(h2h: dict, fetched: bool = False, border_right: bool = True):
    border_cls = 'border-r border-slate-200' if border_right else ''
    with ui.column().classes(f'flex-1 {border_cls} p-2 gap-1 min-w-0'):
        with ui.row().classes('w-full items-center gap-2'):
            ui.label('近六场交手:').classes('text-xs font-semibold text-slate-600 flex-1')
            if h2h['rows']:
                _wdl_badges(h2h['win'], h2h['draw'], h2h['loss'])
        if h2h['rows']:
            ui.table(columns=_H2H_COLS, rows=h2h['rows']).classes('w-full text-xs').props('dense flat')
        elif fetched:
            with ui.row().classes('items-center gap-1 py-3 justify-center'):
                ui.icon('info_outline').classes('text-slate-300 text-base')
                ui.label('暂无历史交手记录').classes('text-xs text-slate-400')
        else:
            _no_data_hint()


def _render_odds_section(odds_rows: list[dict], label: str, company_key: str, border_right: bool = True):
    border_cls = 'border-r border-slate-200' if border_right else ''
    with ui.column().classes(f'flex-1 {border_cls} p-2 gap-1 min-w-0'):
        ui.label(label).classes('text-xs font-semibold text-slate-600')
        row = next((r for r in odds_rows if r['company'] == company_key), None)
        if row:
            table_rows = [
                {'win': row['open_win'],  'draw': row['open_draw'],  'lose': row['open_lose'],
                 'payout': row['open_payout'],  'time': '-'},
                {'win': row['cur_win'],   'draw': row['cur_draw'],   'lose': row['cur_lose'],
                 'payout': row['cur_payout'],   'time': '-'},
                {'win': row['kelly_win'], 'draw': row['kelly_draw'], 'lose': row['kelly_lose'],
                 'payout': '-',                 'time': '-'},
            ]
            ui.table(columns=_ODDS_COLS, rows=table_rows).classes('w-full text-xs').props('dense flat')
        else:
            _no_data_hint()


def _render_asian_section(asian_row: dict | None):
    with ui.column().classes('flex-1 p-2 gap-1 min-w-0'):
        ui.label('365亚盘').classes('text-xs font-semibold text-slate-600')
        if asian_row:
            table_rows = [
                {'home': asian_row['open_home'], 'hc': asian_row['open_handicap'],
                 'away': asian_row['open_away'], 'time': '-', 'data': '-'},
                {'home': asian_row['cur_home'],  'hc': asian_row['cur_handicap'],
                 'away': asian_row['cur_away'],  'time': '-', 'data': '-'},
            ]
            ui.table(columns=_ASIAN_COLS, rows=table_rows).classes('w-full text-xs').props('dense flat')
        else:
            _no_data_hint()


def _render_skeleton_3col():
    _W = 'animation="wave"'
    with ui.row().classes('w-full gap-0 items-start'):
        for i in range(3):
            border_cls = 'border-r border-slate-200' if i < 2 else ''
            with ui.column().classes(f'flex-1 {border_cls} p-2 gap-1'):
                ui.skeleton('text').classes('w-24').props(_W)
                for _ in range(6):
                    ui.skeleton('text').classes('w-full').props(_W)


# ── Main render ────────────────────────────────────────────────────────────────

def render(on_back: callable = None):
    with ui.column().classes('w-full h-full gap-0'):

        # ── 顶部工具栏 ────────────────────────────────────────────────
        with ui.row().classes(
            'w-full items-center gap-1 px-3 py-2 bg-white border-b border-slate-200 flex-wrap'
        ):
            back_btn = ui.button(icon='arrow_back') \
                .props('unelevated round size=xs') \
                .classes('!bg-slate-100 !text-slate-500 mr-1')
            if on_back:
                back_btn.on_click(on_back)

            fetch_btn_1      = ui.button('抓取数据1',    icon='download')    .props('outline size=sm')
            fetch_btn_2      = ui.button('抓取数据2',    icon='bar_chart')   .props('outline size=sm')
            init_btn         = ui.button('数据分析初始',  icon='restart_alt') .props('outline size=sm')
            save_btn         = ui.button('结果保存',     icon='save')         .props('outline size=sm')
            history_load_btn = ui.button('历史数据加载',  icon='history')     .props('outline size=sm')
            history_page_btn = ui.button('历史数据页面',  icon='table_chart') .props('outline size=sm')
            export_img_btn   = ui.button('另存为图片',   icon='image')        .props('outline size=sm')
            print_btn        = ui.button('分析结果打印',  icon='print')       .props('outline size=sm')
            exit_btn         = ui.button('退出',         icon='exit_to_app')  .props('outline size=sm')

            spinner   = ui.spinner(size='sm').classes('hidden ml-2')
            err_label = ui.label('').classes('text-xs text-red-500')

        def _disable_fetch():
            for b in (fetch_btn_1, fetch_btn_2, history_load_btn):
                b.disable()

        def _enable_fetch():
            for b in (fetch_btn_1, fetch_btn_2, history_load_btn):
                b.enable()

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

                sections = _state.get('sections')
                extras   = sections['extras'] if sections else {}
                recent   = sections['recent'] if sections else {}
                h2h      = sections['h2h']    if sections else {'rows': [], 'win': 0, 'draw': 0, 'loss': 0}
                odds     = sections['odds']   if sections else []

                with ui.column().classes('w-full gap-0 p-3'):

                    # ── 行1: 赛事头部 ──────────────────────────────────
                    with ui.row().classes('w-full items-center'):
                        # 主队：队名 flex-1 撑满，排名/积分钉在右侧
                        with ui.row().classes('flex-[2] items-center min-w-0'):
                            with ui.row().classes('flex-1 items-center gap-2 min-w-0'):
                                ui.label('主队').classes('text-xs text-slate-400 flex-shrink-0')
                                ui.label(match['home_team']).classes(
                                    'text-xl font-bold text-blue-700 truncate min-w-0'
                                )
                            with ui.row().classes('items-center gap-3 flex-shrink-0 pl-4'):
                                with ui.row().classes('items-center gap-1'):
                                    ui.label('排名').classes('text-xs text-slate-400')
                                    ui.label(_d(match['home_rank'])).classes('text-xs font-bold text-slate-700')
                                with ui.row().classes('items-center gap-1'):
                                    ui.label('积分').classes('text-xs text-slate-400')
                                    ui.label(_d(extras.get('home_pts'))).classes('text-xs font-bold text-slate-700')

                        # 中间：比赛类型 + 比赛时间（固定宽不参与 flex 拉伸）
                        with ui.row().classes('items-center gap-2 flex-shrink-0 px-6'):
                            ui.label('比赛类型:').classes('text-xs text-slate-500 whitespace-nowrap')
                            ui.label(match['league']).classes('text-xs font-medium text-slate-700 whitespace-nowrap')
                            ui.label('比赛时间:').classes('text-xs text-slate-500 whitespace-nowrap ml-3')
                            ui.label(match['match_time'] or '').classes(
                                'text-xs text-slate-600 whitespace-nowrap'
                            )

                        # 客队（镜像）：积分/排名钉在左侧，队名 flex-1 撑满靠右
                        with ui.row().classes('flex-[2] items-center min-w-0'):
                            with ui.row().classes('items-center gap-3 flex-shrink-0 pr-4'):
                                with ui.row().classes('items-center gap-1'):
                                    ui.label('积分').classes('text-xs text-slate-400')
                                    ui.label(_d(extras.get('away_pts'))).classes('text-xs font-bold text-slate-700')
                                with ui.row().classes('items-center gap-1'):
                                    ui.label('排名').classes('text-xs text-slate-400')
                                    ui.label(_d(match['away_rank'])).classes('text-xs font-bold text-slate-700')
                            with ui.row().classes('flex-1 items-center gap-2 min-w-0 justify-end'):
                                ui.label(match['away_team']).classes(
                                    'text-xl font-bold text-red-600 truncate min-w-0 text-right'
                                )
                                ui.label('客队').classes('text-xs text-slate-400 flex-shrink-0')

                    ui.separator().classes('my-2')

                    # ── 行2: 近六场比赛 + 交手 ─────────────────────────
                    with ui.row().classes('w-full gap-0 items-start border border-slate-200 rounded'):
                        if sections:
                            _render_recent_section(
                                recent.get('home', []), extras.get('home_wdl'),
                                is_home=True, border_right=True
                            )
                            _render_h2h_section(h2h, sections['detail_fetched'], border_right=True)
                            _render_recent_section(
                                recent.get('away', []), extras.get('away_wdl'),
                                is_home=False, border_right=False
                            )
                        else:
                            _render_skeleton_3col()

                    ui.separator().classes('my-2')

                    # ── 行3: 欧赔 + 亚盘 ──────────────────────────────
                    with ui.row().classes('w-full gap-0 items-start border border-slate-200 rounded'):
                        _render_odds_section(odds, '威廉希尔', 'William Hill', border_right=True)
                        _render_odds_section(odds, '立博',     'Ladbrokes',    border_right=True)
                        _render_asian_section(sections['asian_odds'] if sections else None)

                    ui.separator().classes('my-2')

                    # ── 行4: 分析过程 + 结论 ───────────────────────────
                    with ui.row().classes('w-full gap-3'):
                        with ui.column().classes('flex-[3] gap-1'):
                            ui.label('分析过程').classes('text-sm font-semibold text-slate-600')
                            ui.textarea().classes('w-full').props('outlined dense rows=5')
                        with ui.column().classes('flex-[2] gap-1'):
                            ui.label('结论').classes('text-sm font-semibold text-slate-600')
                            ui.textarea().classes('w-full').props('outlined dense rows=5')

                # ── 自动加载逻辑 ──────────────────────────────────────
                if not sections and not _state.get('fetching'):
                    async def _load_sections():
                        data = await run.io_bound(_query_all_sections, mid)
                        _state['sections'] = data
                        detail_content.refresh()
                    ui.timer(0, _load_sections, once=True)

                elif not _state.get('auto_fetched'):
                    async def _auto_fetch():
                        status = match['status']
                        need_detail = should_fetch_detail(mid, status=status)
                        need_odds   = should_fetch_odds(mid, status=status)
                        need_asian  = should_fetch_asian_odds(mid, status=status)
                        if not (need_detail or need_odds or need_asian):
                            _state['auto_fetched'] = True
                            return
                        spinner.classes(remove='hidden')
                        _disable_fetch()
                        _state['fetching'] = True
                        _state['sections'] = None
                        detail_content.refresh()
                        try:
                            coros = []
                            if need_detail:
                                coros.append(run.io_bound(fetch_match_detail, mid))
                            if need_odds:
                                coros.append(run.io_bound(fetch_match_odds_list, mid))
                            if need_asian:
                                coros.append(run.io_bound(fetch_match_asian_handicap_list, mid))
                            if coros:
                                await asyncio.gather(*coros)
                            await run.io_bound(_fetch_recent_odds, mid)
                            _state['auto_fetched'] = True
                            _state['sections'] = await run.io_bound(_query_all_sections, mid)
                            detail_content.refresh()
                        except Exception:
                            _state['auto_fetched'] = True
                            _state['sections'] = await run.io_bound(_query_all_sections, mid)
                            detail_content.refresh()
                        finally:
                            _state['fetching'] = False
                            spinner.classes(add='hidden')
                            _enable_fetch()

                    ui.timer(0, _auto_fetch, once=True)

            _refresh_fn[0] = detail_content.refresh
            detail_content()

    # ── 按钮操作处理 ──────────────────────────────────────────────────

    async def _run_fetch(coro_factories: list, label: str = '抓取'):
        mid = _state.get('match_id')
        if not mid:
            return
        err_label.set_text('')
        spinner.classes(remove='hidden')
        _disable_fetch()
        prev_sections = _state['sections']
        _state['fetching'] = True
        _state['sections'] = None
        detail_content.refresh()
        try:
            if len(coro_factories) > 1:
                await asyncio.gather(*[f() for f in coro_factories])
            else:
                await coro_factories[0]()
            _state['sections'] = await run.io_bound(_query_all_sections, mid)
            detail_content.refresh()
        except Exception as exc:
            err_label.set_text(f'{label}失败：{exc}')
            _state['sections'] = prev_sections
            detail_content.refresh()
        finally:
            _state['fetching'] = False
            spinner.classes(add='hidden')
            _enable_fetch()

    async def _on_fetch_detail():
        mid = _state.get('match_id')
        if mid:
            await _run_fetch([lambda: run.io_bound(fetch_match_detail, mid)], '抓取数据1')

    async def _on_fetch_odds():
        mid = _state.get('match_id')
        if mid:
            await _run_fetch([lambda: run.io_bound(fetch_match_odds_list, mid)], '抓取数据2')

    def _on_init():
        _state['sections'] = None
        _state['auto_fetched'] = False
        _state['fetching'] = False
        err_label.set_text('')
        detail_content.refresh()

    async def _on_load_history():
        mid = _state.get('match_id')
        if mid:
            await _run_fetch([lambda: run.io_bound(_fetch_recent_odds, mid)], '历史数据加载')

    fetch_btn_1.on_click(_on_fetch_detail)
    fetch_btn_2.on_click(_on_fetch_odds)
    init_btn.on_click(_on_init)
    save_btn.on_click(lambda: ui.notify('结果保存功能待实现', type='info'))
    history_load_btn.on_click(_on_load_history)
    history_page_btn.on_click(lambda: ui.notify('历史数据页面功能待实现', type='info'))
    export_img_btn.on_click(lambda: ui.notify('另存为图片功能待实现', type='info'))
    print_btn.on_click(lambda: ui.notify('打印功能待实现', type='info'))
    if on_back:
        exit_btn.on_click(on_back)
