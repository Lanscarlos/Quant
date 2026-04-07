"""
步骤内子任务进度追踪 — 线程安全，供 io_bound 线程调用.

用法 (service 层):
    def fetch_something(mid, tracker=None):
        with tracker.task('html', '下载 HTML') if tracker else nullcontext():
            html = _fetch(mid)
        with tracker.task('parse', '解析数据') if tracker else nullcontext():
            ...

    # 或用显式 start/done/error:
        t = tracker.task('progress', '处理进度').start()
        for i in items:
            ...
            t.update(f'({i}/{total})')
        t.done()
"""

from __future__ import annotations

from contextlib import nullcontext  # noqa: F401 — re-exported for callers


class SubTask:
    """单条子任务，持有状态 + 标签，可作为上下文管理器使用。"""

    def __init__(self, key: str, label: str, on_update):
        self.key    = key
        self.label  = label
        self.status = 'pending'   # pending | running | done | error
        self.msg    = ''
        self._on_update = on_update

    # ── 显式控制 ─────────────────────────────────────────────────────────────

    def start(self) -> 'SubTask':
        self.status = 'running'
        self._on_update()
        return self

    def done(self, msg: str = '') -> None:
        self.status = 'done'
        self.msg    = msg
        self._on_update()

    def error(self, msg: str) -> None:
        self.status = 'error'
        self.msg    = str(msg)[:100]
        self._on_update()

    def update(self, msg: str) -> None:
        """更新进度文本（保持 running 状态，仅刷新消息）。"""
        self.msg = msg
        self._on_update()

    # ── 上下文管理器 ──────────────────────────────────────────────────────────

    def __enter__(self) -> 'SubTask':
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.error(str(exc_val))
        else:
            self.done()
        return False  # 不吞异常


class ProgressTracker:
    """步骤进度追踪器，负责注册子任务并通过线程安全回调触发 UI 刷新。

    Args:
        task_list:  由 index.py 提供的可变列表，UI 层读取渲染。
        on_update:  线程安全的刷新触发器，通常封装 loop.call_soon_threadsafe。
    """

    def __init__(self, task_list: list, on_update):
        self._tasks    = task_list
        self._on_update = on_update

    def task(self, key: str, label: str) -> SubTask:
        """注册一个新子任务（pending），追加到列表并触发 UI 刷新。"""
        st = SubTask(key, label, self._on_update)
        self._tasks.append(st)
        self._on_update()
        return st