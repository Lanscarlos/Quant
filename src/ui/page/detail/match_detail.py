"""
Match detail page — refactored layout matching 赛事详情-样式图.

Layout:
  [toolbar]
  [主队 name+rank+pts] [比赛类型/时间] [pts+rank+客队 name]
  [主队近六场] | [近六场交手] | [客队近六场]
  [威廉希尔]  | [立博]       | [365亚盘]
  [分析过程 textarea]  [结论 textarea]

External API:
  load(match_id) — call before navigating to this page
  render(on_back) — registered with the Router
"""
import asyncio

from nicegui import ui, run

from src.service.archived.match_asian_handicap_list import fetch_match_asian_handicap_list
from src.service.archived.match_detail import fetch_match_detail
from src.service.archived.match_odds_list import fetch_match_odds_list
from src.sync.coordinator import should_fetch_asian_odds, should_fetch_detail, should_fetch_odds

from ._formatters import _d
from ._queries import (
    _fetch_recent_odds,
    _query_all_sections,
    _query_match,
)
from ._renderers import (
    _render_asian_section,
    _render_h2h_section,
    _render_odds_section,
    _render_recent_section,
    _render_skeleton_3col,
)

_state: dict = {'match_id': None, 'sections': None, 'auto_fetched': False, 'fetching': False}
_refresh_fn: list = [None]


def load(match_id: int | str) -> None:
    """Set current match and trigger page refresh."""
    _state['match_id'] = int(match_id)
    _state['sections'] = None
    _state['auto_fetched'] = False
    _state['fetching'] = False
    if _refresh_fn[0]:
        _refresh_fn[0]()


# ── Main render ────────────────────────────────────────────────────────────────

