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

    # 全局抓取进度状态，供右下角浮标读取
    _fetch_global = {
        'running':     False,
        'steps_done':  0,
        'steps_total': 6,
        'mid':         None,
        'completed':   False,
    }

    def _on_match_click(mid):
        router.navigate('fetch')
        if _fetch_trigger[0]:
            _fetch_trigger[0](mid)

    def _go_conclusion_with_mid(mid):
        _fetch_global['completed'] = False
        _fetch_badge.refresh()
        router.navigate('conclusion')
        if _conclusion_trigger[0]:
            _conclusion_trigger[0](mid)

    def _on_fetch_complete(mid):
        _fetch_global['completed'] = True
        _fetch_badge.refresh()

        # 用户仍在抓取页 → 沿用自动跳转，流程连贯
        if router.current == 'fetch':
            _go_conclusion_with_mid(mid)
            return

        # 用户已离开抓取页 → 简短提示，导航入口由右下角浮标承担
        ui.notify(
            f'赛事 {mid} 抓取完成',
            type='positive',
            position='top-right',
            timeout=4000,
        )

    def _on_fetch_status_change(running, steps_done, steps_total, mid):
        _fetch_global.update(running=running, steps_done=steps_done,
                             steps_total=steps_total, mid=mid)
        if running:
            _fetch_global['completed'] = False
        _fetch_badge.refresh()

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
    router.add('fetch',        lambda: fetch_index.render(on_complete=_on_fetch_complete, on_status_change=_on_fetch_status_change))
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

    # 右下角全局抓取进度浮标
    @ui.refreshable
    def _fetch_badge():
        is_running   = _fetch_global['running']
        is_completed = _fetch_global['completed']

        if router.current == 'fetch' or (not is_running and not is_completed):
            return

        done  = _fetch_global['steps_done']
        total = _fetch_global['steps_total']
        mid   = _fetch_global['mid']

        if is_running:
            label_text = f'抓取中 {done}/{total}'
            icon_name  = 'hourglass_top'
            color_cls  = 'text-blue-600'
            border_cls = 'border-blue-200'
            on_click   = lambda: router.navigate('fetch')
        else:
            label_text = '抓取完成 · 查看结论'
            icon_name  = 'check_circle'
            color_cls  = 'text-green-600'
            border_cls = 'border-green-200'
            on_click   = lambda: _go_conclusion_with_mid(mid)

        with ui.row().classes(
            f'fixed bottom-4 right-4 items-center gap-1.5 px-3 py-1.5 '
            f'bg-white/95 rounded-full shadow-md border {border_cls} z-50 '
            f'cursor-pointer select-none'
        ).on('click', on_click):
            ui.icon(icon_name).classes(f'text-sm {color_cls}')
            ui.label(label_text).classes(f'text-xs font-medium {color_cls}')

    _fetch_badge()
    router.on_navigate(lambda _: _fetch_badge.refresh())

    _fetch_trigger[0] = router.get_api('fetch')
    _conclusion_trigger[0] = router.get_api('conclusion')
    _match_list_set_interval[0] = router.get_api('match_list')

    router.navigate('match_list')
