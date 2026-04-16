"""
历史数据 — 已保存赛事分析页.

Displays user-saved match analysis records.
External API:
  render(on_match_click) — registered with the Router
"""

import asyncio
import random
from pathlib import Path

from nicegui import ui, run

from src.db.repo.history import (
    list_saved_matches, list_distinct_leagues, list_distinct_teams, backfill_h30,
    export_to_json, export_to_csv,
)

from .constants import TABLE_COLS, ODDS_OPTIONS
from .odds_panel import render_odds_panel
from .dialogs import build_time_dialog, build_league_dialog, build_team_dialog, build_odds_dialog, build_export_dialog


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

    # 延迟绑定的 UI 引用，在布局和对话框构建后填充
    _refs: dict = {}

    # ── 核心处理函数 ──────────────────────────────────────────────────

    def _reload():
        filters = active_filters[0] if active_filters[0] else None
        cached_rows[0] = list_saved_matches(filters)
        _refs['data_table'].refresh()
        _refs['filter_chips'].refresh()

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

    def _on_recent10():
        active_filters[0] = {'limit': 10}
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
        _reload()

    def _on_league_toggle(name: str):
        sel = league_sel[0]
        sel.discard(name) if name in sel else sel.add(name)
        _refs['league_opts'].refresh()

    def _on_team_toggle(name: str):
        sel = team_sel[0]
        sel.discard(name) if name in sel else sel.add(name)
        _refs['team_opts'].refresh()

    def _apply_league_filter(leagues: list):
        f = active_filters[0]
        f.pop('limit', None)
        if leagues:
            f['league'] = leagues
        else:
            f.pop('league', None)
        league_sel[0] = set(leagues)
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
        _reload()

    # ── 主布局 ────────────────────────────────────────────────────────

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
            recent10_btn    = ui.button('近十场分析数据', icon='analytics')   .props('outline size=sm')
            time_btn        = ui.button('按时间检索',    icon='access_time')  .props('outline size=sm')
            league_btn      = ui.button('按联赛检索',    icon='emoji_events') .props('outline size=sm')
            team_btn        = ui.button('按球队检索',    icon='group')        .props('outline size=sm')
            odds_btn        = ui.button('按赔率检索',    icon='filter_list')  .props('outline size=sm')
            export_data_btn = ui.button('导出数据',      icon='download')     .props('outline size=sm')
            export_img_btn  = ui.button('另存为图片',    icon='image')        .props('outline size=sm')
            print_btn       = ui.button('检索结果打印',  icon='print')        .props('outline size=sm')
            refresh_btn     = ui.button('刷新',          icon='refresh')      .props('outline size=sm')

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
                    label = ODDS_OPTIONS.get(f['odds_type'], f['odds_type'])
                    lo = f.get('odds_min', '…')
                    hi = f.get('odds_max', '…')
                    ui.chip(f"{label}  {lo}~{hi}", icon='filter_list', removable=True,
                            on_value_change=lambda e: _clear_filter('odds') if not e.value else None) \
                        .props('color=blue-2 text-color=blue-10 size=sm')

                ui.button('重置', icon='clear_all', on_click=_clear_all_filters) \
                    .props('flat dense size=sm color=blue-8').classes('ml-auto')

        filter_chips()
        _refs['filter_chips'] = filter_chips

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
                            ui.table(columns=TABLE_COLS, rows=rows, row_key='id')
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
                    _refs['data_table'] = data_table

                # 底部两个平赔面板
                with ui.row().classes('w-full gap-3 items-start'):
                    for name in ('威廉体系', '立博体系'):
                        render_odds_panel(name)

    async def _on_export(scope: str, fmt: str, save_path: str):
        """导出数据：io_bound 序列化后写入用户已选路径."""
        # ── 确定有效筛选条件 ─────────────────────────────────────────
        if scope == 'all' or not active_filters[0]:
            effective_filters = None
        else:
            # 剥离 limit 键，导出不受条数约束
            effective_filters = {k: v for k, v in active_filters[0].items() if k != 'limit'}

        # ── io_bound 序列化 + 写文件 ──────────────────────────────────
        export_data_btn.props(add='loading disable')
        try:
            if fmt == 'json':
                content = await run.io_bound(export_to_json, effective_filters)
            else:
                content = await run.io_bound(export_to_csv, effective_filters)

            await run.io_bound(lambda: Path(save_path).write_text(content, encoding='utf-8'))
            ui.notify(f'导出成功：{Path(save_path).name}', type='positive')

        except PermissionError:
            ui.notify('无法写入该路径，请检查文件权限', type='negative')
        except Exception as e:
            ui.notify(f'导出失败：{e}', type='negative')
        finally:
            export_data_btn.props(remove='loading disable')

    # ── 筛选对话框 ────────────────────────────────────────────────────

    time_dialog = build_time_dialog(on_apply=_apply_time_filter)

    league_dialog, _league_opts = build_league_dialog(
        league_avail, league_sel, _on_league_toggle, _apply_league_filter,
    )
    _refs['league_opts'] = _league_opts

    team_dialog, _team_opts, team_search_input, team_role_toggle = build_team_dialog(
        team_avail, team_sel, team_search_query, _on_team_toggle, _apply_team_filter,
    )
    _refs['team_opts'] = _team_opts

    odds_dialog = build_odds_dialog(on_apply=_apply_odds_filter)

    export_dialog = build_export_dialog(
        on_confirm=lambda scope, fmt, save_path: asyncio.ensure_future(_on_export(scope, fmt, save_path))
    )

    # ── 对话框打开函数 ────────────────────────────────────────────────

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

    # ── 异步刷新 ─────────────────────────────────────────────────────

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
    export_data_btn.on_click(export_dialog.open)
    export_img_btn.on_click(lambda: ui.notify('另存为图片功能待实现', type='info'))
    print_btn.on_click(lambda: ui.notify('打印功能待实现', type='info'))
    refresh_btn.on_click(_on_refresh)

    # 初始加载（顺带补全旧记录的 h30 数据）
    backfill_h30()
    _reload()
