"""历史数据页 — 筛选对话框构建器."""

from nicegui import ui

from .constants import ODDS_OPTIONS


def build_time_dialog(on_apply):
    """按时间检索对话框.

    on_apply(from_val, to_val) — 应用或清除时间筛选.
    返回 dialog.
    """
    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label('按时间检索').classes('text-base font-bold text-slate-700 mb-1')
        time_from_input = ui.input('开始日期', placeholder='YYYY-MM-DD') \
            .props('outlined dense').classes('w-full')
        with time_from_input:
            with ui.menu().props('no-parent-event') as from_menu:
                ui.date(mask='YYYY-MM-DD').bind_value(time_from_input)
            with time_from_input.add_slot('append'):
                ui.icon('edit_calendar').on('click', from_menu.open).classes('cursor-pointer')

        time_to_input = ui.input('结束日期', placeholder='YYYY-MM-DD') \
            .props('outlined dense').classes('w-full mt-2')
        with time_to_input:
            with ui.menu().props('no-parent-event') as to_menu:
                ui.date(mask='YYYY-MM-DD').bind_value(time_to_input)
            with time_to_input.add_slot('append'):
                ui.icon('edit_calendar').on('click', to_menu.open).classes('cursor-pointer')

        def _on_clear():
            dialog.close()
            on_apply(None, None)

        def _on_apply():
            dialog.close()
            on_apply(time_from_input.value or None, time_to_input.value or None)

        with ui.row().classes('w-full justify-end gap-2 mt-3'):
            ui.button('清除', on_click=_on_clear).props('flat')
            ui.button('应用', on_click=_on_apply).props('unelevated color=primary')

    return dialog


def build_league_dialog(league_avail, league_sel, on_toggle, on_apply):
    """按联赛检索对话框.

    league_avail / league_sel — 可变 list 包装的状态引用.
    on_toggle(name) — 切换联赛选中状态.
    on_apply(leagues_list) — 应用或清除联赛筛选.
    返回 (dialog, league_opts_refreshable).
    """
    with ui.dialog() as dialog, ui.card().classes('w-[480px]'):
        ui.label('按联赛检索').classes('text-base font-bold text-slate-700 mb-3')

        @ui.refreshable
        def league_opts():
            if not league_avail[0]:
                with ui.row().classes('w-full justify-center py-6'):
                    ui.label('暂无联赛数据').classes('text-xs text-slate-400')
                return
            with ui.row().classes('flex-wrap gap-2 py-1'):
                for opt in league_avail[0]:
                    is_sel = opt in league_sel[0]
                    (ui.button(opt)
                        .props(f'{"unelevated" if is_sel else "outline"} color=primary rounded')
                        .on_click(lambda _, o=opt: on_toggle(o)))

        league_opts()

        def _on_clear():
            dialog.close()
            on_apply([])

        def _on_apply():
            dialog.close()
            on_apply(list(league_sel[0]))

        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('清除', on_click=_on_clear).props('flat')
            ui.button('应用', on_click=_on_apply).props('unelevated color=primary')

    return dialog, league_opts


def build_team_dialog(team_avail, team_sel, team_search_query, on_toggle, on_apply):
    """按球队检索对话框.

    team_avail / team_sel / team_search_query — 可变 list 包装的状态引用.
    on_toggle(name) — 切换球队选中状态.
    on_apply(teams_list, role) — 应用或清除球队筛选.
    返回 (dialog, team_opts_refreshable, search_input, role_toggle).
    """
    with ui.dialog() as dialog, ui.card().classes('w-[520px]'):
        ui.label('按球队检索').classes('text-base font-bold text-slate-700 mb-2')

        search_input = ui.input(placeholder='搜索球队…') \
            .props('outlined dense clearable').classes('w-full')

        with ui.scroll_area().classes('w-full h-56 mt-2'):
            @ui.refreshable
            def team_opts():
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
                            .on_click(lambda _, o=opt: on_toggle(o)))

            team_opts()

        def _on_team_search(e):
            team_search_query[0] = e.value or ''
            team_opts.refresh()

        search_input.on_value_change(_on_team_search)

        with ui.column().classes('w-full gap-0.5 mt-3'):
            ui.label('检索范围').classes('text-xs text-slate-400')
            role_toggle = ui.toggle(
                {'both': '全部', 'home': '仅主队', 'away': '仅客队'},
                value='both',
            ).props('size=sm')

        def _on_clear():
            dialog.close()
            on_apply([], 'both')

        def _on_apply():
            dialog.close()
            on_apply(list(team_sel[0]), role_toggle.value)

        with ui.row().classes('w-full justify-end gap-2 mt-3'):
            ui.button('清除', on_click=_on_clear).props('flat')
            ui.button('应用', on_click=_on_apply).props('unelevated color=primary')

    return dialog, team_opts, search_input, role_toggle


def build_odds_dialog(on_apply):
    """按赔率检索对话框.

    on_apply(odds_type, min_val, max_val) — 应用筛选; odds_type=None 为清除.
    返回 dialog.
    """
    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label('按赔率检索').classes('text-base font-bold text-slate-700 mb-1')
        odds_type_select = ui.select(options=ODDS_OPTIONS, label='赔率类型') \
            .classes('w-full').props('outlined dense')
        with ui.row().classes('w-full gap-2 mt-2'):
            odds_min_input = ui.number('最小值', format='%.2f') \
                .classes('flex-1').props('outlined dense clearable')
            odds_max_input = ui.number('最大值', format='%.2f') \
                .classes('flex-1').props('outlined dense clearable')

        def _on_clear():
            dialog.close()
            on_apply(None)

        def _on_apply():
            dialog.close()
            on_apply(odds_type_select.value, odds_min_input.value, odds_max_input.value)

        with ui.row().classes('w-full justify-end gap-2 mt-3'):
            ui.button('清除', on_click=_on_clear).props('flat')
            ui.button('应用', on_click=_on_apply).props('unelevated color=primary')

    return dialog
