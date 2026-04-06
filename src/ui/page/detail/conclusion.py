"""结论步骤 — 展示已抓取的赛事数据汇总."""
from nicegui import ui

from ._formatters import _d
from ._queries import _query_header_extras, _query_h2h, _query_match, _query_odds
from ._renderers import _render_h2h_section, _render_odds_section, _wdl_badges


def render(mid: int) -> None:
    match = _query_match(mid)
    if not match:
        ui.label('未找到赛事数据').classes('text-sm text-slate-400')
        return

    extras = _query_header_extras(mid)
    h2h    = _query_h2h(mid)
    odds   = _query_odds(mid)

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
                        ui.label(_d(match['home_rank'])).classes('text-xs font-bold text-slate-600')
                    with ui.row().classes('items-center gap-1'):
                        ui.label('积分').classes('text-xs text-slate-400')
                        ui.label(_d(extras.get('home_pts'))).classes('text-xs font-bold text-slate-600')
                    if extras.get('home_wdl'):
                        _wdl_badges(*extras['home_wdl'])

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
                        _wdl_badges(*extras['away_wdl'])
                    with ui.row().classes('items-center gap-1'):
                        ui.label('积分').classes('text-xs text-slate-400')
                        ui.label(_d(extras.get('away_pts'))).classes('text-xs font-bold text-slate-600')
                    with ui.row().classes('items-center gap-1'):
                        ui.label('排名').classes('text-xs text-slate-400')
                        ui.label(_d(match['away_rank'])).classes('text-xs font-bold text-slate-600')

        ui.separator().classes('my-2')

        # ── 近六场交手 ────────────────────────────────────────────────
        with ui.row().classes('w-full gap-0 items-start border border-slate-200 rounded'):
            _render_h2h_section(h2h, fetched=True, border_right=False)

        ui.separator().classes('my-2')

        # ── 欧赔：威廉希尔 + 立博 ─────────────────────────────────────
        with ui.row().classes('w-full gap-0 items-start border border-slate-200 rounded'):
            _render_odds_section(odds, '威廉希尔', 'William Hill', border_right=True)
            _render_odds_section(odds, '立博', 'Ladbrokes', border_right=False)
