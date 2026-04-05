"""
分析页面 — 自动步进数据抓取流程.

External API:
  render() — registered with the Router
"""
from nicegui import ui, run

from src.service.archived.match_detail import fetch_match_detail
from src.service.archived.match_odds_list import fetch_match_odds_list
from src.service.archived.match_asian_handicap_list import fetch_match_asian_handicap_list

# ── 步骤定义 ──────────────────────────────────────────────────────────────────
# (key, material-icon, 显示标题)
_STEPS = [
    ('match_detail', 'search',        '赛事信息 & 联赛比分'),
    ('h2h',          'people',        '两队交手数据'),
    ('euro_odds',    'analytics',     '欧赔数据'),
    ('asian_odds',   'filter_list',   '365 亚盘数据'),
    ('conclusion',   'emoji_events',  '结论'),
]

_FETCH_KEYS = [k for k, _, _ in _STEPS if k != 'conclusion']

_STATUS_ICON = {
    'pending': ('radio_button_unchecked', 'text-gray-300'),
    'running': ('hourglass_top',          'text-blue-500'),
    'done':    ('check_circle',           'text-green-500'),
    'error':   ('cancel',                 'text-red-500'),
    'stopped': ('do_not_disturb_on',      'text-orange-400'),
}

_STATUS_LABEL = {
    'pending': '等待中',
    'running': '抓取中…',
    'done':    '完成',
    'error':   '出错',
    'stopped': '已中断',
}


def render():
    state = {
        'running':  False,
        'abort':    False,
        'statuses': {k: 'pending' for k, _, _ in _STEPS},
        'messages': {k: ''        for k, _, _ in _STEPS},
    }

    def _reset():
        state.update(running=False, abort=False)
        state['statuses'] = {k: 'pending' for k, _, _ in _STEPS}
        state['messages'] = {k: ''        for k, _, _ in _STEPS}

    # ── 布局 ──────────────────────────────────────────────────────────────────
    with ui.column().classes('w-full h-full gap-4'):

        # 顶部：输入框 + 按钮
        with ui.row().classes('w-full items-center gap-3 shrink-0'):
            match_input = (
                ui.input(placeholder='输入赛事 ID')
                .classes('flex-1')
                .props('outlined dense clearable')
            )
            fetch_btn = ui.button('抓取数据', icon='download').props('unelevated color=primary')
            stop_btn  = (
                ui.button('中断', icon='stop')
                .props('unelevated color=negative')
                .classes('hidden')
            )

        # Stepper
        with ui.stepper(value='match_detail').props('animated').classes('flex-1 w-full') as stepper:
            refresh_fns: dict = {}

            for key, icon, label in _STEPS:
                with ui.step(key, title=label, icon=icon):

                    # 每个 step 的状态显示区域（独立 refreshable，互不影响）
                    def _make_status(k: str):
                        @ui.refreshable
                        def _status():
                            s   = state['statuses'][k]
                            msg = state['messages'][k]
                            ico, cls = _STATUS_ICON[s]
                            with ui.row().classes('items-center gap-2 py-1'):
                                ui.icon(ico).classes(f'{cls} text-lg')
                                ui.label(msg or _STATUS_LABEL[s]).classes('text-sm text-gray-500')
                        _status()
                        return _status

                    refresh_fns[key] = _make_status(key)

                    if key == 'conclusion':
                        ui.separator().classes('my-2')
                        ui.label('结论内容待填充').classes('text-gray-400 text-sm')

    # ── 业务逻辑 ──────────────────────────────────────────────────────────────

    def _update(key: str, status: str, msg: str = '') -> None:
        state['statuses'][key] = status
        state['messages'][key] = msg
        refresh_fns[key].refresh()

    async def _do_step(key: str, mid: str) -> None:
        """执行单步数据抓取。"""
        if key == 'match_detail':
            await run.io_bound(fetch_match_detail, mid)
        elif key == 'h2h':
            pass  # TODO: 待下一步指示
        elif key == 'euro_odds':
            await run.io_bound(fetch_match_odds_list, mid)
        elif key == 'asian_odds':
            await run.io_bound(fetch_match_asian_handicap_list, mid)

    async def _run_fetch() -> None:
        mid = (match_input.value or '').strip()
        if not mid:
            ui.notify('请输入赛事 ID', type='warning')
            return

        # 初始化 UI 状态
        _reset()
        for k, _, _ in _STEPS:
            refresh_fns[k].refresh()
        state['running'] = True
        fetch_btn.disable()
        stop_btn.classes(remove='hidden')
        stepper.set_value('match_detail')

        for key in _FETCH_KEYS:
            if state['abort']:
                _update(key, 'stopped')
                continue

            stepper.set_value(key)
            _update(key, 'running')

            try:
                await _do_step(key, mid)
                _update(key, 'done')
            except Exception as exc:
                _update(key, 'error', str(exc)[:80])
                state['abort'] = True   # 出错后中断后续步骤

        stepper.set_value('conclusion')
        fetch_btn.enable()
        stop_btn.classes(add='hidden')
        state['running'] = False

    fetch_btn.on_click(_run_fetch)
    stop_btn.on_click(lambda: state.update(abort=True))