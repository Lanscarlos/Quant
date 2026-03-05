from nicegui import ui
# from src.ui import match_panel
from src.ui import navigation_bar
from src.ui.page import home, test

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
        navigation_bar.render()

        ui.separator().props('vertical')

        ui.sub_pages({'/': home.render, '/test': test.render}).classes('flex-1 h-full bg-gray-100 p-6 gap-4')

        # 右侧主面板
        # with ui.column().classes('flex-1 h-full bg-gray-100 p-6 gap-4'):
        #     ui.label('📋 主面板').classes('text-2xl font-bold')
        #     ui.separator()
        #     ui.label('这里是主要内容区域')
