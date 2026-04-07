"""
历史数据 — 赛事列表页（新版）.

Displays historical match data with odds analysis panels.
External API:
  render(on_match_click) — registered with the Router
"""
import asyncio
import random

from nicegui import ui, run

from src.db import get_conn
from src.service.match_list import fetch_match_list
from src.service.browser_filter import get_filtered_match_ids
from src.sync.coordinator import should_fetch_match_list


_TABLE_COLS = [
    {'name': 'idx',      'label': '序号',         'field': 'idx',      'align': 'center', 'style': 'width:48px'},
    {'name': 'time',     'label': '时间',         'field': 'match_time','align': 'center', 'style': 'width:130px'},
    {'name': 'home',     'label': '主队',         'field': 'home_team','align': 'left'},
    {'name': 'away',     'label': '客队',         'field': 'away_team','align': 'left'},
    {'name': 'league',   'label': '联赛类型',     'field': 'league',   'align': 'left'},
    {'name': 'open',     'label': '初始赔率',     'field': 'open_odds','align': 'center'},
    {'name': 'h30',      'label': '赛前半小时赔率','field': 'h30_odds', 'align': 'center'},
    {'name': 'cur',      'label': '最终赔率',     'field': 'cur_odds', 'align': 'center'},
    {'name': 'asian',    'label': '最终亚盘',     'field': 'asian',    'align': 'center'},
    {'name': 'analysis', 'label': '分析结论',     'field': 'analysis', 'align': 'left'},
    {'name': 'result',   'label': '赛果输入',     'field': 'score',    'align': 'center'},
    {'name': 'detail',   'label': '详细信息',     'field': 'id',       'align': 'center', 'style': 'width:72px'},
]

_PANEL_LEAGUES = ['胜赔', '章甲', '英超', '德甲', '西甲', '法甲', '荷甲', '欧冠']


def _f(v) -> str:
    return f"{v:.2f}" if v is not None else '-'


def _query_filtered(ids: list) -> list[dict]:
    conn = get_conn()
    if ids:
        placeholders = ",".join("?" * len(ids))
        rows = conn.execute(f"""
            SELECT
                m.schedule_id,
                m.match_time,
                COALESCE(ht.team_name_cn, '') AS home_team,
                COALESCE(at.team_name_cn, '') AS away_team,
                COALESCE(l.league_name_cn, m.league_abbr, '') AS league,
                o.open_win,  o.open_draw,  o.open_lose,
                o.cur_win,   o.cur_draw,   o.cur_lose,
                m.home_score, m.away_score
            FROM matches m
            LEFT JOIN teams   ht ON m.home_team_id = ht.team_id
            LEFT JOIN teams   at ON m.away_team_id = at.team_id
            LEFT JOIN leagues l  ON m.league_abbr  = l.league_abbr
            LEFT JOIN odds_wh o ON o.schedule_id = m.schedule_id
            WHERE CAST(m.schedule_id AS TEXT) IN ({placeholders})
            ORDER BY m.match_time DESC
        """, (*ids,)).fetchall()
    else:
        rows = []

    result = []
    for i, r in enumerate(rows, 1):
        hs, as_ = r[11], r[12]
        score = f"{hs}:{as_}" if hs is not None and as_ is not None else '-'
        result.append({
            'idx':       i,
            'id':        r[0],
            'match_time': r[1] or '-',
            'home_team': r[2],
            'away_team': r[3],
            'league':    r[4],
            'open_odds': f"{_f(r[5])} / {_f(r[6])} / {_f(r[7])}",
            'h30_odds':  '-',
            'cur_odds':  f"{_f(r[8])} / {_f(r[9])} / {_f(r[10])}",
            'asian':     '-',
            'analysis':  '',
            'score':     score,
        })
    return result


# ── UI helpers ────────────────────────────────────────────────────────────────

