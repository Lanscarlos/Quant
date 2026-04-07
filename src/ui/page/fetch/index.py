"""
抓取数据页 — 用户手动输入赛事 URL 或 ID，分阶段并行抓取数据.

改进点:
  - 同一 HTML 只请求一次 (步骤 1 合并排名/近期/交手)
  - 同阶段步骤并行执行 (欧赔 & 亚盘、两个历史)
  - 错误隔离: 非依赖步骤失败不影响其他步骤
  - 新鲜度检查: 数据仍然新鲜时自动跳过
  - 步骤间通过 ctx 传递数据 (record_ids, match_year)

External API:
  render() — registered with the Router, returns trigger(mid) callback
"""
import asyncio
import re

from nicegui import ui

from .steps import STEPS, PHASES

_STATUS_ICON = {
    'pending':  ('radio_button_unchecked', 'text-gray-300'),
    'running':  ('hourglass_top',          'text-blue-500'),
    'done':     ('check_circle',           'text-green-500'),
    'skipped':  ('check_circle',           'text-slate-400'),
    'error':    ('cancel',                 'text-red-500'),
    'stopped':  ('do_not_disturb_on',      'text-orange-400'),
}

_STATUS_LABEL = {
    'pending':  '等待中',
    'running':  '抓取中…',
    'done':     '完成',
    'skipped':  '已跳过',
    'error':    '出错',
    'stopped':  '已中断',
}

_CIRCLE_CLS = {
    'pending':  'bg-slate-100 text-slate-400',
    'running':  'bg-blue-100  text-blue-600',
    'done':     'bg-green-100 text-green-600',
    'skipped':  'bg-slate-100 text-slate-500',
    'error':    'bg-red-100   text-red-600',
    'stopped':  'bg-orange-100 text-orange-500',
}


def render(on_complete=None):
    state = {
        'running':  False,
        'abort':    False,
        'mid':      None,
        'statuses': {s.KEY: 'pending' for s in STEPS},
        'messages': {s.KEY: ''        for s in STEPS},
    }

    def _reset():
        state.update(running=False, abort=False, mid=None)
        state['statuses'] = {s.KEY: 'pending' for s in STEPS}
        state['messages'] = {s.KEY: ''        for s in STEPS}

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

        ui.separator().classes('m-0')

        # ── 抓取进度 ─────────────────────────────────────────────────────
        with ui.scroll_area().classes('flex-1 w-full'):
            with ui.column().classes('w-full p-4'):
                refresh_fns: dict = {}
                circle_fns:  dict = {}

                for idx, step in enumerate(STEPS, start=1):

                    def _make_row(k: str, number: int, label: str, icon: str):
                        with ui.row().classes('w-full items-start gap-4'):

                            # 左：编号圆圈 + 连接线
                            with ui.column().classes('items-center gap-0 shrink-0 w-8'):

                                @ui.refreshable
                                def _circle(k=k, n=number):
                                    cls = _CIRCLE_CLS[state['statuses'][k]]
                                    ui.label(str(n)).classes(
                                        f'w-7 h-7 rounded-full {cls} '
                                        'text-xs font-bold flex items-center justify-center'
                                    )

                                _circle()
                                circle_fns[k] = _circle

                                if number < len(STEPS):
                                    ui.element('div').classes('w-px bg-slate-200 mt-1').style('height: 48px')

                            # 右：步骤标题 + 状态
                            with ui.column().classes('flex-1 gap-1 pb-4'):
                                with ui.row().classes('items-center gap-2 h-7'):
                                    ui.icon(icon).classes('text-slate-400 text-base')
                                    ui.label(label).classes('text-sm font-medium text-slate-700')

                                @ui.refreshable
                                def _status(k=k):
                                    s   = state['statuses'][k]
                                    msg = state['messages'][k]
                                    ico, cls = _STATUS_ICON[s]
                                    with ui.row().classes('items-center gap-2'):
                                        ui.icon(ico).classes(f'{cls} text-base')
                                        ui.label(msg or _STATUS_LABEL[s]).classes('text-xs text-gray-500')

                                _status()
                                refresh_fns[k] = _status

                    _make_row(step.KEY, idx, step.LABEL, step.ICON)

    # ── 事件处理 ──────────────────────────────────────────────────────────────

    def _update(key: str, status: str, msg: str = '') -> None:
        state['statuses'][key] = status
        state['messages'][key] = msg
        refresh_fns[key].refresh()
        circle_fns[key].refresh()

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
        for s in STEPS:
            refresh_fns[s.KEY].refresh()
            circle_fns[s.KEY].refresh()

        state.update(running=True, mid=int(mid_str))
        fetch_btn.disable()
        stop_btn.classes(remove='hidden')

        ctx: dict = {}
        failed_keys: set = set()

        for phase in PHASES:
            if state['abort']:
                for step in phase:
                    if state['statuses'][step.KEY] == 'pending':
                        _update(step.KEY, 'stopped')
                continue

            async def _run_step(step) -> None:
                # 检查依赖是否失败
                if step.DEPENDS_ON and any(d in failed_keys for d in step.DEPENDS_ON):
                    _update(step.KEY, 'stopped', '依赖步骤失败，已跳过')
                    return

                if state['abort']:
                    _update(step.KEY, 'stopped')
                    return

                # 新鲜度检查
                skip, msg = step.should_skip(int(mid_str))
                if skip:
                    _update(step.KEY, 'skipped', msg)
                    return

                _update(step.KEY, 'running')

                # 线程安全的进度回调：io_bound 线程调用 → 调度到事件循环更新 UI
                loop = asyncio.get_running_loop()
                key  = step.KEY

                def _on_progress(msg: str) -> None:
                    loop.call_soon_threadsafe(_update, key, 'running', msg)

                try:
                    await step.fetch(mid_str, ctx, _on_progress)
                    _update(step.KEY, 'done')
                except Exception as exc:
                    _update(step.KEY, 'error', str(exc)[:80])
                    failed_keys.add(step.KEY)

            if len(phase) == 1:
                await _run_step(phase[0])
            else:
                await asyncio.gather(*[_run_step(s) for s in phase])

        fetch_btn.enable()
        stop_btn.classes(add='hidden')
        state['running'] = False

        # 只要没有用户中断，即使部分步骤失败也跳转结论页
        if not state['abort'] and on_complete:
            on_complete(state['mid'])

    fetch_btn.on_click(_run_fetch)
    stop_btn.on_click(lambda: state.update(abort=True))

    def trigger(mid: int | str) -> None:
        """从外部跳入时调用：填入 URL 并自动开始抓取。"""
        url = f"https://zq.titan007.com/analysis/{mid}sb.htm"
        match_input.set_value(url)
        ui.timer(0, _run_fetch, once=True)

    return trigger
