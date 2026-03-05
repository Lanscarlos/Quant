from nicegui import ui

def render():
    with ui.column().classes('w-48 h-full p-4 gap-2'):
        with ui.column().classes('flex-1'):
            ui.button(
                icon='home',
                text='首页',
                on_click=lambda: ui.notify('首页')
            ).classes('w-full !bg-gray-100 !text-gray-500') \
                .props('unelevated')

            ui.button(
                icon='info',
                text='首页',
                color='gray-200',
                on_click=lambda: ui.notify('关于')
            ).classes('w-full !bg-gray-100 !text-gray-500') \
                .props('unelevated')

        with ui.column():
            ui.button(
                icon='settings',
                text='设置',
                color='gray-200',
                on_click=lambda: ui.notify('设置')
            ).classes('w-full !bg-gray-100 !text-gray-500') \
                .props('unelevated')
