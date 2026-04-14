"""
设置页面。

External API:
  render(on_interval_change) — 注册到 Router
"""
from nicegui import ui

from src.service.config import get_refresh_interval, set_refresh_interval


def render(on_interval_change: callable = None):
    with ui.column().classes('w-full h-full gap-0'):

        # ── 标题行 ────────────────────────────────────────────────────
        with ui.row().classes(
            'w-full items-center gap-2 px-4 py-2 bg-white border-b border-slate-200'
        ):
            ui.icon('settings').classes('text-xl text-blue-600')
            ui.label('设置').classes('text-base font-bold text-slate-700')

        # ── 内容区 ────────────────────────────────────────────────────
        with ui.scroll_area().classes('w-full flex-1'):
            with ui.column().classes('w-full gap-4 p-4 max-w-xl'):

                # ── 赛事列表设置卡片 ──────────────────────────────────
                with ui.card().classes('w-full').props('flat bordered'):
                    with ui.card_section():
                        ui.label('赛事列表').classes('text-sm font-bold text-slate-600')
                    ui.separator()
                    with ui.card_section():
                        with ui.column().classes('gap-3'):
                            ui.label('自动刷新间隔').classes('text-xs text-slate-500')
                            with ui.row().classes('items-center gap-3'):
                                current_minutes = get_refresh_interval() // 60
                                interval_input = (
                                    ui.number(value=current_minutes, min=1, max=60, step=1)
                                    .props('outlined dense suffix=分钟')
                                    .style('width: 130px')
                                )
                                save_btn = (
                                    ui.button('保存', icon='save')
                                    .props('unelevated color=primary dense')
                                )
                                status_label = ui.label('').classes('text-xs text-green-600')

                            ui.label('范围 1 ~ 60 分钟，默认 5 分钟').classes('text-xs text-slate-400')

                    def _on_save():
                        raw = interval_input.value
                        minutes = max(1, min(60, int(raw or 5)))
                        seconds = minutes * 60
                        set_refresh_interval(seconds)
                        interval_input.set_value(minutes)
                        status_label.set_text('已保存')
                        if on_interval_change:
                            on_interval_change(seconds)
                        ui.timer(2, lambda: status_label.set_text(''), once=True)

                    save_btn.on_click(_on_save)
