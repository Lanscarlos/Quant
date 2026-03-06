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

    # 自定义 slide-fade 组合过渡动画
    ui.add_head_html('''
    <style>
    .q-transition--slide-fade-up-enter-active,
    .q-transition--slide-fade-up-leave-active,
    .q-transition--slide-fade-down-enter-active,
    .q-transition--slide-fade-down-leave-active {
        transition: transform 0.3s ease, opacity 0.3s ease;
    }
    .q-transition--slide-fade-up-enter-from {
        transform: translateY(30px); opacity: 0;
    }
    .q-transition--slide-fade-up-leave-to {
        transform: translateY(-30px); opacity: 0;
    }
    .q-transition--slide-fade-down-enter-from {
        transform: translateY(-30px); opacity: 0;
    }
    .q-transition--slide-fade-down-leave-to {
        transform: translateY(30px); opacity: 0;
    }
    </style>
    ''')

    with ui.row().classes('w-full h-screen gap-0'):
        panels_ref = [None]
        navigation_bar.render(panels_ref)
        ui.separator().props('vertical')

        panels = ui.tab_panels(value='home') \
            .props('animated transition-prev=slide-fade-down transition-next=slide-fade-up') \
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