def render(on_back: callable = None):
    with ui.column().classes('w-full h-full gap-0'):

        # ── 顶部工具栏 ────────────────────────────────────────────────
        with ui.row().classes(
            'w-full items-center gap-1 px-3 py-2 bg-white border-b border-slate-200 flex-wrap'
        ):
            back_btn = ui.button(icon='arrow_back') \
                .props('unelevated round size=xs') \
                .classes('!bg-slate-100 !text-slate-500 mr-1')
            if on_back:
                back_btn.on_click(on_back)

            fetch_btn_1      = ui.button('抓取数据1',    icon='download')    .props('outline size=sm')
            fetch_btn_2      = ui.button('抓取数据2',    icon='bar_chart')   .props('outline size=sm')
            init_btn         = ui.button('数据分析初始',  icon='restart_alt') .props('outline size=sm')
            save_btn         = ui.button('结果保存',     icon='save')         .props('outline size=sm')
            history_load_btn = ui.button('历史数据加载',  icon='history')     .props('outline size=sm')
            history_page_btn = ui.button('历史数据页面',  icon='table_chart') .props('outline size=sm')
            export_img_btn   = ui.button('另存为图片',   icon='image')        .props('outline size=sm')
            print_btn        = ui.button('分析结果打印',  icon='print')       .props('outline size=sm')
            exit_btn         = ui.button('退出',         icon='exit_to_app')  .props('outline size=sm')

            spinner   = ui.spinner(size='sm').classes('hidden ml-2')
            err_label = ui.label('').classes('text-xs text-red-500')

        def _disable_fetch():
            for b in (fetch_btn_1, fetch_btn_2, history_load_btn):
                b.disable()

        def _enable_fetch():
            for b in (fetch_btn_1, fetch_btn_2, history_load_btn):
                b.enable()

        # ── 内容区域 ──────────────────────────────────────────────────
        with ui.scroll_area().classes('w-full flex-1'):

            @ui.refreshable
            def detail_content():
                mid = _state.get('match_id')
                if not mid:
                    with ui.column().classes('w-full items-center py-20 gap-3'):
                        ui.icon('sports_soccer').classes('text-5xl text-slate-300')
                        ui.label('请从赛事列表选择一场比赛').classes('text-slate-400 text-sm')
                    return

                match = _query_match(mid)
                if not match:
                    with ui.column().classes('w-full items-center py-20'):
                        ui.label('未找到比赛数据').classes('text-slate-400 text-sm')
                    return

                sections = _state.get('sections')
                extras   = sections['extras'] if sections else {}
                recent   = sections['recent'] if sections else {}
                h2h      = sections['h2h']    if sections else {'rows': [], 'win': 0, 'draw': 0, 'loss': 0}
                odds     = sections['odds']   if sections else []

                with ui.column().classes('w-full gap-0 p-3'):

                    # ── 行1: 赛事头部 ──────────────────────────────────
                    with ui.row().classes('w-full items-center'):
                        with ui.row().classes('flex-[2] items-center min-w-0'):
                            with ui.row().classes('flex-1 items-center gap-2 min-w-0'):
                                ui.label('主队').classes('text-xs text-slate-400 flex-shrink-0')
                                ui.label(match['home_team']).classes(
                                    'text-xl font-bold text-blue-700 truncate min-w-0'
                                )
                            with ui.row().classes('items-center gap-3 flex-shrink-0 pl-4'):
                                with ui.row().classes('items-center gap-1'):
                                    ui.label('排名').classes('text-xs text-slate-400')
                                    ui.label(_d(match['home_rank'])).classes('text-xs font-bold text-slate-700')
                                with ui.row().classes('items-center gap-1'):
                                    ui.label('积分').classes('text-xs text-slate-400')
                                    ui.label(_d(extras.get('home_pts'))).classes('text-xs font-bold text-slate-700')

                        with ui.row().classes('items-center gap-2 flex-shrink-0 px-6'):
                            ui.label('比赛类型:').classes('text-xs text-slate-500 whitespace-nowrap')
                            ui.label(match['league']).classes('text-xs font-medium text-slate-700 whitespace-nowrap')
                            ui.label('比赛时间:').classes('text-xs text-slate-500 whitespace-nowrap ml-3')
                            ui.label(match['match_time'] or '').classes(
                                'text-xs text-slate-600 whitespace-nowrap'
                            )

                        with ui.row().classes('flex-[2] items-center min-w-0'):
                            with ui.row().classes('items-center gap-3 flex-shrink-0 pr-4'):
                                with ui.row().classes('items-center gap-1'):
                                    ui.label('积分').classes('text-xs text-slate-400')
                                    ui.label(_d(extras.get('away_pts'))).classes('text-xs font-bold text-slate-700')
                                with ui.row().classes('items-center gap-1'):
                                    ui.label('排名').classes('text-xs text-slate-400')
                                    ui.label(_d(match['away_rank'])).classes('text-xs font-bold text-slate-700')
                            with ui.row().classes('flex-1 items-center gap-2 min-w-0 justify-end'):
                                ui.label(match['away_team']).classes(
                                    'text-xl font-bold text-red-600 truncate min-w-0 text-right'
                                )
                                ui.label('客队').classes('text-xs text-slate-400 flex-shrink-0')

                    ui.separator().classes('my-2')

                    # ── 行2: 近六场比赛 + 交手 ─────────────────────────
                    with ui.row().classes('w-full gap-0 items-start border border-slate-200 rounded'):
                        if sections:
                            _render_recent_section(
                                recent.get('home', []), extras.get('home_wdl'),
                                is_home=True, border_right=True
                            )
                            _render_h2h_section(h2h, sections['detail_fetched'], border_right=True)
                            _render_recent_section(
                                recent.get('away', []), extras.get('away_wdl'),
                                is_home=False, border_right=False
                            )
                        else:
                            _render_skeleton_3col()

                    ui.separator().classes('my-2')

                    # ── 行3: 欧赔 + 亚盘 ──────────────────────────────
                    with ui.row().classes('w-full gap-0 items-start border border-slate-200 rounded'):
                        _render_odds_section(odds, '威廉希尔', 'William Hill', border_right=True)
                        _render_odds_section(odds, '立博',     'Ladbrokes',    border_right=True)
                        _render_asian_section(sections['asian_odds'] if sections else None)

                    ui.separator().classes('my-2')

                    # ── 行4: 分析过程 + 结论 ───────────────────────────
                    with ui.row().classes('w-full gap-3'):
                        with ui.column().classes('flex-[3] gap-1'):
                            ui.label('分析过程').classes('text-sm font-semibold text-slate-600')
                            ui.textarea().classes('w-full').props('outlined dense rows=5')
                        with ui.column().classes('flex-[2] gap-1'):
                            ui.label('结论').classes('text-sm font-semibold text-slate-600')
                            ui.textarea().classes('w-full').props('outlined dense rows=5')

                # ── 自动加载逻辑 ──────────────────────────────────────
                if not sections and not _state.get('fetching'):
                    async def _load_sections():
                        data = await run.io_bound(_query_all_sections, mid)
                        _state['sections'] = data
                        detail_content.refresh()
                    ui.timer(0, _load_sections, once=True)

                elif not _state.get('auto_fetched'):
                    async def _auto_fetch():
                        status = match['status']
                        need_detail = should_fetch_detail(mid, status=status)
                        need_odds   = should_fetch_odds(mid, status=status)
                        need_asian  = should_fetch_asian_odds(mid, status=status)
                        if not (need_detail or need_odds or need_asian):
                            _state['auto_fetched'] = True
                            return
                        spinner.classes(remove='hidden')
                        _disable_fetch()
                        _state['fetching'] = True
                        _state['sections'] = None
                        detail_content.refresh()
                        try:
                            coros = []
                            if need_detail:
                                coros.append(run.io_bound(fetch_match_detail, mid))
                            if need_odds:
                                coros.append(run.io_bound(fetch_match_odds_list, mid))
                            if need_asian:
                                coros.append(run.io_bound(fetch_match_asian_handicap_list, mid))
                            if coros:
                                await asyncio.gather(*coros)
                            await run.io_bound(_fetch_recent_odds, mid)
                            _state['auto_fetched'] = True
                            _state['sections'] = await run.io_bound(_query_all_sections, mid)
                            detail_content.refresh()
                        except Exception:
                            _state['auto_fetched'] = True
                            _state['sections'] = await run.io_bound(_query_all_sections, mid)
                            detail_content.refresh()
                        finally:
                            _state['fetching'] = False
                            spinner.classes(add='hidden')
                            _enable_fetch()

                    ui.timer(0, _auto_fetch, once=True)

            _refresh_fn[0] = detail_content.refresh
            detail_content()

    # ── 按钮操作处理 ──────────────────────────────────────────────────

    async def _run_fetch(coro_factories: list, label: str = '抓取'):
        mid = _state.get('match_id')
        if not mid:
            return
        err_label.set_text('')
        spinner.classes(remove='hidden')
        _disable_fetch()
        prev_sections = _state['sections']
        _state['fetching'] = True
        _state['sections'] = None
        detail_content.refresh()
        try:
            if len(coro_factories) > 1:
                await asyncio.gather(*[f() for f in coro_factories])
            else:
                await coro_factories[0]()
            _state['sections'] = await run.io_bound(_query_all_sections, mid)
            detail_content.refresh()
        except Exception as exc:
            err_label.set_text(f'{label}失败：{exc}')
            _state['sections'] = prev_sections
            detail_content.refresh()
        finally:
            _state['fetching'] = False
            spinner.classes(add='hidden')
            _enable_fetch()

    async def _on_fetch_detail():
        mid = _state.get('match_id')
        if mid:
            await _run_fetch([lambda: run.io_bound(fetch_match_detail, mid)], '抓取数据1')

    async def _on_fetch_odds():
        mid = _state.get('match_id')
        if mid:
            await _run_fetch([lambda: run.io_bound(fetch_match_odds_list, mid)], '抓取数据2')

    def _on_init():
        _state['sections'] = None
        _state['auto_fetched'] = False
        _state['fetching'] = False
        err_label.set_text('')
        detail_content.refresh()

    async def _on_load_history():
        mid = _state.get('match_id')
        if mid:
            await _run_fetch([lambda: run.io_bound(_fetch_recent_odds, mid)], '历史数据加载')

    fetch_btn_1.on_click(_on_fetch_detail)
    fetch_btn_2.on_click(_on_fetch_odds)
    init_btn.on_click(_on_init)
    save_btn.on_click(lambda: ui.notify('结果保存功能待实现', type='info'))
    history_load_btn.on_click(_on_load_history)
    history_page_btn.on_click(lambda: ui.notify('历史数据页面功能待实现', type='info'))
    export_img_btn.on_click(lambda: ui.notify('另存为图片功能待实现', type='info'))
    print_btn.on_click(lambda: ui.notify('打印功能待实现', type='info'))
    if on_back:
        exit_btn.on_click(on_back)