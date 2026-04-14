"""
结论展示页 — 由抓取页完成后自动跳转并渲染数据.

External API:
  render() — registered with the Router, returns trigger(mid) callback
"""
import subprocess

from nicegui import ui

from .formatters import fmt_display
from .queries import load_all_from_quant
from .renderers import render_asian_section, render_h2h_section, render_odds_section, render_recent_section, wdl_badges


def _render_body(data: dict, on_back=None, on_refetch=None, source: str = 'live') -> None:
    """渲染结论主体内容。data 是 load_all_from_quant / load_snapshot 返回的统一数据包。"""
    match = data['match']
    if not match:
        ui.label('未找到赛事数据').classes('text-sm text-slate-400')
        return

    extras      = data['extras']
    recent      = data['recent']
    h2h         = data['h2h']
    odds        = data['odds']
    asian_odds  = data['asian_odds']

    with ui.column().classes('w-full gap-0'):

        # ── 操作按钮栏 ────────────────────────────────────────────────
        def _on_save():
            from src.db.repo.history import save_match
            try:
                save_match(match['schedule_id'])
                ui.notify('保存成功', type='positive')
            except Exception as exc:
                ui.notify(f'保存失败：{exc}', type='negative')

        with ui.row().classes('w-full items-center gap-1 pb-2 flex-wrap'):
            ui.button('数据分析初始', on_click=lambda: ui.notify('数据分析初始')).props('outline size=sm')
            ui.button('结果保存',     on_click=_on_save).props('outline size=sm')
            ui.button('历史数据加载', on_click=lambda: ui.notify('历史数据加载')).props('outline size=sm')
            ui.button('历史数据页面', on_click=lambda: ui.notify('历史数据页面')).props('outline size=sm')
            ui.button('反向为图片',   on_click=lambda: ui.notify('反向为图片')).props('outline size=sm')
            ui.button('分析结果打印', on_click=lambda: ui.notify('分析结果打印')).props('outline size=sm')
            def _do_refetch():
                if on_refetch:
                    on_refetch(match['schedule_id'])
            ui.button('重新抓取', icon='refresh', on_click=_do_refetch).props('outline size=sm color=warning')
            def _open_in_chrome():
                url = f'https://zq.titan007.com/analysis/{match["schedule_id"]}sb.htm'
                subprocess.Popen(['cmd', '/c', 'start', 'chrome', url])
            ui.button('在浏览器查看', icon='open_in_browser', on_click=_open_in_chrome).props('outline size=sm color=primary')
            def _go_back():
                if on_back:
                    on_back(source)
            ui.button('返回', on_click=_go_back).props('outline size=sm color=negative')

        ui.separator().classes('mb-2')

        # ── 赛事头部 ──────────────────────────────────────────────────
        with ui.row().classes('w-full items-center py-2 gap-2'):

            # 联赛名称（最左侧）
            ui.label(match['league']).classes('text-xs text-slate-500 self-center w-20 shrink-0')

            # 主队（靠中间右对齐）
            with ui.column().classes('flex-1 items-end gap-0'):
                with ui.row().classes('items-baseline gap-1 justify-end'):
                    if match['home_rank'] is not None:
                        ui.label(str(match['home_rank'])).classes('text-sm text-slate-400')
                    ui.label(match['home_team']).classes('text-lg font-bold text-blue-700')
                with ui.row().classes('items-center gap-3'):
                    with ui.row().classes('items-center gap-1'):
                        ui.label('积分').classes('text-xs text-slate-400')
                        ui.label(fmt_display(extras.get('home_pts'))).classes('text-xs font-bold text-slate-600')
                    if extras.get('home_wdl'):
                        wdl_badges(*extras['home_wdl'])

            # 比分 / 时间
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

            # 客队（靠中间左对齐）
            with ui.column().classes('flex-1 items-start gap-0'):
                with ui.row().classes('items-baseline gap-1'):
                    if match['away_rank'] is not None:
                        ui.label(str(match['away_rank'])).classes('text-sm text-slate-400')
                    ui.label(match['away_team']).classes('text-lg font-bold text-red-600')
                with ui.row().classes('items-center gap-3'):
                    if extras.get('away_wdl'):
                        wdl_badges(*extras['away_wdl'])
                    with ui.row().classes('items-center gap-1'):
                        ui.label('积分').classes('text-xs text-slate-400')
                        ui.label(fmt_display(extras.get('away_pts'))).classes('text-xs font-bold text-slate-600')

            # 右侧占位，平衡左边联赛标签宽度，保持整体居中
            ui.element('div').classes('w-20 shrink-0')

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

        # ── 欧赔：威廉希尔 + 立博 + 365亚盘 ─────────────────────────────
        with ui.row().classes('w-full gap-0 items-start border border-slate-200 rounded'):
            render_odds_section(odds, '威廉希尔', 'William Hill', border_right=True)
            render_odds_section(odds, '立博', 'Ladbrokes', border_right=True)
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


def render(on_back: callable = None, on_refetch: callable = None):
    state = {'mid': None, 'source': 'live'}

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

                if state['source'] == 'history':
                    from src.db.repo.history import load_snapshot
                    data = load_snapshot(mid)
                else:
                    data = load_all_from_quant(mid)

                if not data or not data.get('match'):
                    ui.label('未找到赛事数据').classes('text-sm text-slate-400')
                    return

                _render_body(data, on_back=on_back, on_refetch=on_refetch, source=state['source'])

            conclusion_body()

    # ── 外部 API ──────────────────────────────────────────────────────────────

    def trigger(mid: int | str, source: str = 'live') -> None:
        """设置 mid 并刷新结论。source='live' 从 quant.db 读，'history' 从 history.db 读。"""
        state['mid'] = int(mid)
        state['source'] = source
        conclusion_body.refresh()

    return trigger
