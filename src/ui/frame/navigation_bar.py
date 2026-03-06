from nicegui import ui

NAV_ITEMS = [
    ('home', 'home', '首页'),
    ('info', 'info', '关于'),
]

BOTTOM_ITEMS = [
    ('settings', 'settings', '设置'),
]


def render(panels_ref: list):
    buttons: dict = {}

    def set_active(key: str):
        for k, b in buttons.items():
            if k == key:
                b.classes(remove='!bg-gray-100 !text-gray-500', add='!bg-blue-100 !text-blue-600')
            else:
                b.classes(remove='!bg-blue-100 !text-blue-600', add='!bg-gray-100 !text-gray-500')

    def navigate(key: str):
        set_active(key)
        panels_ref[0].set_value(key)

    def make_button(key: str, icon: str, label: str):
        btn = ui.button(
            icon=icon,
            text=label,
            on_click=lambda k=key: navigate(k),
        ).classes('w-full !bg-gray-100 !text-gray-500 rounded-lg') \
            .props('unelevated align=left')
        buttons[key] = btn

    with ui.column().classes('w-48 h-full bg-gray-100 p-2 gap-2'):
        with ui.column().classes('w-full flex-1'):
            ui.label('Quant').classes('px-4 py-2 text-2xl font-medium text-blue-500')
            for key, icon, label in NAV_ITEMS:
                make_button(key, icon, label)

        with ui.column().classes('w-full'):
            for key, icon, label in BOTTOM_ITEMS:
                make_button(key, icon, label)

    set_active('home')
