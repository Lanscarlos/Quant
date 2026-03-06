from nicegui import ui
from src.ui.frame import navigation_bar
from src.ui.panel import home, info

PORT = 19193
NAME = "Quant"
ICON = "assets/icon.ico"
SIZE = (1080, 720)

@ui.page('/')
def render():
    # 关键：让页面自身没有内边距，且铺满全屏
    ui.query('body').style('margin: 0; padding: 0; height: 100vh; background-color: #f8fafc')
    ui.query('.nicegui-content').classes('h-full p-0')

    with ui.row().classes('w-full h-screen gap-0'):
        panels_ref = [None]
        navigation_bar.render(panels_ref)
        ui.separator().props('vertical')

        panels = ui.tab_panels(value='home') \
            .props('animated transition-prev=slide-down transition-next=slide-up') \
            .classes('flex-1 h-full bg-gray-100 p-6 gap-4')
        panels_ref[0] = panels

        with panels:
            with ui.tab_panel('home'):
                home.render()

            with ui.tab_panel('info'):
                info.render()

            with ui.tab_panel('settings'):
                ui.label('⚙️ 设置页').classes('text-2xl')
                ui.button('← 返回', on_click=lambda: panels.set_value('home'))
