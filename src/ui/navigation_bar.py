from nicegui import ui

def render(panels_ref: list):
    with ui.column().classes('w-48 h-full bg-gray-100 p-2 gap-2'):
        with ui.column().classes('w-full flex-1'):
            ui.label('Quant').classes('px-4 py-2 text-2xl font-medium text-blue-500')

            ui.button(
                icon='home',
                text='首页',
                on_click=lambda: panels_ref[0].set_value('home')
            ).classes('w-full !bg-gray-100 !text-gray-500 rounded-lg') \
                .props('unelevated align=left')

            ui.button(
                icon='info',
                text='关于',
                color='gray-200',
                on_click=lambda: panels_ref[0].set_value('info')
            ).classes('w-full !bg-gray-100 !text-gray-500 rounded-lg') \
                .props('unelevated align=left')

        with ui.column().classes('w-full'):
            ui.button(
                icon='settings',
                text='设置',
                color='gray-200',
                on_click=lambda: panels_ref[0].set_value('settings')
            ).classes('w-full !bg-gray-100 !text-gray-500 rounded-lg') \
                .props('unelevated align=left')
