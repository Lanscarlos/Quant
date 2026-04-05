"""
分析页面 — 自动步进数据抓取流程.

External API:
  render() — registered with the Router
"""
from nicegui import ui, run

from src.service.archived.match_detail import fetch_match_detail
from src.service.archived.match_odds_list import fetch_match_odds_list
from src.service.archived.match_asian_handicap_list import fetch_match_asian_handicap_list

from ._formatters import _d
from ._queries import _query_match, _query_header_extras, _query_h2h, _query_odds
from ._renderers import _render_h2h_section, _render_odds_section, _no_data_hint, _wdl_badges

# ── 步骤定义 ──────────────────────────────────────────────────────────────────
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
        'mid':      None,
        'statuses': {k: 'pending' for k, _, _ in _STEPS},
        'messages': {k: ''        for k, _, _ in _STEPS},
    }

    def _reset():
        state.update(running=False, abort=False, mid=None)
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

                    # 结论步骤：独立的 refreshable 区域
                    if key == 'conclusion':
                        ui.separator().classes('my-2')

                        @ui.refreshable
                        def conclusion_body():
                            mid = state['mid']
                            if not mid:
                                with ui.row().classes('items-center gap-2 py-4 text-gray-400'):
                                    ui.icon('info_outline').classes('text-base')
                                    ui.label('完成抓取后自动展示结论').classes('text-sm')
                                return

                            match = _query_match(mid)
                            if not match:
                                ui.label('未找到赛事数据').classes('text-sm text-slate-400')
                                return

                            extras = _query_header_extras(mid)
                            h2h    = _query_h2h(mid)
                            odds   = _query_odds(mid)

                            with ui.column().classes('w-full gap-0'):

                                # ── 赛事头部 ─────────────────────────────────
                                with ui.row().classes('w-full items-center py-2'):
                                    # 主队
                                    with ui.column().classes('flex-1 gap-0'):
                                        ui.label(match['home_team']).classes(
                                            'text-lg font-bold text-blue-700'
                                        )
                                        with ui.row().classes('items-center gap-3'):
                                            with ui.row().classes('items-center gap-1'):
                                                ui.label('排名').classes('text-xs text-slate-400')
                                                ui.label(_d(match['home_rank'])).classes(
                                                    'text-xs font-bold text-slate-600'
                                                )
                                            with ui.row().classes('items-center gap-1'):
                                                ui.label('积分').classes('text-xs text-slate-400')
                                                ui.label(_d(extras.get('home_pts'))).classes(
                                                    'text-xs font-bold text-slate-600'
                                                )
                                            if extras.get('home_wdl'):
                                                _wdl_badges(*extras['home_wdl'])

                                    # 比分 / 时间 / 联赛
                                    with ui.column().classes('px-4 items-center gap-0 flex-shrink-0'):
                                        hs, as_ = match['home_score'], match['away_score']
                                        if hs is not None:
                                            ui.label(f'{hs}  :  {as_}').classes(
                                                'text-2xl font-bold text-slate-800'
                                            )
                                            hhs, ahs = match['home_half_score'], match['away_half_score']
                                            if hhs is not None:
                                                ui.label(f'半场 {hhs}:{ahs}').classes(
                                                    'text-xs text-slate-400'
                                                )
                                        else:
                                            ui.label('VS').classes('text-2xl font-bold text-slate-300')
                                        ui.label(match['match_time'] or '').classes(
                                            'text-xs text-slate-400 mt-1'
                                        )
                                        ui.label(match['league']).classes('text-xs text-slate-500')

                                    # 客队
                                    with ui.column().classes('flex-1 items-end gap-0'):
                                        ui.label(match['away_team']).classes(
                                            'text-lg font-bold text-red-600 text-right'
                                        )
                                        with ui.row().classes('items-center gap-3'):
                                            if extras.get('away_wdl'):
                                                _wdl_badges(*extras['away_wdl'])
                                            with ui.row().classes('items-center gap-1'):
                                                ui.label('积分').classes('text-xs text-slate-400')
                                                ui.label(_d(extras.get('away_pts'))).classes(
                                                    'text-xs font-bold text-slate-600'
                                                )
                                            with ui.row().classes('items-center gap-1'):
                                                ui.label('排名').classes('text-xs text-slate-400')
                                                ui.label(_d(match['away_rank'])).classes(
                                                    'text-xs font-bold text-slate-600'
                                                )

                                ui.separator().classes('my-2')

                                # ── 近六场交手 ───────────────────────────────
                                with ui.row().classes(
                                    'w-full gap-0 items-start border border-slate-200 rounded'
                                ):
                                    _render_h2h_section(h2h, fetched=True, border_right=False)

                                ui.separator().classes('my-2')

                                # ── 欧赔：威廉希尔 + 立博 ────────────────────
                                with ui.row().classes(
                                    'w-full gap-0 items-start border border-slate-200 rounded'
                                ):
                                    _render_odds_section(
                                        odds, '威廉希尔', 'William Hill', border_right=True
                                    )
                                    _render_odds_section(
                                        odds, '立博', 'Ladbrokes', border_right=False
                                    )

                        conclusion_body()

    # ── 事件处理 ──────────────────────────────────────────────────────────────

    def _update(key: str, status: str, msg: str = '') -> None:
        state['statuses'][key] = status
        state['messages'][key] = msg
        refresh_fns[key].refresh()

    async def _do_step(key: str, mid: str) -> None:
        if key == 'match_detail':
            await run.io_bound(fetch_match_detail, mid)
        elif key == 'h2h':
            pass  # TODO: 待下一步指示
        elif key == 'euro_odds':
            await run.io_bound(fetch_match_odds_list, mid)
        elif key == 'asian_odds':
            await run.io_bound(fetch_match_asian_handicap_list, mid)

    async def _run_fetch() -> None:
        mid_str = (match_input.value or '').strip()
        if not mid_str:
            ui.notify('请输入赛事 ID', type='warning')
            return

        _reset()
        for k, _, _ in _STEPS:
            refresh_fns[k].refresh()
        conclusion_body.refresh()

        state.update(running=True, mid=int(mid_str))
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
                await _do_step(key, mid_str)
                _update(key, 'done')
            except Exception as exc:
                _update(key, 'error', str(exc)[:80])
                state['abort'] = True

        stepper.set_value('conclusion')
        conclusion_body.refresh()
        fetch_btn.enable()
        stop_btn.classes(add='hidden')
        state['running'] = False

    fetch_btn.on_click(_run_fetch)
    stop_btn.on_click(lambda: state.update(abort=True))