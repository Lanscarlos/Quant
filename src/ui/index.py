from nicegui import ui
from src.ui.frame import navigation_bar
from src.ui.panel import home, info
from src.ui.page import dashboard, match_list
from src.ui.page.fetch import index as fetch_index
from src.ui.page.conclusion import index as conclusion_index
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

    # 用 holder 打破初始化顺序依赖：render 回调在 mount 之前定义，
    # 但 trigger 在 mount 之后才能拿到。
    _fetch_trigger: list = [None]
    _conclusion_trigger: list = [None]

    def _on_match_click(mid):
        router.navigate('fetch')
        if _fetch_trigger[0]:
            _fetch_trigger[0](mid)

    def _on_fetch_complete(mid):
        router.navigate('conclusion')
        if _conclusion_trigger[0]:
            _conclusion_trigger[0](mid)

    router.add('match_list',   lambda: match_list.render(on_match_click=_on_match_click))
    router.add('fetch',        lambda: fetch_index.render(on_complete=_on_fetch_complete))
    router.add('conclusion',   conclusion_index.render)
    router.add('info',         info.render)
    router.add('settings',     lambda: ui.label('⚙️ 设置页').classes('text-2xl'))

    with ui.row().classes('w-full h-screen gap-0'):
        navigation_bar.render(router)
        ui.separator().props('vertical')
        router.mount()

    _fetch_trigger[0] = router.get_api('fetch')
    _conclusion_trigger[0] = router.get_api('conclusion')

    router.navigate('match_list')