def _render_odds_panel(system_name: str):
    """搭配的平赔平局值面板（威廉/立博体系）。"""
    with ui.card().classes('flex-1').props('flat').style(
        'border:1px solid #e2e8f0; border-radius:4px; min-width:0'
    ):
        with ui.column().classes('w-full gap-0'):
            # 标题
            with ui.row().classes(
                'w-full items-center justify-center py-1 bg-slate-50 border-b border-slate-200'
            ):
                ui.label(f'搭配的平赔平局值（{system_name}）') \
                    .classes('text-xs font-medium text-slate-700')

            # 列头
            with ui.row().classes('w-full border-b border-slate-200 bg-slate-50'):
                for lbl in _PANEL_LEAGUES:
                    ui.label(lbl).classes(
                        'flex-1 text-center text-xs text-slate-600 '
                        'py-1 border-r border-slate-200'
                    )
                with ui.row().classes('items-center px-2 gap-0.5'):
                    ui.label('其它').classes('text-xs text-slate-600')
                    ui.icon('expand_more').classes('text-sm text-slate-400')

            # 输入行
            with ui.row().classes('w-full border-b border-slate-100'):
                for _ in _PANEL_LEAGUES:
                    ui.input(placeholder='点击输入') \
                        .classes('flex-1 text-xs') \
                        .props('dense borderless')
                ui.input(placeholder='输入') \
                    .classes('w-14 text-xs') \
                    .props('dense borderless')

            # 数据行（空白展示行）
            for _ in range(5):
                with ui.row().classes('w-full border-b border-slate-100'):
                    for _ in range(len(_PANEL_LEAGUES) + 1):
                        ui.label('-').classes('flex-1 text-center text-xs text-slate-300 py-1')

            # 操作按钮
            with ui.row().classes('w-full justify-center gap-3 py-2'):
                ui.button('统计平赔', icon='calculate') \
                    .props('outline size=sm') \
                    .on('click', lambda: ui.notify('统计平赔功能待实现', type='info'))
                ui.button('保存数据', icon='save') \
                    .props('outline size=sm') \
                    .on('click', lambda: ui.notify('保存数据功能待实现', type='info'))


# ── Main render ───────────────────────────────────────────────────────────────

