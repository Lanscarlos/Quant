"""
Match detail page.

Displays league standings and European odds for a selected match.
External API:
  load(match_id) — call before navigating to this page
  render(on_back) — registered with the Router
"""
import asyncio
import datetime

from nicegui import ui, run

from src.db import get_conn
from src.service.archived.match_detail import fetch_match_detail, fetch_match_time
from src.service.archived.match_odds_history import fetch_odds_history
from src.service.archived.match_odds_list import fetch_match_odds_list
from src.sync.coordinator import should_fetch_detail, should_fetch_odds

_state: dict = {'match_id': None, 'sections': None, 'auto_fetched': False, 'fetching': False}
_refresh_fn: list = [None]

_WH_COMPANY_ID = 115  # William Hill


def load(match_id: int | str) -> None:
    """Set current match and trigger page refresh."""
    _state['match_id'] = int(match_id)
    _state['sections'] = None
    _state['auto_fetched'] = False
    _state['fetching'] = False
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


def _query_h2h(mid: int) -> dict:
    """Returns last 6 head-to-head matches between the two teams, with WH final odds."""
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
        # side from perspective of the current match's home team
        side = '主' if home_id == h_id else '客'
        if home_ft is not None and away_ft is not None:
            focus_win = (home_ft > away_ft) if home_id == h_id else (away_ft > home_ft)
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
            -- 优先用 matches.match_time，其次用 match_recent.match_time
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
    """Queries points (from standings) and recent W/D/L counts."""
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

def _stat_chip(label: str, value):
    with ui.column().classes(
        'items-center gap-0 flex-shrink-0 '
        'bg-slate-50 border border-slate-200 rounded-lg px-3 py-1'
    ):
        ui.label(label).classes('text-xs text-slate-400 leading-none')
        ui.label(_d(value)).classes('text-sm font-bold text-slate-700 leading-none mt-0.5')


def _render_team_half(team_name: str, rank, pts, wdl: tuple | None, is_home: bool):
    """Renders one team's half of the match header (home or away)."""
    badge_color = 'blue'  if is_home else 'red'
    side_label  = '主队'  if is_home else '客队'
    name_cls    = 'text-blue-700' if is_home else 'text-red-600'

    with ui.column().classes('flex-1 min-w-0 gap-2'):
        # Row 1: badge + name
        with ui.row().classes('w-full items-center gap-2'):
            ui.badge(side_label, color=badge_color).classes('text-xs flex-shrink-0')
            ui.label(team_name).classes(
                f'text-base font-bold {name_cls} truncate min-w-0'
            )
        # Row 2: stat chips + W/D/L
        with ui.row().classes('items-center gap-2 flex-wrap'):
            _stat_chip('排名', rank)
            _stat_chip('积分', pts)
            if wdl:
                w, d, l = wdl
                with ui.column().classes(
                    'items-center gap-0 flex-shrink-0 '
                    'bg-slate-50 border border-slate-200 rounded-lg px-3 py-1'
                ):
                    ui.label('近6场').classes('text-xs text-slate-400 leading-none')
                    ui.label(f"{w}胜{d}平{l}负").classes(
                        'text-sm font-bold text-slate-700 leading-none mt-0.5'
                    )


def _render_match_header(match: dict, extras: dict):
    with ui.row().classes('w-full gap-3 items-start'):
        with ui.card().classes('flex-1').props('flat bordered'):
            with ui.column().classes('p-3'):
                _render_team_half(
                    match['home_team'], match['home_rank'], extras.get('home_pts'),
                    extras.get('home_wdl'), is_home=True,
                )
        with ui.card().classes('flex-1').props('flat bordered'):
            with ui.column().classes('p-3'):
                _render_team_half(
                    match['away_team'], match['away_rank'], extras.get('away_pts'),
                    extras.get('away_wdl'), is_home=False,
                )


_RECENT_COLS = [
    {'name': 'home',  'label': '主场',   'field': 'home_name', 'align': 'left'},
    {'name': 'away',  'label': '客场',   'field': 'away_name', 'align': 'left'},
    {'name': 'score', 'label': '比分',   'field': 'score',     'align': 'center'},
    {'name': 'h30',   'label': '赛前半小时', 'field': 'h30_odds', 'align': 'center'},
    {'name': 'cur',   'label': '最终赔率',     'field': 'cur_odds', 'align': 'center'},
]


def _render_recent_matches(recent: dict, match: dict):
    with ui.column().classes('w-full gap-2'):
        ui.label('联赛数据').classes('text-sm font-semibold text-slate-600 px-1')
        has_data = any(recent.get(s) for s in ('home', 'away'))
        if not has_data:
            _no_data_hint()
            return
        with ui.row().classes('w-full gap-3 items-start'):
            for side, team_key, is_home in [
                ('home', 'home_team', True),
                ('away', 'away_team', False),
            ]:
                rows = recent.get(side, [])
                color_cls   = 'text-blue-700' if is_home else 'text-red-600'
                badge_color = 'blue' if is_home else 'red'
                side_label  = '主' if is_home else '客'
                with ui.card().classes('flex-1').props('flat bordered'):
                    with ui.column().classes('gap-1 p-3'):
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


