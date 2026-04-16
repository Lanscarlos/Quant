"""历史数据页 — 筛选对话框构建器."""

import asyncio
import datetime as dt
from pathlib import Path

from nicegui import run, ui

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


def build_export_dialog(on_confirm):
    """导出数据对话框.

    on_confirm(scope, fmt, save_path) — 用户点击导出后回调（普通 callable）.
        scope:     'filtered' | 'all'
        fmt:       'csv' | 'json'
        save_path: str — 用户选择的保存路径
    返回 dialog.
    """
    with ui.dialog() as dialog, ui.card().classes('w-[460px]'):
        ui.label('导出数据').classes('text-base font-bold text-slate-700 mb-1')

        # ── 导出范围 ──────────────────────────────────────────────────
        with ui.column().classes('w-full gap-0.5 mt-2'):
            ui.label('导出范围').classes('text-xs text-slate-400')
            scope_toggle = ui.toggle(
                {'filtered': '当前筛选结果', 'all': '全部数据'},
                value='filtered',
            ).props('size=sm')

        # ── 导出格式 ──────────────────────────────────────────────────
        with ui.column().classes('w-full gap-0.5 mt-3'):
            ui.label('导出格式').classes('text-xs text-slate-400')
            fmt_toggle = ui.toggle(
                {'csv': 'CSV（查看用）', 'json': 'JSON（数据迁移）'},
                value='csv',
            ).props('size=sm')

        # 格式说明（随格式切换联动）
        notice = ui.label('').classes('text-xs font-medium mt-1')

        # ── 保存位置 ──────────────────────────────────────────────────
        with ui.column().classes('w-full gap-0.5 mt-3'):
            ui.label('保存位置').classes('text-xs text-slate-400')
            with ui.row().classes('w-full gap-2 items-center'):
                path_input = ui.input(placeholder='请先点击浏览选择保存路径…') \
                    .props('outlined dense readonly').classes('flex-1')
                browse_btn = ui.button('浏览', icon='folder_open').props('outline size=sm')

        # ── 回调定义（在所有 UI 元素定义完后绑定，避免引用顺序问题） ──

        def _update_notice(fmt, clear_path=True):
            """切换格式时更新说明提示，并可选清空已选路径（防止扩展名不匹配）."""
            if clear_path:
                path_input.set_value('')
            if fmt == 'csv':
                notice.set_text('⚠ 仅用于在 Excel / WPS 中查看，不支持导回应用')
                notice.classes(remove='text-blue-700', add='text-amber-700')
            else:
                notice.set_text('ℹ 含完整快照数据，用于在另一台电脑上导入数据，不适合直接查看')
                notice.classes(remove='text-amber-700', add='text-blue-700')

        _update_notice('csv', clear_path=False)  # 初始提示，不清路径
        fmt_toggle.on_value_change(lambda e: _update_notice(e.value))

        async def _on_browse():
            ext = 'json' if fmt_toggle.value == 'json' else 'csv'
            ts = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
            default_name = f'history_export_{ts}.{ext}'

            def _open_save_dialog() -> str:
                """在线程池中打开系统原生保存对话框（避免阻塞事件循环）."""
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                root.wm_attributes('-topmost', True)  # 置顶，防止被遮挡
                label_cn = 'JSON 文件' if ext == 'json' else 'CSV 文件'
                path = filedialog.asksaveasfilename(
                    parent=root,
                    initialdir=str(Path.home() / 'Desktop'),
                    initialfile=default_name,
                    defaultextension=f'.{ext}',
                    filetypes=[(label_cn, f'*.{ext}'), ('所有文件', '*.*')],
                )
                root.destroy()
                return path or ''

            try:
                path = await run.io_bound(_open_save_dialog)
            except Exception as e:
                ui.notify(f'文件对话框出错：{e}', type='negative')
                return
            if path:
                path_input.set_value(path)

        browse_btn.on_click(_on_browse)

        async def _on_confirm():
            if not path_input.value:
                ui.notify('请先点击浏览选择保存路径', type='warning')
                return
            dialog.close()
            result = on_confirm(scope_toggle.value, fmt_toggle.value, path_input.value)
            # 兼容 on_confirm 为协程函数（async def）的情况，确保在当前 client 上下文内 await
            if asyncio.iscoroutine(result):
                await result

        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('取消', on_click=dialog.close).props('flat')
            ui.button('导出', on_click=_on_confirm).props('unelevated color=primary')

    return dialog


def build_import_dialog(on_confirm):
    """导入数据对话框.

    on_confirm(file_path) — 用户点击导入后回调（可为 async def）.
        file_path: str — 用户选择的 JSON 文件路径
    返回 dialog.
    """
    preview_text: list[str] = ['']  # 文件预览信息

    with ui.dialog() as dialog, ui.card().classes('w-[460px]'):
        ui.label('导入数据').classes('text-base font-bold text-slate-700 mb-1')

        # ── 文件选择 ──────────────────────────────────────────────────
        with ui.column().classes('w-full gap-0.5 mt-2'):
            ui.label('JSON 文件').classes('text-xs text-slate-400')
            with ui.row().classes('w-full gap-2 items-center'):
                path_input = ui.input(placeholder='请先点击浏览选择文件…') \
                    .props('outlined dense readonly').classes('flex-1')
                browse_btn = ui.button('浏览', icon='folder_open').props('outline size=sm')

        # ── 文件预览 ──────────────────────────────────────────────────
        preview_label = ui.label('').classes('text-xs text-slate-500 mt-1 min-h-[1.2em]')

        # ── 提示信息 ──────────────────────────────────────────────────
        ui.label('⚠ 已存在的相同赛事将被覆盖') \
            .classes('text-xs font-medium text-amber-700 mt-2')

        # ── 回调定义 ──────────────────────────────────────────────────

        async def _on_browse():
            def _open_dialog() -> str:
                """在线程池中打开系统原生文件选择对话框."""
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.withdraw()
                root.wm_attributes('-topmost', True)
                path = filedialog.askopenfilename(
                    parent=root,
                    initialdir=str(Path.home() / 'Desktop'),
                    filetypes=[('JSON 文件', '*.json'), ('所有文件', '*.*')],
                )
                root.destroy()
                return path or ''

            try:
                path = await run.io_bound(_open_dialog)
            except Exception as e:
                ui.notify(f'文件对话框出错：{e}', type='negative')
                return
            if not path:
                return

            path_input.set_value(path)

            # 读取文件顶层元信息生成预览
            def _read_preview() -> str:
                import json as _json
                try:
                    text = Path(path).read_text(encoding='utf-8')
                    data = _json.loads(text)
                    count = data.get('record_count', len(data.get('records', [])))
                    exported_at = data.get('exported_at', '未知')
                    return f'共 {count} 条记录，导出于 {exported_at}'
                except Exception as ex:
                    return f'无法读取文件预览：{ex}'

            preview = await run.io_bound(_read_preview)
            preview_label.set_text(preview)

        browse_btn.on_click(_on_browse)

        async def _on_confirm():
            if not path_input.value:
                ui.notify('请先点击浏览选择文件', type='warning')
                return
            dialog.close()
            result = on_confirm(path_input.value)
            if asyncio.iscoroutine(result):
                await result

        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('取消', on_click=dialog.close).props('flat')
            ui.button('导入', on_click=_on_confirm).props('unelevated color=primary')

    return dialog


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