def render(on_match_click: callable = None):
    cached_rows: list = [[]]
    filter_ids: list = [get_filtered_match_ids()]
    is_loading: list = [False]

    with ui.column().classes('w-full h-full gap-0'):

        # ── 标题行 ────────────────────────────────────────────────────
        with ui.row().classes(
            'w-full items-center gap-2 px-4 py-2 bg-white border-b border-slate-200'
        ):
            ui.icon('history').classes('text-xl text-blue-600')
            ui.label('历史数据').classes('text-base font-bold text-slate-700 flex-1')
            err_label = ui.label('').classes('text-xs text-red-500')

        # ── 操作按钮行 ────────────────────────────────────────────────
        with ui.row().classes(
            'w-full items-center gap-2 px-4 py-2 bg-slate-50 '
            'border-b border-slate-200 flex-wrap'
        ):
            recent10_btn   = ui.button('近十场分析数据', icon='analytics')    .props('outline size=sm')
            time_btn       = ui.button('按时间检索',    icon='access_time')   .props('outline size=sm')
            league_btn     = ui.button('按联赛检索',    icon='emoji_events')  .props('outline size=sm')
            team_btn       = ui.button('按球队检索',    icon='group')         .props('outline size=sm')
            odds_btn       = ui.button('按赔率检索',    icon='filter_list')   .props('outline size=sm')
            export_img_btn = ui.button('另存为图片',    icon='image')         .props('outline size=sm')
            print_btn      = ui.button('检索结果打印',  icon='print')         .props('outline size=sm')
            save_btn       = ui.button('保存',          icon='save')          .props('outline size=sm')
            home_btn       = ui.button('返回主界面',    icon='home')          .props('outline size=sm')
            exit_btn       = ui.button('退出',          icon='exit_to_app')   .props('outline size=sm')
            refresh_btn    = ui.button('刷新',          icon='refresh')       .props('outline size=sm')

        # ── 主内容区 ──────────────────────────────────────────────────
        with ui.scroll_area().classes('w-full flex-1'):
            with ui.column().classes('w-full gap-3 p-3'):

                # 主数据表格（蓝色边框）
                with ui.element('div').style(
                    'width:100%; border:2px solid #3b82f6; border-radius:4px; overflow:hidden'
                ):
                    @ui.refreshable
                    def data_table():
                        if is_loading[0]:
                            with ui.row().classes(
                                'w-full items-center justify-center gap-3 py-16'
                            ):
                                ui.spinner('dots', size='lg', color='blue-6')
                                ui.label('正在加载...').classes('text-sm text-slate-400')
                            return

                        rows = cached_rows[0]
                        if not rows:
                            with ui.row().classes(
                                'w-full items-center justify-center py-10 gap-2'
                            ):
                                ui.icon('search_off').classes('text-3xl text-slate-300')
                                ui.label('暂无数据，请点击按钮加载').classes('text-sm text-slate-400')
                            return

                        tbl = (
                            ui.table(columns=_TABLE_COLS, rows=rows, row_key='id')
                            .classes('w-full text-xs')
                            .props('dense flat')
                        )

                        # 详情列：只渲染图标，实际点击通过 rowClick 响应
                        tbl.add_slot('body-cell-detail', '''
                            <q-td :props="props" class="cursor-pointer">
                                <q-icon name="open_in_new" color="blue-6" size="14px" />
                            </q-td>
                        ''')

                        if on_match_click:
                            tbl.on('rowClick', lambda e: on_match_click(e.args[1]['id']))

                    data_table()

                # 底部两个平赔面板
                with ui.row().classes('w-full gap-3 items-start'):
                    for name in ('威廉体系', '立博体系'):
                        _render_odds_panel(name)

    # ── 事件绑定 ──────────────────────────────────────────────────────

    def _reload():
        cached_rows[0] = _query_filtered(filter_ids[0])
        data_table.refresh()

    async def _on_fetch():
        err_label.set_text('')
        is_loading[0] = True
        data_table.refresh()
        try:
            await run.io_bound(fetch_match_list)
            is_loading[0] = False
            _reload()
        except Exception as exc:
            is_loading[0] = False
            data_table.refresh()
            err_label.set_text(f'抓取失败：{exc}')

    async def _on_refresh():
        refresh_btn.props(add='loading disable')
        is_loading[0] = True
        data_table.refresh()
        try:
            filter_ids[0], _ = await asyncio.gather(
                run.io_bound(get_filtered_match_ids),
                asyncio.sleep(random.uniform(0.5, 2.0)),
            )
            is_loading[0] = False
            _reload()
        except Exception:
            is_loading[0] = False
            data_table.refresh()
        finally:
            refresh_btn.props(remove='loading disable')

    recent10_btn.on_click(lambda: ui.notify('近十场分析数据功能待实现', type='info'))
    time_btn.on_click(lambda: ui.notify('按时间检索功能待实现', type='info'))
    league_btn.on_click(lambda: ui.notify('按联赛检索功能待实现', type='info'))
    team_btn.on_click(lambda: ui.notify('按球队检索功能待实现', type='info'))
    odds_btn.on_click(lambda: ui.notify('按赔率检索功能待实现', type='info'))
    export_img_btn.on_click(lambda: ui.notify('另存为图片功能待实现', type='info'))
    print_btn.on_click(lambda: ui.notify('打印功能待实现', type='info'))
    save_btn.on_click(lambda: ui.notify('保存功能待实现', type='info'))
    home_btn.on_click(lambda: ui.notify('已在主界面', type='info'))
    exit_btn.on_click(lambda: ui.notify('退出功能待实现', type='info'))
    refresh_btn.on_click(_on_refresh)

    # 初始加载 + 自动抓取
    _reload()

    async def _auto_fetch():
        if should_fetch_match_list():
            await _on_fetch()

    ui.timer(0, _auto_fetch, once=True)
