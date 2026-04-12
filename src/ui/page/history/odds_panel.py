"""历史数据页 — 搭配的平赔平局值面板组件."""

from nicegui import ui

from .constants import PANEL_LEAGUES


def render_odds_panel(system_name: str):
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
                for lbl in PANEL_LEAGUES:
                    ui.label(lbl).classes(
                        'flex-1 text-center text-xs text-slate-600 '
                        'py-1 border-r border-slate-200'
                    )
                with ui.row().classes('items-center px-2 gap-0.5'):
                    ui.label('其它').classes('text-xs text-slate-600')
                    ui.icon('expand_more').classes('text-sm text-slate-400')

            with ui.row().classes('w-full border-b border-slate-100'):
                for _ in PANEL_LEAGUES:
                    ui.input(placeholder='点击输入') \
                        .classes('flex-1 text-xs') \
                        .props('dense borderless')
                ui.input(placeholder='输入') \
                    .classes('w-14 text-xs') \
                    .props('dense borderless')

            for _ in range(5):
                with ui.row().classes('w-full border-b border-slate-100'):
                    for _ in range(len(PANEL_LEAGUES) + 1):
                        ui.label('-').classes('flex-1 text-center text-xs text-slate-300 py-1')

            with ui.row().classes('w-full justify-center gap-3 py-2'):
                ui.button('统计平赔', icon='calculate') \
                    .props('outline size=sm') \
                    .on('click', lambda: ui.notify('统计平赔功能待实现', type='info'))
                ui.button('保存数据', icon='save') \
                    .props('outline size=sm') \
                    .on('click', lambda: ui.notify('保存数据功能待实现', type='info'))
