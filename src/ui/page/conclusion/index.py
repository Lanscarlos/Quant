"""
结论展示页 — 由抓取页完成后自动跳转并渲染数据.

External API:
  render() — registered with the Router, returns trigger(mid) callback
"""
from nicegui import ui

from .formatters import fmt_display
from .queries import query_asian_odds, query_header_extras, query_h2h, query_match, query_odds, query_recent_matches
from .renderers import render_asian_section, render_h2h_section, render_odds_section, render_recent_section, wdl_badges


def _render_body(mid: int) -> None:
    """渲染结论主体内容."""
    match = query_match(mid)
    if not match:
        ui.label('未找到赛事数据').classes('text-sm text-slate-400')
        return

    extras      = query_header_extras(mid)
    recent      = query_recent_matches(mid)
    h2h         = query_h2h(mid)
    odds        = query_odds(mid)
    asian_odds  = query_asian_odds(mid)

    with ui.column().classes('w-full gap-0'):

        # ── 操作按钮栏 ────────────────────────────────────────────────
        with ui.row().classes('w-full items-center gap-1 pb-2 flex-wrap'):
            ui.button('点击获取数据1', on_click=lambda: ui.notify('点击获取数据1')).props('outline size=sm')
            ui.button('点击获取数据2', on_click=lambda: ui.notify('点击获取数据2')).props('outline size=sm')
            ui.button('数据分析初始', on_click=lambda: ui.notify('数据分析初始')).props('outline size=sm')
            ui.button('结果保存',     on_click=lambda: ui.notify('结果保存')).props('outline size=sm')
            ui.button('历史数据加载', on_click=lambda: ui.notify('历史数据加载')).props('outline size=sm')
            ui.button('历史数据页面', on_click=lambda: ui.notify('历史数据页面')).props('outline size=sm')
            ui.button('反向为图片',   on_click=lambda: ui.notify('反向为图片')).props('outline size=sm')
            ui.button('分析结果打印', on_click=lambda: ui.notify('分析结果打印')).props('outline size=sm')
            ui.button('返回',         on_click=lambda: ui.notify('返回')).props('outline size=sm color=negative')

        ui.separator().classes('mb-2')

        # ── 赛事头部 ──────────────────────────────────────────────────
        with ui.row().classes('w-full items-center py-2'):

            # 主队
            with ui.column().classes('flex-1 gap-0'):
                ui.label(match['home_team']).classes('text-lg font-bold text-blue-700')
                with ui.row().classes('items-center gap-3'):
                    with ui.row().classes('items-center gap-1'):
                        ui.label('排名').classes('text-xs text-slate-400')
                        ui.label(fmt_display(match['home_rank'])).classes('text-xs font-bold text-slate-600')
                    with ui.row().classes('items-center gap-1'):
                        ui.label('积分').classes('text-xs text-slate-400')
                        ui.label(fmt_display(extras.get('home_pts'))).classes('text-xs font-bold text-slate-600')
                    if extras.get('home_wdl'):
                        wdl_badges(*extras['home_wdl'])

            # 比分 / 时间 / 联赛
            with ui.column().classes('px-4 items-center gap-0 flex-shrink-0'):
                hs, as_ = match['home_score'], match['away_score']
                if hs is not None:
                    ui.label(f'{hs}  :  {as_}').classes('text-2xl font-bold text-slate-800')
                    hhs, ahs = match['home_half_score'], match['away_half_score']
                    if hhs is not None:
                        ui.label(f'半场 {hhs}:{ahs}').classes('text-xs text-slate-400')
                else:
                    ui.label('VS').classes('text-2xl font-bold text-slate-300')
                ui.label(match['match_time'] or '').classes('text-xs text-slate-400 mt-1')
                ui.label(match['league']).classes('text-xs text-slate-500')

            # 客队
            with ui.column().classes('flex-1 items-end gap-0'):
                ui.label(match['away_team']).classes('text-lg font-bold text-red-600 text-right')
                with ui.row().classes('items-center gap-3'):
                    if extras.get('away_wdl'):
                        wdl_badges(*extras['away_wdl'])
                    with ui.row().classes('items-center gap-1'):
                        ui.label('积分').classes('text-xs text-slate-400')
                        ui.label(fmt_display(extras.get('away_pts'))).classes('text-xs font-bold text-slate-600')
                    with ui.row().classes('items-center gap-1'):
                        ui.label('排名').classes('text-xs text-slate-400')
                        ui.label(fmt_display(match['away_rank'])).classes('text-xs font-bold text-slate-600')

        ui.separator().classes('my-2')

        # ── 主客队各自近六场 ──────────────────────────────────────────
        with ui.row().classes('w-full gap-0 items-start border border-slate-200 rounded'):
            render_recent_section(recent['home'], extras.get('home_wdl'), is_home=True,  border_right=True)
            render_recent_section(recent['away'], extras.get('away_wdl'), is_home=False, border_right=False)

        ui.separator().classes('my-2')

        # ── 近六场交手 ────────────────────────────────────────────────
        with ui.row().classes('w-full gap-0 items-start border border-slate-200 rounded'):
            render_h2h_section(h2h, fetched=True, border_right=False)

        ui.separator().classes('my-2')

        # ── 欧赔：威廉希尔 + 立博 ─────────────────────────────────────
        with ui.row().classes('w-full gap-0 items-start border border-slate-200 rounded'):
            render_odds_section(odds, '威廉希尔', 'William Hill', border_right=True)
            render_odds_section(odds, '立博', 'Ladbrokes', border_right=False)

        ui.separator().classes('my-2')

        # ── 365 亚盘 ──────────────────────────────────────────────────
        with ui.row().classes('w-full gap-0 items-start border border-slate-200 rounded'):
            render_asian_section(asian_odds)

        ui.separator().classes('my-2')

        # ── 分析过程 & 结论 ───────────────────────────────────────────
        with ui.row().classes('w-full gap-3 items-start'):
            with ui.column().classes('flex-1 gap-1'):
                ui.label('分析过程').classes('text-sm font-semibold text-slate-600')
                ui.textarea().classes('w-full').props('outlined dense rows=6')
            with ui.column().classes('flex-1 gap-1'):
                ui.label('结论').classes('text-sm font-semibold text-slate-600')
                ui.textarea().classes('w-full').props('outlined dense rows=6')


def render():
    state = {'mid': None}

    # ── 布局 ──────────────────────────────────────────────────────────────────
    with ui.scroll_area().classes('w-full h-full'):
        with ui.column().classes('w-full p-4'):

            @ui.refreshable
            def conclusion_body():
                mid = state['mid']
                if not mid:
                    with ui.column().classes('w-full items-center gap-3 py-16 text-gray-400'):
                        ui.icon('info_outline').classes('text-4xl')
                        ui.label('暂无数据').classes('text-base font-medium')
                        ui.label('请在「赛事列表」中点击赛事，或在「抓取数据」页输入赛事 URL 后抓取').classes('text-sm')
                    return
                _render_body(mid)

            conclusion_body()

    # ── 外部 API ──────────────────────────────────────────────────────────────

    def trigger(mid: int | str) -> None:
        """由抓取页完成后调用：设置 mid 并刷新结论."""
        state['mid'] = int(mid)
        conclusion_body.refresh()

    return trigger
