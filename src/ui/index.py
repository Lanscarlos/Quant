from nicegui import ui
from src.ui.frame import navigation_bar
from src.ui.panel import home, info
from src.ui.page import dashboard, match_list, match_detail
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

    def _go_to_detail(mid: int):
        match_detail.load(mid)
        router.navigate('match_detail')

    router.add('match_list',   lambda: match_list.render(on_match_click=_go_to_detail))
    router.add('match_detail', lambda: match_detail.render(on_back=lambda: router.navigate('match_list')))
    router.add('info',         info.render)
    router.add('settings',     lambda: ui.label('⚙️ 设置页').classes('text-2xl'))

    with ui.row().classes('w-full h-screen gap-0'):
        navigation_bar.render(router)
        ui.separator().props('vertical')
        router.mount()

    router.navigate('match_list')
