"""
赛事列表页.

External API:
  render(on_match_click) — 注册到 Router
  返回值: set_refresh_interval(seconds) — 供设置页动态更新自动刷新间隔
"""
import asyncio
import random
import subprocess
from datetime import datetime, timedelta

from nicegui import ui, run

from src.service.browser_filter import get_filtered_match_ids
from src.service.config import get_refresh_interval
from src.service.freshness import match_ids_needing_refresh

from .columns import TABLE_COLS
from .queries import query_filtered
from .refresh import hydrate_ids


def _diff_ids(new_ids: list, cached_ids: list) -> tuple[list, list]:
    """拆分新白名单与缓存白名单的差异。

    Returns:
        (added, kept)
        added — 新增 ID（缓存中没有），需全量抓取
        kept  — 已在缓存中的 ID，仍交给 hydrate_ids 内部 freshness 判断
        两者顺序均沿用 new_ids 中的原始顺序。
    """
    cached_set = set(map(str, cached_ids))
    added, kept = [], []
    for mid in new_ids:
        (added if str(mid) not in cached_set else kept).append(mid)
    return added, kept


def render(on_match_click: callable = None):
    cached_rows:  list = [[]]
    filter_ids:   list = [get_filtered_match_ids()]
    is_loading:   list = [False]   # 仅首次加载时置 True，显示全屏占位 spinner
    is_fetching:  list = [False]   # 重入保护：任何网络抓取任务的并发锁

    # 进度状态：done=0, total=0 表示空闲
    progress_state: dict = {'done': 0, 'total': 0}

    # 倒计时状态：以绝对时间点驱动，避免 tick 抖动累积误差
    interval_seconds: list = [get_refresh_interval()]
    next_refresh_at:  list = [datetime.now() + timedelta(seconds=interval_seconds[0])]

    def _reset_countdown() -> None:
        next_refresh_at[0] = datetime.now() + timedelta(seconds=interval_seconds[0])

    with ui.column().classes('w-full h-full gap-0 relative'):

        # ── 标题行 ────────────────────────────────────────────────────
        with ui.row().classes(
            'w-full items-center gap-2 px-4 py-2 bg-white border-b border-slate-200'
        ):
            ui.icon('sports_soccer').classes('text-xl text-blue-600')
            ui.label('赛事列表').classes('text-base font-bold text-slate-700 flex-1')
            err_label = ui.label('').classes('text-xs text-red-500')
            # 进度徽标：抓取期间可见，空闲时隐藏
            with ui.row().classes(
                'items-center gap-1.5 px-2 py-0.5 bg-blue-50 rounded-full'
            ) as progress_chip:
                ui.spinner('dots', size='sm', color='blue-6')
                progress_label = ui.label('').classes('text-xs text-blue-600')
            progress_chip.set_visibility(False)
            ui.button('打开赛事列表', icon='open_in_browser',
                      on_click=lambda: subprocess.Popen(['cmd', '/c', 'start', 'chrome', 'https://live.titan007.com/oldIndexall.aspx'])).props('outline color=primary')
            refresh_btn = ui.button('刷新列表', icon='refresh').props('unelevated color=primary')

        # ── 提示行 ────────────────────────────────────────────────────
        with ui.row().classes(
            'w-full items-center gap-2 px-4 py-1.5 bg-blue-50 border-b border-blue-100'
        ):
            ui.icon('info').classes('text-sm text-blue-400')
            ui.label('请使用 Chrome 浏览器筛选赛事，筛选后点击「刷新列表」加载数据').classes(
                'text-xs text-blue-600'
            )

        # ── 主内容区 ──────────────────────────────────────────────────
        with ui.scroll_area().classes('w-full flex-1'):
            with ui.column().classes('w-full gap-3 p-3'):

                # 主数据表格（蓝色边框）
                with ui.element('div').style(
                    'width:100%; border:2px solid #3b82f6; border-radius:4px; overflow:hidden'
                ):
                    @ui.refreshable
                    def data_table():
                        if is_loading[0]:
                            with ui.row().classes(
                                'w-full items-center justify-center gap-3 py-16'
                            ):
                                ui.spinner('dots', size='lg', color='blue-6')
                                ui.label('正在加载...').classes('text-sm text-slate-400')
                            return

                        rows = cached_rows[0]
                        if not rows:
                            with ui.row().classes(
                                'w-full items-center justify-center py-10 gap-2'
                            ):
                                ui.icon('search_off').classes('text-3xl text-slate-300')
                                ui.label('暂无数据，请点击按钮加载').classes('text-sm text-slate-400')
                            return

                        tbl = (
                            ui.table(columns=TABLE_COLS, rows=rows, row_key='id')
                            .classes('w-full text-xs')
                            .props('dense flat')
                        )

                        # 详情列：只渲染图标，实际点击通过 rowClick 响应
                        tbl.add_slot('body-cell-detail', '''
                            <q-td :props="props" class="cursor-pointer">
                                <q-icon name="open_in_new" color="blue-6" size="14px" />
                            </q-td>
                        ''')

                        if on_match_click:
                            tbl.on('rowClick', lambda e: on_match_click(e.args[1]['id']))

                    data_table()

        # ── 倒计时浮标（右下角） ──────────────────────────────────────
        with ui.row().classes(
            'absolute bottom-4 right-4 items-center gap-1.5 px-3 py-1.5 '
            'bg-white/90 rounded-full shadow border border-slate-200 z-10'
        ):
            ui.icon('schedule').classes('text-sm text-slate-400')
            countdown_label = ui.label('--').classes('text-xs font-mono text-slate-600')

    # ── 进度回调（由 io_bound 线程触发，必须通过 call_soon_threadsafe 回主循环） ──

    loop = asyncio.get_event_loop()

    def _apply_progress(done: int, total: int) -> None:
        """在事件循环中更新进度徽标并增量刷新表格。"""
        if total == 0 or done >= total:
            # 抓取完毕或清零：隐藏徽标、归零状态
            progress_state['done'] = 0
            progress_state['total'] = 0
            progress_chip.set_visibility(False)
            progress_label.set_text('')
        else:
            progress_state['done'] = done
            progress_state['total'] = total
            progress_label.set_text(f'正在抓取 {done}/{total}')
            progress_chip.set_visibility(True)
        # 每条完成后重查 DB，让已抓好的赛事立即出现在表格
        cached_rows[0] = query_filtered(filter_ids[0])
        data_table.refresh()

    def _progress_cb(done: int, total: int, _mid: str) -> None:
        """hydrate_ids 每处理完一条赛事时调用，转回事件循环执行 UI 更新。"""
        loop.call_soon_threadsafe(_apply_progress, done, total)

    def _clear_progress() -> None:
        """抓取结束/异常时确保进度状态归零（在事件循环内直接调用）。"""
        _apply_progress(0, 0)

    # ── 事件绑定 ──────────────────────────────────────────────────────

    def _reload():
        cached_rows[0] = query_filtered(filter_ids[0])
        data_table.refresh()

    async def _on_fetch():
        """首次/手动触发：仅当表格为空时显示全屏 spinner，其余使用进度徽标。"""
        if is_fetching[0]:
            return
        is_fetching[0] = True
        err_label.set_text('')
        # 仅首次（表格还没有数据）才显示全屏 loading 占位
        first_load = not cached_rows[0]
        if first_load:
            is_loading[0] = True
            data_table.refresh()
        try:
            await run.io_bound(hydrate_ids, filter_ids[0], _progress_cb)
            is_loading[0] = False
            _reload()
        except Exception as exc:
            is_loading[0] = False
            data_table.refresh()
            err_label.set_text(f'抓取失败：{exc}')
        finally:
            _clear_progress()
            is_fetching[0] = False
            _reset_countdown()

    async def _on_refresh():
        if is_fetching[0]:
            return
        is_fetching[0] = True
        refresh_btn.props(add='loading disable')
        err_label.set_text('')
        try:
            # 1) 重读 Chrome 筛选白名单
            new_filter, _ = await asyncio.gather(
                run.io_bound(get_filtered_match_ids),
                asyncio.sleep(random.uniform(0.1, 0.6)),
            )
            # 2) 白名单为空 → 提示用户先在 Chrome 筛选赛事
            if not new_filter:
                ui.notify('请先在 Chrome 浏览器中筛选赛事，再点击刷新列表',
                          type='warning', position='top', timeout=4000)
                return
            # 3) 差量：新增 ID 全量抓，老 ID 走 freshness 判断
            added, kept = _diff_ids(new_filter, filter_ids[0])
            filter_ids[0] = new_filter
            # 4) 按差量抓取（进度回调驱动增量渲染）
            await run.io_bound(hydrate_ids, added + kept, _progress_cb)
            _reload()
        except Exception as exc:
            data_table.refresh()
            err_label.set_text(f'刷新失败：{exc}')
        finally:
            _clear_progress()
            is_fetching[0] = False
            refresh_btn.props(remove='loading disable')
            _reset_countdown()

    async def _auto_refresh():
        """周期静默刷新：重读 Chrome 白名单 + 差量补抓过期赛事，不显示 loading 遮罩。"""
        if is_fetching[0]:
            return
        is_fetching[0] = True
        try:
            new_filter = await run.io_bound(get_filtered_match_ids)
            added, kept = _diff_ids(new_filter, filter_ids[0])
            filter_ids[0] = new_filter
            await run.io_bound(hydrate_ids, added + kept, _progress_cb)
            cached_rows[0] = query_filtered(filter_ids[0])
            data_table.refresh()
        except Exception as exc:
            err_label.set_text(f'自动刷新失败：{exc}')
        finally:
            _clear_progress()
            is_fetching[0] = False
            _reset_countdown()

    refresh_btn.on_click(_on_refresh)

    # 初始加载 + 自动抓取缺失/过期赛事
    _reload()

    async def _auto_fetch():
        if match_ids_needing_refresh(filter_ids[0]):
            await _on_fetch()

    ui.timer(0, _auto_fetch, once=True)                          # 首次挂载立即抓一次
    refresh_timer = ui.timer(interval_seconds[0], _auto_refresh)  # 按配置间隔静默刷新

    # ── 倒计时显示：每秒 tick 更新标签 ─────────────────────────────
    def _tick_countdown():
        # 优先级 1：有抓取进度 → 显示 "抓取中 x/y"
        if progress_state['total'] > 0:
            done, total = progress_state['done'], progress_state['total']
            countdown_label.set_text(f'抓取中 {done}/{total}')
            countdown_label.classes(remove='text-slate-600', add='text-blue-600')
            return
        # 优先级 2：正在读取/等待中（无具体进度）→ 显示 "刷新中…"
        if is_fetching[0]:
            countdown_label.set_text('刷新中…')
            countdown_label.classes(remove='text-slate-600', add='text-blue-600')
            return
        # 优先级 3：空闲 → 显示倒计时
        remaining = int((next_refresh_at[0] - datetime.now()).total_seconds())
        remaining = max(0, remaining)
        mins, secs = divmod(remaining, 60)
        text = f'{mins}:{secs:02d} 后自动刷新' if mins else f'{secs} 秒后自动刷新'
        countdown_label.set_text(text)
        countdown_label.classes(remove='text-blue-600', add='text-slate-600')

    ui.timer(1, _tick_countdown)

    def set_refresh_interval(seconds: int) -> None:
        """供设置页调用，动态更新定时器间隔并重置倒计时。"""
        interval_seconds[0] = seconds
        refresh_timer.interval = seconds
        _reset_countdown()

    return set_refresh_interval
