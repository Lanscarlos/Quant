from nicegui import ui
from src.ui.frame import navigation_bar
from src.ui.panel import home, info
from src.ui.page import dashboard
from src.ui.router import Router

PORT = 19193
NAME = "Quant"
ICON = "assets/icon.ico"
SIZE = (1080, 720)


@ui.page('/')
def render():
    ui.query('body').style('margin: 0; padding: 0; height: 100vh; background-color: #f8fafc')
    ui.query('.nicegui-content').classes('h-full p-0')

    router = Router()
    router.add('home', home.render)
    router.add('info', info.render)
    router.add('dashboard', dashboard.render)
    router.add('settings', lambda: ui.label('⚙️ 设置页').classes('text-2xl'))

    with ui.row().classes('w-full h-screen gap-0'):
        navigation_bar.render(router)
        ui.separator().props('vertical')
        router.mount()

    router.navigate('home')
