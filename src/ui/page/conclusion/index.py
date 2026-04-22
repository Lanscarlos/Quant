"""
结论展示页 — 由抓取页完成后自动跳转并渲染数据.

External API:
  render() — registered with the Router, returns trigger(mid) callback
"""
import asyncio
import subprocess

from nicegui import ui

from .formatters import fmt_display
from .queries import load_all_from_quant
from .renderers import render_asian_section, render_h2h_section, render_league_table_section, render_odds_section, render_over_under_section, render_recent_section, wdl_badges


def _render_body(data: dict, on_back=None, on_refetch=None, on_refresh_odds=None,
                 source: str = 'live', table_vis: dict | None = None) -> None:
    """渲染结论主体内容。data 是 load_all_from_quant / load_snapshot 返回的统一数据包。"""
    match = data['match']
    if not match:
        ui.label('未找到赛事数据').classes('text-sm text-slate-400')
        return

    extras       = data['extras']
    recent       = data['recent']
    h2h          = data['h2h']
    odds         = data['odds']
    asian_odds   = data['asian_odds']
    over_under   = data.get('over_under')
    league_table = data.get('league_table') or {}
    if table_vis is None:
        table_vis = {'open': True}

    def _toggle_table():
        table_vis['open'] = not table_vis['open']

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
            ui.button('反向为图片',   on_click=lambda: ui.notify('反向为图片')).props('outline size=sm')
            ui.button('分析结果打印', on_click=lambda: ui.notify('分析结果打印')).props('outline size=sm')
            def _do_refetch():
                if on_refetch:
                    on_refetch(match['schedule_id'])
            ui.button('重新抓取', icon='refresh', on_click=_do_refetch).props('outline size=sm color=warning')
            if on_refresh_odds:
                ui.button('刷新赔率', icon='sync', on_click=on_refresh_odds).props('outline size=sm color=accent')
            def _open_in_chrome():
                url = f'https://zq.titan007.com/analysis/{match["schedule_id"]}sb.htm'
                subprocess.Popen(['cmd', '/c', 'start', 'chrome', url])
            ui.button('在浏览器查看', icon='open_in_browser', on_click=_open_in_chrome).props('outline size=sm color=primary')
            def _go_back():
                if on_back:
                    on_back(source)
            ui.button('返回', on_click=_go_back).props('outline size=sm color=negative')
            ui.element('div').classes('flex-1')
            btn_collapse = ui.button('收起积分榜', icon='chevron_right', on_click=_toggle_table).props('outline size=sm')
            btn_collapse.bind_visibility_from(table_vis, 'open')
            btn_expand = ui.button('展开积分榜', icon='chevron_left', on_click=_toggle_table).props('outline size=sm')
            btn_expand.bind_visibility_from(table_vis, 'open', backward=lambda v: not v)

        ui.separator().classes('mb-2')

        # ── 主区：左侧（头部+数据）+ 右侧积分榜（从主客队头部起对齐）──
        with ui.row().classes('w-full gap-0 items-start'):

            # 左侧：赛事头部 + 数据内容
            with ui.column().classes('flex-1 gap-0 min-w-0'):

                # ── 赛事头部 ──────────────────────────────────────────
                with ui.row().classes('w-full items-center py-2 gap-2'):

                    # 联赛名称（最左侧）
                    ui.label(match['league']).classes('text-xs text-slate-500 self-center w-20 shrink-0')

                    # 主队（靠中间右对齐）
                    with ui.column().classes('flex-1 items-end gap-0'):
                        with ui.row().classes('items-baseline gap-1 justify-end'):
                            if match['home_rank'] is not None:
                                ui.label(str(match['home_rank'])).classes('text-lg font-bold text-blue-700')
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
                                ui.label(str(match['away_rank'])).classes('text-lg font-bold text-red-600')
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

                # ── 主客队各自近八场 ──────────────────────────────────
                with ui.row().classes('w-full gap-0 items-start border border-slate-200 rounded'):
                    render_recent_section(recent['home'], extras.get('home_wdl'), is_home=True,  border_right=True)
                    render_recent_section(recent['away'], extras.get('away_wdl'), is_home=False, border_right=False)

                ui.separator().classes('my-2')

                # ── 近八场交手 + 365亚盘 + 365大小球 (1:1:1) ─────────
                with ui.row().classes('w-full gap-0 items-start border border-slate-200 rounded'):
                    render_h2h_section(h2h, fetched=True, border_right=True)
                    render_asian_section(asian_odds, border_right=True)
                    render_over_under_section(over_under)

                ui.separator().classes('my-2')

                # ── 欧赔：威廉希尔 + 立博 + 365 ──────────────────────
                with ui.row().classes('w-full gap-0 items-start border border-slate-200 rounded'):
                    render_odds_section(odds, '威廉希尔', 'William Hill', border_right=True)
                    render_odds_section(odds, '立博', 'Ladbrokes', border_right=True)
                    render_odds_section(odds, '365欧赔', 'Bet365', border_right=False)

                ui.separator().classes('my-2')

                # ── 分析过程 & 结论 ───────────────────────────────────
                with ui.row().classes('w-full gap-3 items-start'):
                    with ui.column().classes('flex-1 gap-1'):
                        ui.label('分析过程').classes('text-sm font-semibold text-slate-600')
                        ui.textarea().classes('w-full').props('outlined dense rows=6')
                    with ui.column().classes('flex-1 gap-1'):
                        ui.label('结论').classes('text-sm font-semibold text-slate-600')
                        ui.textarea().classes('w-full').props('outlined dense rows=6')

            # 右侧积分榜（与主客队头部顶部对齐，可收起）
            with ui.column().classes('w-44 shrink-0 border-l border-slate-200 pl-2 gap-0') as standings_col:
                standings_col.bind_visibility_from(table_vis, 'open')
                render_league_table_section(league_table)


