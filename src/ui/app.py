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
    ui.add_head_html("""
    <style>
    @keyframes slideIn {
      from { opacity: 0; transform: translateX(-20px); }
      to   { opacity: 1; transform: translateX(0); }
    }
    .animated { animation: slideIn 0.4s ease; }
    </style>
    """)
    # 关键：让页面自身没有内边距，且铺满全屏
    ui.query('body').style('margin: 0; padding: 0; height: 100vh; background-color: #f8fafc')
    ui.query('.nicegui-content').classes('h-full p-0')
    with ui.row().classes('w-full h-screen gap-0'):
        navigation_bar.render()
        ui.separator().props('vertical')

        container = ui.column().classes('flex-1 h-full bg-gray-100 p-6 gap-4')
        ui.timer(0.05, lambda: ui.run_javascript(
            f'document.getElementById("c{container.id}").classList.add("animated")'
        ), once=True)

        def render():
            with container:
                home.render()

        ui.timer(0.1, lambda: render(), once=True)

@ui.page('/test')
def page_test():
    ui.add_head_html("""
    <style>
    @keyframes slideIn {
      from { opacity: 0; transform: translateX(-20px); }
      to   { opacity: 1; transform: translateX(0); }
    }
    .animated { animation: slideIn 0.4s ease; }
    </style>
    """)
    # 关键：让页面自身没有内边距，且铺满全屏
    ui.query('body').style('margin: 0; padding: 0; height: 100vh; background-color: #f8fafc')
    ui.query('.nicegui-content').classes('h-full p-0')
    with ui.row().classes('w-full h-screen gap-0'):
        navigation_bar.render()
        ui.separator().props('vertical')

        container = ui.column().classes('flex-1 h-full bg-gray-100 p-6 gap-4')
        ui.timer(0.05, lambda: ui.run_javascript(
            f'document.getElementById("c{container.id}").classList.add("animated")'
        ), once=True)

        def render():
            with container:
                test.render()

        ui.timer(0.1, lambda: render(), once=True)

