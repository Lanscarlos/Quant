from nicegui import ui
from src.ui.frame import navigation_bar
from src.ui.panel import home, info
from src.ui.page import dashboard, match_list
from src.ui.page.detail import index as detail_index
from src.ui.router import Router

PORT = 19193
NAME = "Quant"
ICON = "assets/icon.ico"
SIZE = (1260, 840)


@ui.page('/')
def render():
    ui.query('body').style('margin: 0; padding: 0; height: 100vh; background-color: #f8fafc')
    ui.query('.nicegui-content').classes('h-full p-0')

    router = Router()

    # 用 holder 打破初始化顺序依赖：on_match_click 在 mount 之前定义，
    # 但 detail trigger 在 mount 之后才能拿到。
    _detail_trigger: list = [None]

    def _on_match_click(mid):
        router.navigate('analysis')
        if _detail_trigger[0]:
            _detail_trigger[0](mid)

    router.add('match_list',   lambda: match_list.render(on_match_click=_on_match_click))
    router.add('analysis',     detail_index.render)
    router.add('info',         info.render)
    router.add('settings',     lambda: ui.label('⚙️ 设置页').classes('text-2xl'))

    with ui.row().classes('w-full h-screen gap-0'):
        navigation_bar.render(router)
        ui.separator().props('vertical')
        router.mount()

    _detail_trigger[0] = router.get_api('analysis')

    router.navigate('match_list')