def render(on_back: callable = None, on_refetch: callable = None):
    state      = {'mid': None, 'source': 'live'}
    table_vis  = {'open': True}

    # 悬浮指示器状态：idle / loading / done / error
    refresh_state = {'phase': 'idle', 'msg': ''}

    async def _start_odds_refresh():
        """在结论页内直接抓取欧赔+亚盘四个步骤，无需跳转 fetch 页。"""
        if refresh_state['phase'] == 'loading' or not state['mid']:
            return
        # 在任何 conclusion_body.refresh() 销毁元素之前捕获 client.content，
        # 以便后续通过 with _client_content: 重建 slot 上下文调用 ui.notify()。
        from nicegui.context import context as _nicegui_ctx
        _client_content = _nicegui_ctx.client.content
        from src.ui.page.fetch.steps import (
            StepEuroOdds, StepAsianOdds, StepEuroHistory, StepAsianHistory,
        )
        refresh_state['phase'] = 'loading'
        refresh_state['msg'] = '欧赔 & 亚盘…'
        _odds_refresh_badge.refresh()
        mid_str = str(state['mid'])
        ctx: dict = {}
        try:
            # Phase 3 并行抓取；await 处事件循环得以运行，悬浮指示器状态推送至浏览器
            await asyncio.gather(
                StepEuroOdds.fetch(mid_str, ctx),
                StepAsianOdds.fetch(mid_str, ctx),
            )
            refresh_state['msg'] = '历史数据…'
            _odds_refresh_badge.refresh()
            # Phase 4 并行抓取
            await asyncio.gather(
                StepEuroHistory.fetch(mid_str, ctx),
                StepAsianHistory.fetch(mid_str, ctx),
            )
        except Exception as exc:
            refresh_state['phase'] = 'error'
            refresh_state['msg'] = f'刷新失败：{str(exc)[:40]}'
            _odds_refresh_badge.refresh()
            conclusion_body.refresh()
            # 3 秒后恢复空闲态
            ui.timer(3.0, lambda: _reset_refresh_state(), once=True)
            return
        refresh_state['phase'] = 'done'
        refresh_state['msg'] = '刷新完成'
        _odds_refresh_badge.refresh()
        conclusion_body.refresh()
        # 2 秒后恢复空闲态
        ui.timer(2.0, lambda: _reset_refresh_state(), once=True)

    def _reset_refresh_state():
        refresh_state['phase'] = 'idle'
        refresh_state['msg'] = ''
        _odds_refresh_badge.refresh()

    # ── 布局 ──────────────────────────────────────────────────────────────────
    with ui.scroll_area().classes('w-full h-full'):
        with ui.column().classes('w-full px-4 pt-1 pb-4'):

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

                _render_body(data, on_back=on_back, on_refetch=on_refetch,
                             on_refresh_odds=(lambda: _start_odds_refresh()) if state['source'] == 'live' else None,
                             source=state['source'], table_vis=table_vis)

            conclusion_body()

    # ── 右下角悬浮刷新赔率指示器 ──────────────────────────────────────────────
    # 注入呼吸动画 CSS（仅一次）
    ui.add_css('''
    @keyframes odds-pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(59,130,246,0.4); }
        50%      { box-shadow: 0 0 0 8px rgba(59,130,246,0); }
    }
    .odds-badge-loading {
        animation: odds-pulse 1.8s ease-in-out infinite;
    }
    @keyframes odds-fade-in {
        from { opacity: 0; transform: translateY(8px) scale(0.95); }
        to   { opacity: 1; transform: translateY(0) scale(1); }
    }
    .odds-badge-enter {
        animation: odds-fade-in 0.25s ease-out;
    }
    ''')

    @ui.refreshable
    def _odds_refresh_badge():
        # 仅在 live 模式且有赛事时显示
        if state['source'] != 'live' or not state['mid']:
            return

        phase = refresh_state['phase']
        msg   = refresh_state['msg']

        if phase == 'idle':
            # 空闲态：按钮已移至操作栏，右下角不显示任何内容
            return

        elif phase == 'loading':
            # 加载态：胶囊展开，带呼吸动画
            with ui.row().classes(
                'fixed bottom-5 right-5 z-50 items-center gap-2 px-4 py-2.5 '
                'bg-white rounded-full shadow-lg border border-blue-200 '
                'odds-badge-loading odds-badge-enter select-none'
            ):
                ui.spinner('dots', size='sm', color='blue')
                ui.label(msg).classes('text-sm font-medium text-blue-600 whitespace-nowrap')

        elif phase == 'done':
            # 完成态：绿色胶囊
            with ui.row().classes(
                'fixed bottom-5 right-5 z-50 items-center gap-2 px-4 py-2.5 '
                'bg-green-50 rounded-full shadow-lg border border-green-300 '
                'odds-badge-enter select-none'
            ):
                ui.icon('check_circle').classes('text-green-600 text-lg')
                ui.label(msg).classes('text-sm font-medium text-green-600 whitespace-nowrap')

        elif phase == 'error':
            # 失败态：红色胶囊
            with ui.row().classes(
                'fixed bottom-5 right-5 z-50 items-center gap-2 px-4 py-2.5 '
                'bg-red-50 rounded-full shadow-lg border border-red-300 '
                'odds-badge-enter select-none'
            ):
                ui.icon('error_outline').classes('text-red-500 text-lg')
                ui.label(msg).classes('text-sm font-medium text-red-500 whitespace-nowrap')

    _odds_refresh_badge()

    # ── 外部 API ──────────────────────────────────────────────────────────────

    def trigger(mid: int | str, source: str = 'live') -> None:
        """设置 mid 并刷新结论。source='live' 从 quant.db 读，'history' 从 history.db 读。"""
        state['mid']      = int(mid)
        state['source']   = source
        table_vis['open'] = True
        # 切换赛事时重置悬浮指示器
        refresh_state['phase'] = 'idle'
        refresh_state['msg'] = ''
        conclusion_body.refresh()
        _odds_refresh_badge.refresh()

    return trigger
