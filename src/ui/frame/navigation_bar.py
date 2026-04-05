from nicegui import ui
from src.ui.router import Router

NAV_ITEMS = [
    ('match_list', 'sports_soccer', '赛事列表'),
    ('analysis',   'query_stats',   '数据分析'),
    ('info',       'info',          '关于'),
]

BOTTOM_ITEMS = [
    ('settings', 'settings', '设置'),
]


def render(router: Router):
    buttons: dict = {}

    def set_active(key: str):
        for k, b in buttons.items():
            if k == key:
                b.classes(remove='!bg-gray-100 !text-gray-500', add='!bg-blue-100 !text-blue-600')
            else:
                b.classes(remove='!bg-blue-100 !text-blue-600', add='!bg-gray-100 !text-gray-500')

    def make_button(key: str, icon: str, label: str):
        with ui.element('div').classes('w-full'):
            btn = ui.button(
                icon=icon,
                on_click=lambda k=key: router.navigate(k),
            ).classes('w-full !bg-gray-100 !text-gray-500 rounded-lg') \
                .props('unelevated')
            with btn:
                ui.tooltip(label).props('anchor="center right" self="center left" :offset="[8, 0]"')
            buttons[key] = btn

    with ui.column().classes('w-14 h-full bg-gray-100 p-2 gap-2 items-center'):
        with ui.column().classes('w-full flex-1 items-center gap-2'):
            for key, icon, label in NAV_ITEMS:
                make_button(key, icon, label)

        with ui.column().classes('w-full items-center'):
            for key, icon, label in BOTTOM_ITEMS:
                make_button(key, icon, label)

    router.on_navigate(set_active)
