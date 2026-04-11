"""
历史数据 — 已保存赛事分析页.

Displays user-saved match analysis records.
External API:
  render(on_match_click) — registered with the Router
"""

import asyncio
import random

from nicegui import ui, run

from src.db.repo.history import list_saved_matches, list_distinct_leagues, list_distinct_teams

_TABLE_COLS = [
    {'name': 'idx',      'label': '序号',          'field': 'idx',       'align': 'center', 'style': 'width:48px'},
    {'name': 'time',     'label': '时间',           'field': 'match_time', 'align': 'center', 'style': 'width:130px'},
    {'name': 'home',     'label': '主队',           'field': 'home_team', 'align': 'left'},
    {'name': 'away',     'label': '客队',           'field': 'away_team', 'align': 'left'},
    {'name': 'league',   'label': '联赛类型',       'field': 'league',    'align': 'left'},
    {'name': 'open',     'label': '初始赔率',       'field': 'open_odds', 'align': 'center'},
    {'name': 'h30',      'label': '赛前半小时赔率', 'field': 'h30_odds',  'align': 'center'},
    {'name': 'cur',      'label': '最终赔率',       'field': 'cur_odds',  'align': 'center'},
    {'name': 'asian',    'label': '最终亚盘',       'field': 'asian',     'align': 'center'},
    {'name': 'analysis', 'label': '分析结论',       'field': 'analysis',  'align': 'left'},
    {'name': 'result',   'label': '赛果输入',       'field': 'score',     'align': 'center'},
    {'name': 'detail',   'label': '详细信息',       'field': 'id',        'align': 'center', 'style': 'width:72px'},
]

_PANEL_LEAGUES = ['胜赔', '章甲', '英超', '德甲', '西甲', '法甲', '荷甲', '欧冠']

_ODDS_OPTIONS = {
    'wh_open_win':   '威廉 初始 胜',
    'wh_open_draw':  '威廉 初始 平',
    'wh_open_lose':  '威廉 初始 负',
    'wh_cur_win':    '威廉 即时 胜',
    'wh_cur_draw':   '威廉 即时 平',
    'wh_cur_lose':   '威廉 即时 负',
    'coral_open_win':  '立博 初始 胜',
    'coral_open_draw': '立博 初始 平',
    'coral_open_lose': '立博 初始 负',
    'coral_cur_win':   '立博 即时 胜',
    'coral_cur_draw':  '立博 即时 平',
    'coral_cur_lose':  '立博 即时 负',
}


def _render_odds_panel(system_name: str):
    """搭配的平赔平局值面板（威廉/立博体系）。"""
    with ui.card().classes('flex-1').props('flat').style(
        'border:1px solid #e2e8f0; border-radius:4px; min-width:0'
    ):
        with ui.column().classes('w-full gap-0'):
            with ui.row().classes(
                'w-full items-center justify-center py-1 bg-slate-50 border-b border-slate-200'
            ):
                ui.label(f'搭配的平赔平局值（{system_name}）') \
                    .classes('text-xs font-medium text-slate-700')

            with ui.row().classes('w-full border-b border-slate-200 bg-slate-50'):
                for lbl in _PANEL_LEAGUES:
                    ui.label(lbl).classes(
                        'flex-1 text-center text-xs text-slate-600 '
                        'py-1 border-r border-slate-200'
                    )
                with ui.row().classes('items-center px-2 gap-0.5'):
                    ui.label('其它').classes('text-xs text-slate-600')
                    ui.icon('expand_more').classes('text-sm text-slate-400')

            with ui.row().classes('w-full border-b border-slate-100'):
                for _ in _PANEL_LEAGUES:
                    ui.input(placeholder='点击输入') \
                        .classes('flex-1 text-xs') \
                        .props('dense borderless')
                ui.input(placeholder='输入') \
                    .classes('w-14 text-xs') \
                    .props('dense borderless')

            for _ in range(5):
                with ui.row().classes('w-full border-b border-slate-100'):
                    for _ in range(len(_PANEL_LEAGUES) + 1):
                        ui.label('-').classes('flex-1 text-center text-xs text-slate-300 py-1')

            with ui.row().classes('w-full justify-center gap-3 py-2'):
                ui.button('统计平赔', icon='calculate') \
                    .props('outline size=sm') \
                    .on('click', lambda: ui.notify('统计平赔功能待实现', type='info'))
                ui.button('保存数据', icon='save') \
                    .props('outline size=sm') \
                    .on('click', lambda: ui.notify('保存数据功能待实现', type='info'))


