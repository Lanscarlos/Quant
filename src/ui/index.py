from nicegui import ui
from src.ui.frame import navigation_bar
from src.ui.page import dashboard
from src.ui.page.match_list import index as match_list_index
from src.ui.page.history import index as history_index
from src.ui.page.fetch import index as fetch_index
from src.ui.page.conclusion import index as conclusion_index
from src.ui.page.settings import index as settings_index
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
    # 但 trigger/api 在 mount 之后才能拿到。
    _fetch_trigger: list = [None]
    _conclusion_trigger: list = [None]
    _match_list_set_interval: list = [None]

    def _on_match_click(mid):
        router.navigate('fetch')
        if _fetch_trigger[0]:
            _fetch_trigger[0](mid)

    def _on_fetch_complete(mid):
        router.navigate('conclusion')
        if _conclusion_trigger[0]:
            _conclusion_trigger[0](mid)

    def _on_history_match_click(mid):
        router.navigate('conclusion')
        if _conclusion_trigger[0]:
            _conclusion_trigger[0](mid, source='history')

    def _on_conclusion_back(source):
        if source == 'history':
            router.navigate('history')
        else:
            router.navigate('match_list')

    def _on_conclusion_refetch(mid):
        router.navigate('fetch')
        if _fetch_trigger[0]:
            _fetch_trigger[0](mid, force=True)

    router.add('match_list',   lambda: match_list_index.render(on_match_click=_on_match_click))
    router.add('fetch',        lambda: fetch_index.render(on_complete=_on_fetch_complete))
    router.add('conclusion',   lambda: conclusion_index.render(on_back=_on_conclusion_back, on_refetch=_on_conclusion_refetch))
    router.add('history',      lambda: history_index.render(on_match_click=_on_history_match_click))
    def _on_interval_change(seconds: int):
        if _match_list_set_interval[0]:
            _match_list_set_interval[0](seconds)

    router.add('settings',     lambda: settings_index.render(on_interval_change=_on_interval_change))

    with ui.row().classes('w-full h-screen gap-0'):
        navigation_bar.render(router)
        ui.separator().props('vertical')
        router.mount()

    _fetch_trigger[0] = router.get_api('fetch')
    _conclusion_trigger[0] = router.get_api('conclusion')
    _match_list_set_interval[0] = router.get_api('match_list')

    router.navigate('match_list')