_H2H_COLS = [
    {'name': 'side',      'label': '主/客', 'field': 'side',      'align': 'center'},
    {'name': 'home_name', 'label': '主场',   'field': 'home_name', 'align': 'left'},
    {'name': 'away_name', 'label': '客场',   'field': 'away_name', 'align': 'left'},
    {'name': 'score',     'label': '比分',   'field': 'score',     'align': 'center'},
    {'name': 'cur',       'label': '最终赔率', 'field': 'cur_odds',  'align': 'center'},
]


def _render_h2h(h2h: dict, fetched: bool = False):
    with ui.column().classes('w-full gap-2'):
        with ui.row().classes('items-center gap-2 px-1'):
            ui.label('近六场交手').classes('text-sm font-semibold text-slate-600')
            rows = h2h['rows']
            if rows:
                win, draw, loss = h2h['win'], h2h['draw'], h2h['loss']
                ui.label(f'胜{win} 负{loss} 平{draw}').classes(
                    'text-xs text-slate-500 bg-slate-50 border border-slate-200 '
                    'rounded px-2 py-0.5'
                )
        if not h2h['rows']:
            if fetched:
                with ui.row().classes('w-full items-center gap-2 py-3 justify-center'):
                    ui.icon('info_outline').classes('text-slate-300 text-lg')
                    ui.label('两队暂无历史交手记录').classes('text-xs text-slate-400')
            else:
                _no_data_hint()
            return
        ui.table(columns=_H2H_COLS, rows=h2h['rows']) \
            .classes('w-full text-xs') \
            .props('dense flat bordered')


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


def _parse_year(date_str: str | None) -> int:
    """从 'YY-MM-DD' 格式日期中解析 4 位年份，用于补全 odds_history 的时间戳。"""
    if date_str:
        try:
            return 2000 + int(str(date_str)[:2])
        except (ValueError, TypeError):
            pass
    return datetime.date.today().year


def _fetch_recent_odds(mid: int) -> None:
    """为 match_recent 里的历史场次补抓欧赔快照及赔率历史（赛前半小时赔率依赖后者）。"""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    conn = get_conn()
    rows = conn.execute(
        "SELECT match_id, MAX(date), MAX(match_time) FROM match_recent WHERE schedule_id = ? GROUP BY match_id",
        (mid,)
    ).fetchall()

    def _process_one(match_id, date_str, existing_time):
        c = get_conn()
        # ── 1. 补抓欧赔快照 ────────────────────────────────────────────
        has_odds = c.execute(
            "SELECT 1 FROM match_odds WHERE schedule_id = ? LIMIT 1", (match_id,)
        ).fetchone()
        if not has_odds:
            try:
                fetch_match_odds_list(match_id)
            except Exception:
                return  # 历史场次可能已下线（404），跳过

        # ── 2. 补抓 WH 赔率历史（赛前半小时赔率数据来源）─────────────
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
                    pass  # 历史赔率页面可能已下线，跳过

        # ── 3. 补抓开球时间（精确 T-30min 计算的基础）──────────────────
        if existing_time is None:  # None=未尝试；''=已尝试但页面已下线
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


def _query_all_sections(mid: int) -> dict:
    """Batch-query all detail sections for async loading."""
    return {
        'extras': _query_header_extras(mid),
        'recent': _query_recent_matches(mid),
        'h2h': _query_h2h(mid),
        'odds': _query_odds(mid),
        'detail_fetched': get_conn().execute(
            "SELECT 1 FROM match_standings WHERE schedule_id = ? LIMIT 1", (mid,)
        ).fetchone() is not None,
    }


def _no_data_hint():
    with ui.row().classes('w-full items-center gap-2 py-3 justify-center'):
        ui.icon('info_outline').classes('text-slate-300 text-lg')
        ui.label('暂无数据，请点击「抓取数据」').classes('text-xs text-slate-400')


def _render_skeleton():
    """Render skeleton placeholders mimicking the real content layout."""
    _W = 'animation="wave"'
    # 联赛数据
    with ui.column().classes('w-full gap-2'):
        ui.skeleton('text').classes('w-20').props(_W)
        with ui.row().classes('w-full gap-3 items-start'):
            for _ in range(2):
                with ui.card().classes('flex-1').props('flat bordered'):
                    with ui.column().classes('gap-2 p-3'):
                        ui.skeleton('text').classes('w-32').props(_W)
                        for _ in range(6):
                            ui.skeleton('text').classes('w-full').props(_W)
    ui.separator().classes('my-1')
    # 近六场交手
    with ui.column().classes('w-full gap-2'):
        ui.skeleton('text').classes('w-24').props(_W)
        for _ in range(4):
            ui.skeleton('text').classes('w-full').props(_W)
    ui.separator().classes('my-1')
    # 欧赔数据
    with ui.column().classes('w-full gap-2'):
        ui.skeleton('text').classes('w-20').props(_W)
        with ui.row().classes('w-full gap-4'):
            for _ in range(2):
                with ui.column().classes('flex-1 gap-2'):
                    ui.skeleton('text').classes('w-28').props(_W)
                    for _ in range(3):
                        ui.skeleton('text').classes('w-full').props(_W)


