"""
赛事详情页 — 用户手动输入赛事 URL 或 ID，步进抓取数据，结论步展示结果.

External API:
  render() — registered with the Router
"""
import re

from nicegui import ui

from . import conclusion, step_asian_odds, step_euro_odds, step_h2h, step_match_info

_STEPS = [step_match_info, step_h2h, step_euro_odds, step_asian_odds]

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
        'mid':      None,
        'statuses': {s.KEY: 'pending' for s in _STEPS},
        'messages': {s.KEY: ''        for s in _STEPS},
    }

    def _reset():
        state.update(running=False, abort=False, mid=None)
        state['statuses'] = {s.KEY: 'pending' for s in _STEPS}
        state['messages'] = {s.KEY: ''        for s in _STEPS}

    # ── 布局 ──────────────────────────────────────────────────────────────────
    with ui.column().classes('w-full h-full gap-0'):

        # 顶部：输入框 + 按钮
        with ui.row().classes('w-full items-center gap-3 shrink-0 px-4 pt-4 pb-2'):
            match_input = (
                ui.input(placeholder='输入赛事 URL 或 ID，如 https://zq.titan007.com/analysis/2907948sb.htm')
                .classes('flex-1')
                .props('outlined dense clearable')
            )
            fetch_btn = ui.button('抓取数据', icon='download').props('unelevated color=primary')
            stop_btn  = (
                ui.button('中断', icon='stop')
                .props('unelevated color=negative')
                .classes('hidden')
            )

        # Tabs 导航
        with ui.tabs().classes('w-full shrink-0') as tabs:
            ui.tab('stepper', label='抓取进度', icon='hourglass_top')
            ui.tab('conclusion', label='结论', icon='emoji_events')

        ui.separator().classes('m-0')

        # Tab 面板
        with ui.tab_panels(tabs, value='stepper').classes('flex-1 w-full overflow-auto'):

            # ── 抓取进度 tab ──────────────────────────────────────────────
            with ui.tab_panel('stepper').classes('p-4'):
                with ui.stepper(value=_STEPS[0].KEY).props('vertical animated').classes('w-full') as stepper:
                    refresh_fns: dict = {}

                    for step in _STEPS:
                        with ui.step(step.KEY, title=step.LABEL, icon=step.ICON):

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

                            refresh_fns[step.KEY] = _make_status(step.KEY)

            # ── 结论 tab ──────────────────────────────────────────────────
            with ui.tab_panel('conclusion').classes('p-4'):

                @ui.refreshable
                def conclusion_body():
                    mid = state['mid']
                    if not mid:
                        with ui.row().classes('items-center gap-2 py-4 text-gray-400'):
                            ui.icon('info_outline').classes('text-base')
                            ui.label('完成抓取后自动展示结论').classes('text-sm')
                        return
                    conclusion.render(mid)

                conclusion_body()

    # ── 事件处理 ──────────────────────────────────────────────────────────────

    def _update(key: str, status: str, msg: str = '') -> None:
        state['statuses'][key] = status
        state['messages'][key] = msg
        refresh_fns[key].refresh()

    def _parse_mid(raw: str) -> str | None:
        """从 URL 或纯数字中提取赛事 ID."""
        raw = raw.strip()
        m = re.search(r'/(\d+)sb\.htm', raw)
        if m:
            return m.group(1)
        if raw.isdigit():
            return raw
        return None

    async def _run_fetch() -> None:
        raw = (match_input.value or '').strip()
        mid_str = _parse_mid(raw)
        if not mid_str:
            ui.notify('请输入有效的赛事 URL 或 ID', type='warning')
            return

        _reset()
        for s in _STEPS:
            refresh_fns[s.KEY].refresh()
        conclusion_body.refresh()

        state.update(running=True, mid=int(mid_str))
        fetch_btn.disable()
        stop_btn.classes(remove='hidden')
        tabs.set_value('stepper')
        stepper.set_value(_STEPS[0].KEY)

        for step in _STEPS:
            if state['abort']:
                _update(step.KEY, 'stopped')
                continue

            stepper.set_value(step.KEY)
            _update(step.KEY, 'running')

            try:
                await step.fetch(mid_str)
                _update(step.KEY, 'done')
            except Exception as exc:
                _update(step.KEY, 'error', str(exc)[:80])
                state['abort'] = True

        fetch_btn.enable()
        stop_btn.classes(add='hidden')
        state['running'] = False

        # 抓取完成后自动切换到结论 tab
        tabs.set_value('conclusion')
        conclusion_body.refresh()

    fetch_btn.on_click(_run_fetch)
    stop_btn.on_click(lambda: state.update(abort=True))

    def trigger(mid: int | str) -> None:
        """从外部跳入详情页时调用：填入 URL 并自动开始抓取。"""
        url = f"https://zq.titan007.com/analysis/{mid}sb.htm"
        match_input.set_value(url)
        ui.timer(0, _run_fetch, once=True)

    return trigger