def render(on_match_click: callable = None):
    cached_rows: list = [[]]
    active_filters: list = [{}]
    is_loading: list = [False]

    # ── 筛选对话框内部状态 ─────────────────────────────────────────────
    league_avail:      list = [[]]
    league_sel:        list = [set()]
    team_avail:        list = [[]]
    team_sel:          list = [set()]
    team_search_query: list = ['']

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
            recent10_btn   = ui.button('近十场分析数据', icon='analytics')   .props('outline size=sm')
            time_btn       = ui.button('按时间检索',    icon='access_time')  .props('outline size=sm')
            league_btn     = ui.button('按联赛检索',    icon='emoji_events') .props('outline size=sm')
            team_btn       = ui.button('按球队检索',    icon='group')        .props('outline size=sm')
            odds_btn       = ui.button('按赔率检索',    icon='filter_list')  .props('outline size=sm')
            export_img_btn = ui.button('另存为图片',    icon='image')        .props('outline size=sm')
            print_btn      = ui.button('检索结果打印',  icon='print')        .props('outline size=sm')
            save_btn       = ui.button('保存',          icon='save')         .props('outline size=sm')
            refresh_btn    = ui.button('刷新',          icon='refresh')      .props('outline size=sm')

        # ── 筛选指示行 ────────────────────────────────────────────────
        @ui.refreshable
        def filter_chips():
            f = active_filters[0]
            if not f:
                return
            with ui.row().classes(
                'w-full items-center gap-2 px-4 py-2 bg-blue-50 '
                'border-b border-blue-200 flex-wrap'
            ):
                ui.icon('filter_alt').classes('text-xs text-blue-500')
                ui.label('筛选条件').classes('text-xs font-medium text-blue-700')

                if 'limit' in f:
                    ui.chip(f"近{f['limit']}场", icon='analytics', removable=True,
                            on_value_change=lambda e: _clear_filter('limit') if not e.value else None) \
                        .props('color=blue-2 text-color=blue-10 size=sm')

                if 'time_from' in f or 'time_to' in f:
                    tf = f.get('time_from', '…')
                    tt = f.get('time_to', '…')
                    ui.chip(f"{tf} ~ {tt}", icon='access_time', removable=True,
                            on_value_change=lambda e: _clear_filter('time') if not e.value else None) \
                        .props('color=blue-2 text-color=blue-10 size=sm')

                if 'league' in f:
                    leagues = f['league']
                    lbl = '、'.join(leagues[:2]) + (f' 等{len(leagues)}个' if len(leagues) > 2 else '')
                    ui.chip(lbl, icon='emoji_events', removable=True,
                            on_value_change=lambda e: _clear_filter('league') if not e.value else None) \
                        .props('color=blue-2 text-color=blue-10 size=sm')

                if 'team' in f:
                    teams = f['team']
                    role_label = {'home': ' (主)', 'away': ' (客)', 'both': ''}.get(
                        f.get('team_role', 'both'), '')
                    lbl = '、'.join(teams[:2]) + (f' 等{len(teams)}个' if len(teams) > 2 else '') + role_label
                    ui.chip(lbl, icon='group', removable=True,
                            on_value_change=lambda e: _clear_filter('team') if not e.value else None) \
                        .props('color=blue-2 text-color=blue-10 size=sm')

                if 'odds_type' in f:
                    label = _ODDS_OPTIONS.get(f['odds_type'], f['odds_type'])
                    lo = f.get('odds_min', '…')
                    hi = f.get('odds_max', '…')
                    ui.chip(f"{label}  {lo}~{hi}", icon='filter_list', removable=True,
                            on_value_change=lambda e: _clear_filter('odds') if not e.value else None) \
                        .props('color=blue-2 text-color=blue-10 size=sm')

                ui.button('重置', icon='clear_all', on_click=_clear_all_filters) \
                    .props('flat dense size=sm color=blue-8').classes('ml-auto')

        filter_chips()

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
                                ui.icon('bookmark_border').classes('text-3xl text-slate-300')
                                ui.label('暂无历史数据').classes('text-sm text-slate-400')
                            return

                        tbl = (
                            ui.table(columns=_TABLE_COLS, rows=rows, row_key='id')
                            .classes('w-full text-xs')
                            .props('dense flat')
                        )

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

    # ── 筛选对话框 ────────────────────────────────────────────────────

    # 按时间检索
    with ui.dialog() as time_dialog, ui.card().classes('w-96'):
        ui.label('按时间检索').classes('text-base font-bold text-slate-700 mb-1')
        time_from_input = ui.input('开始日期', placeholder='YYYY-MM-DD').props('outlined dense').classes('w-full')
        with time_from_input:
            with ui.menu().props('no-parent-event') as from_menu:
                ui.date(mask='YYYY-MM-DD').bind_value(time_from_input)
            with time_from_input.add_slot('append'):
                ui.icon('edit_calendar').on('click', from_menu.open).classes('cursor-pointer')

        time_to_input = ui.input('结束日期', placeholder='YYYY-MM-DD').props('outlined dense').classes('w-full mt-2')
        with time_to_input:
            with ui.menu().props('no-parent-event') as to_menu:
                ui.date(mask='YYYY-MM-DD').bind_value(time_to_input)
            with time_to_input.add_slot('append'):
                ui.icon('edit_calendar').on('click', to_menu.open).classes('cursor-pointer')

        with ui.row().classes('w-full justify-end gap-2 mt-3'):
            ui.button('清除', on_click=lambda: _apply_time_filter(None, None)).props('flat')
            ui.button('应用', on_click=lambda: _apply_time_filter(
                time_from_input.value or None, time_to_input.value or None
            )).props('unelevated color=primary')

    # 按联赛检索
    with ui.dialog() as league_dialog, ui.card().classes('w-[480px]'):
        ui.label('按联赛检索').classes('text-base font-bold text-slate-700 mb-3')

        @ui.refreshable
        def _league_opts():
            if not league_avail[0]:
                with ui.row().classes('w-full justify-center py-6'):
                    ui.label('暂无联赛数据').classes('text-xs text-slate-400')
                return
            with ui.row().classes('flex-wrap gap-2 py-1'):
                for opt in league_avail[0]:
                    is_sel = opt in league_sel[0]
                    (ui.button(opt)
                        .props(f'{"unelevated" if is_sel else "outline"} color=primary rounded')
                        .on_click(lambda _, o=opt: _on_league_toggle(o)))

        _league_opts()

        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('清除', on_click=lambda: _apply_league_filter([])).props('flat')
            ui.button('应用', on_click=lambda: _apply_league_filter(list(league_sel[0]))) \
                .props('unelevated color=primary')

    # 按球队检索
    with ui.dialog() as team_dialog, ui.card().classes('w-[520px]'):
        ui.label('按球队检索').classes('text-base font-bold text-slate-700 mb-2')

        team_search_input = ui.input(placeholder='搜索球队…') \
            .props('outlined dense clearable').classes('w-full')

        with ui.scroll_area().classes('w-full h-56 mt-2'):
            @ui.refreshable
            def _team_opts():
                q = team_search_query[0].lower()
                visible = [t for t in team_avail[0] if not q or q in t.lower()]
                if not visible:
                    with ui.row().classes('w-full justify-center py-6'):
                        ui.label('无匹配球队').classes('text-xs text-slate-400')
                    return
                with ui.row().classes('flex-wrap gap-2 py-1 pr-2'):
                    for opt in visible:
                        is_sel = opt in team_sel[0]
                        (ui.button(opt)
                            .props(f'{"unelevated" if is_sel else "outline"} color=primary rounded')
                            .on_click(lambda _, o=opt: _on_team_toggle(o)))

            _team_opts()

        def _on_team_search(e):
            team_search_query[0] = e.value or ''
            _team_opts.refresh()

        team_search_input.on_value_change(_on_team_search)

        with ui.column().classes('w-full gap-0.5 mt-3'):
            ui.label('检索范围').classes('text-xs text-slate-400')
            team_role_toggle = ui.toggle(
                {'both': '全部', 'home': '仅主队', 'away': '仅客队'},
                value='both',
            ).props('size=sm')

        with ui.row().classes('w-full justify-end gap-2 mt-3'):
            ui.button('清除', on_click=lambda: _apply_team_filter([], 'both')).props('flat')
            ui.button('应用', on_click=lambda: _apply_team_filter(
                list(team_sel[0]), team_role_toggle.value
            )).props('unelevated color=primary')

    # 按赔率检索
    with ui.dialog() as odds_dialog, ui.card().classes('w-96'):
        ui.label('按赔率检索').classes('text-base font-bold text-slate-700 mb-1')
        odds_type_select = ui.select(options=_ODDS_OPTIONS, label='赔率类型') \
            .classes('w-full').props('outlined dense')
        with ui.row().classes('w-full gap-2 mt-2'):
            odds_min_input = ui.number('最小值', format='%.2f') \
                .classes('flex-1').props('outlined dense clearable')
            odds_max_input = ui.number('最大值', format='%.2f') \
                .classes('flex-1').props('outlined dense clearable')

        with ui.row().classes('w-full justify-end gap-2 mt-3'):
            ui.button('清除', on_click=lambda: _apply_odds_filter(None)).props('flat')
            ui.button('应用', on_click=lambda: _apply_odds_filter(
                odds_type_select.value, odds_min_input.value, odds_max_input.value
            )).props('unelevated color=primary')

    # ── 内部函数 ──────────────────────────────────────────────────────

    def _reload():
        filters = active_filters[0] if active_filters[0] else None
        cached_rows[0] = list_saved_matches(filters)
        data_table.refresh()
        filter_chips.refresh()

    def _clear_filter(group: str):
        f = active_filters[0]
        if group == 'time':
            f.pop('time_from', None)
            f.pop('time_to', None)
        elif group == 'league':
            f.pop('league', None)
        elif group == 'team':
            f.pop('team', None)
            f.pop('team_role', None)
        elif group == 'odds':
            f.pop('odds_type', None)
            f.pop('odds_min', None)
            f.pop('odds_max', None)
        elif group == 'limit':
            f.pop('limit', None)
        _reload()

    def _clear_all_filters():
        active_filters[0] = {}
        _reload()

    def _apply_time_filter(from_val, to_val):
        f = active_filters[0]
        f.pop('limit', None)
        if from_val is None and to_val is None:
            f.pop('time_from', None)
            f.pop('time_to', None)
        else:
            if from_val:
                f['time_from'] = from_val
            else:
                f.pop('time_from', None)
            if to_val:
                f['time_to'] = to_val
            else:
                f.pop('time_to', None)
        time_dialog.close()
        _reload()

    def _on_league_toggle(name: str):
        sel = league_sel[0]
        sel.discard(name) if name in sel else sel.add(name)
        _league_opts.refresh()

    def _on_team_toggle(name: str):
        sel = team_sel[0]
        sel.discard(name) if name in sel else sel.add(name)
        _team_opts.refresh()

    def _apply_league_filter(leagues: list):
        f = active_filters[0]
        f.pop('limit', None)
        if leagues:
            f['league'] = leagues
        else:
            f.pop('league', None)
        league_sel[0] = set(leagues)
        league_dialog.close()
        _reload()

    def _apply_team_filter(teams: list, role='both'):
        f = active_filters[0]
        f.pop('limit', None)
        if teams:
            f['team'] = teams
            f['team_role'] = role or 'both'
        else:
            f.pop('team', None)
            f.pop('team_role', None)
        team_sel[0] = set(teams)
        team_dialog.close()
        _reload()

    def _apply_odds_filter(odds_type, min_val=None, max_val=None):
        f = active_filters[0]
        f.pop('limit', None)
        if odds_type is None:
            f.pop('odds_type', None)
            f.pop('odds_min', None)
            f.pop('odds_max', None)
        else:
            f['odds_type'] = odds_type
            if min_val is not None:
                f['odds_min'] = float(min_val)
            else:
                f.pop('odds_min', None)
            if max_val is not None:
                f['odds_max'] = float(max_val)
            else:
                f.pop('odds_max', None)
        odds_dialog.close()
        _reload()

    def _on_recent10():
        active_filters[0] = {'limit': 10}
        _reload()

    def _on_open_league_dialog():
        league_avail[0] = list_distinct_leagues()
        league_sel[0] = set(active_filters[0].get('league', []))
        _league_opts.refresh()
        league_dialog.open()

    def _on_open_team_dialog():
        team_avail[0] = list_distinct_teams()
        team_sel[0] = set(active_filters[0].get('team', []))
        team_search_query[0] = ''
        team_search_input.set_value('')
        team_role_toggle.set_value(active_filters[0].get('team_role', 'both'))
        _team_opts.refresh()
        team_dialog.open()

    async def _on_refresh():
        refresh_btn.props(add='loading disable')
        is_loading[0] = True
        data_table.refresh()
        try:
            filters = active_filters[0] if active_filters[0] else None
            cached_rows[0], _ = await asyncio.gather(
                run.io_bound(list_saved_matches, filters),
                asyncio.sleep(random.uniform(0.1, 0.6)),
            )
            is_loading[0] = False
            data_table.refresh()
            filter_chips.refresh()
        except Exception:
            is_loading[0] = False
            data_table.refresh()
        finally:
            refresh_btn.props(remove='loading disable')

    # ── 事件绑定 ──────────────────────────────────────────────────────
    recent10_btn.on_click(_on_recent10)
    time_btn.on_click(time_dialog.open)
    league_btn.on_click(_on_open_league_dialog)
    team_btn.on_click(_on_open_team_dialog)
    odds_btn.on_click(odds_dialog.open)
    export_img_btn.on_click(lambda: ui.notify('另存为图片功能待实现', type='info'))
    print_btn.on_click(lambda: ui.notify('打印功能待实现', type='info'))
    save_btn.on_click(lambda: ui.notify('保存功能待实现', type='info'))
    refresh_btn.on_click(_on_refresh)

    # 初始加载
    _reload()
