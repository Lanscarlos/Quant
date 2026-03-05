from nicegui import ui
# from src.ui import match_panel
from src.ui import navigation_bar

PORT = 19193
NAME = "Quant"
ICON = "assets/icon.ico"
SIZE = (1080, 720)


@ui.page('/')
def index():
    # 关键：让页面自身没有内边距，且铺满全屏
    ui.query('body').style('margin: 0; padding: 0; height: 100vh; background-color: #f8fafc')
    ui.query('.nicegui-content').classes('h-full p-0')

    with ui.row().classes('w-full h-screen gap-0'):
        # 左侧导航栏
        with ui.column().classes('w-16 h-full bg-gray-100 px-1 py-2 gap-1 items-center'):
            with ui.column().classes('flex-1'):
                ui.button(
                    icon='home',
                    on_click=lambda: ui.notify('首页')
                ).classes('w-12 h-12 !bg-gray-100 !text-gray-500') \
                .props('unelevated')

                ui.button(
                    icon='info',
                    color='gray-200',
                    on_click=lambda: ui.notify('关于')
                ).classes('w-12 h-12 !bg-gray-100 !text-gray-500') \
                .props('unelevated')

            with ui.column():
                ui.button(
                    icon='settings',
                    color='gray-200',
                    on_click=lambda: ui.notify('设置')
                ).classes('w-12 h-12 !bg-gray-100 !text-gray-500') \
                    .props('unelevated')

        # 右侧主面板
        with ui.column().classes('flex-1 h-full p-6 gap-4'):
            ui.label('📋 主面板').classes('text-2xl font-bold')
            ui.separator()
            ui.label('这里是主要内容区域')