# ── Main render ───────────────────────────────────────────────────────────────

def render(on_back: callable = None):
    with ui.column().classes('w-full h-full gap-0'):

        # ── 顶部工具栏 ────────────────────────────────────────────────
        with ui.column().classes('w-full gap-0 bg-white border-b border-slate-200'):
            # 标题行
            with ui.row().classes('w-full items-center gap-2 px-4 py-2'):
                back_btn = ui.button(icon='arrow_back') \
                    .props('unelevated round size=sm') \
                    .classes('!bg-slate-100 !text-slate-500')
                if on_back:
                    back_btn.on_click(on_back)
                ui.icon('analytics').classes('text-xl text-blue-600')
                title_label  = ui.label('比赛详情') \
                    .classes('text-base font-bold text-slate-700 truncate flex-1')
                league_label = ui.label('') \
                    .classes('text-xs text-blue-600 bg-blue-50 px-2 py-0.5 '
                             'rounded border border-blue-100 flex-shrink-0')
                time_label   = ui.label('') \
                    .classes('text-xs text-slate-400 flex-shrink-0')
                spinner   = ui.spinner(size='sm').classes('hidden')
                err_label = ui.label('').classes('text-xs text-red-500')
            # 操作按钮行
            with ui.row().classes('w-full items-center gap-2 px-4 py-2 bg-slate-50 border-t border-slate-100 flex-wrap'):
                fetch_btn_1      = ui.button('抓取数据1',   icon='download')    .props('outline size=sm')
                fetch_btn_2      = ui.button('抓取数据2',   icon='bar_chart')   .props('outline size=sm')
                init_btn         = ui.button('数据分析初始', icon='restart_alt') .props('outline size=sm')
                save_btn         = ui.button('结果保存',    icon='save')         .props('outline size=sm')
                history_load_btn = ui.button('历史数据加载', icon='history')     .props('outline size=sm')
                history_page_btn = ui.button('历史数据页面', icon='table_chart') .props('outline size=sm')
                export_img_btn   = ui.button('另存为图片',  icon='image')        .props('outline size=sm')
                print_btn        = ui.button('分析结果打印', icon='print')       .props('outline size=sm')
                exit_btn         = ui.button('退出',        icon='exit_to_app')  .props('outline size=sm')

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

                title_label.set_text(f"{match['home_team']}  vs  {match['away_team']}")
                league_label.set_text(match['league'])
                time_label.set_text(match['match_time'])

                sections = _state.get('sections')

                with ui.column().classes('w-full gap-4 p-4'):
                    if sections:
                        _render_match_header(match, sections['extras'])
                        ui.separator().classes('my-1')
                        _render_recent_matches(sections['recent'], match)
                        ui.separator().classes('my-1')
                        _render_h2h(sections['h2h'], sections['detail_fetched'])
                        ui.separator().classes('my-1')
                        _render_odds(sections['odds'])
                    else:
                        _render_match_header(match, {})
                        ui.separator().classes('my-1')
                        _render_skeleton()

                if not sections and not _state.get('fetching'):
                    # 首次渲染：异步加载数据区
                    async def _load_sections():
                        data = await run.io_bound(_query_all_sections, mid)
                        _state['sections'] = data
                        detail_content.refresh()
                    ui.timer(0, _load_sections, once=True)

                elif not _state.get('auto_fetched'):
                    # 数据已加载：检查是否需要自动抓取
                    async def _auto_fetch():
                        status = match['status']
                        need_detail = should_fetch_detail(mid, status=status)
                        need_odds   = should_fetch_odds(mid, status=status)
                        if not (need_detail or need_odds):
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
        """通用抓取流程：显示 spinner、禁用按钮、执行协程、刷新内容。"""
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

    # 抓取数据1：赛事详情（联赛数据）
    async def _on_fetch_detail():
        mid = _state.get('match_id')
        if mid:
            await _run_fetch([lambda: run.io_bound(fetch_match_detail, mid)], '抓取数据1')

    # 抓取数据2：欧赔快照
    async def _on_fetch_odds():
        mid = _state.get('match_id')
        if mid:
            await _run_fetch([lambda: run.io_bound(fetch_match_odds_list, mid)], '抓取数据2')

    # 数据分析初始：清空已加载数据，重新触发自动加载
    def _on_init():
        _state['sections'] = None
        _state['auto_fetched'] = False
        _state['fetching'] = False
        err_label.set_text('')
        detail_content.refresh()

    # 历史数据加载：补抓近期历史赛事欧赔及赔率历史
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
