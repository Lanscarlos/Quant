"""
Match detail page.

Displays league standings and European odds for a selected match.
External API:
  load(match_id) — call before navigating to this page
  render(on_back) — registered with the Router
"""
import datetime

from nicegui import ui, run

from src.db import get_conn
from src.service.match_detail import fetch_match_detail, fetch_match_time
from src.service.match_odds_history import fetch_odds_history
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
    conn = get_conn()
    rows = conn.execute(
        "SELECT match_id, MAX(date), MAX(match_time) FROM match_recent WHERE schedule_id = ? GROUP BY match_id",
        (mid,)
    ).fetchall()
    for match_id, date_str, existing_time in rows:
        # ── 1. 补抓欧赔快照 ────────────────────────────────────────────
        has_odds = conn.execute(
            "SELECT 1 FROM match_odds WHERE schedule_id = ? LIMIT 1", (match_id,)
        ).fetchone()
        if not has_odds:
            try:
                fetch_match_odds_list(match_id)
            except Exception:
                continue  # 历史场次可能已下线（404），跳过

        # ── 2. 补抓 WH 赔率历史（赛前半小时赔率数据来源）─────────────
        has_history = conn.execute(
            "SELECT 1 FROM odds_history WHERE schedule_id = ? AND company_id = ? LIMIT 1",
            (match_id, _WH_COMPANY_ID)
        ).fetchone()
        if not has_history:
            odds_row = conn.execute(
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
            with conn:
                conn.execute(
                    "UPDATE match_recent SET match_time = ? WHERE schedule_id = ? AND match_id = ?",
                    (mt or "", mid, match_id)
                )


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
            title_label  = ui.label('比赛详情') \
                .classes('text-base font-bold text-slate-700 truncate')
            league_label = ui.label('') \
                .classes('text-xs text-blue-600 bg-blue-50 px-2 py-0.5 '
                         'rounded border border-blue-100 flex-shrink-0')
            time_label   = ui.label('') \
                .classes('text-xs text-slate-400 flex-shrink-0 flex-1')
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
                league_label.set_text(match['league'])
                time_label.set_text(match['match_time'])
                extras    = _query_header_extras(mid)
                recent    = _query_recent_matches(mid)
                odds_rows = _query_odds(mid)

                with ui.column().classes('w-full gap-4 p-4'):
                    _render_match_header(match, extras)
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
                        await run.io_bound(_fetch_recent_odds, mid)
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
            await run.io_bound(_fetch_recent_odds, mid)
            detail_content.refresh()
        except Exception as exc:
            err_label.set_text(f'抓取失败：{exc}')
        finally:
            spinner.classes(add='hidden')
            fetch_btn.enable()

    fetch_btn.on_click(_on_fetch)
