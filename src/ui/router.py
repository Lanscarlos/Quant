from nicegui import ui


class Router:
    def __init__(self):
        self._routes: dict[str, callable] = {}
        self._panels: ui.tab_panels | None = None
        self.current: str | None = None
        self._listeners: list[callable] = []
        self._apis: dict[str, any] = {}

    def add(self, key: str, render_fn: callable) -> 'Router':
        self._routes[key] = render_fn
        return self

    def on_navigate(self, callback: callable) -> None:
        """注册导航回调，每次 navigate() 时触发。"""
        self._listeners.append(callback)

    def mount(
        self,
        transition_prev: str = 'slide-down',
        transition_next: str = 'slide-up',
    ) -> ui.tab_panels:
        """在当前 UI 上下文中创建 tab_panels 容器，预渲染所有已注册页面。"""
        self._panels = (
            ui.tab_panels(value='__init__')
            .props(f'animated transition-prev={transition_prev} transition-next={transition_next}')
            .classes('flex-1 h-full bg-gray-100 p-6 gap-4')
        )
        with self._panels:
            for key, render_fn in self._routes.items():
                with ui.tab_panel(key):
                    ret = render_fn()
                    if ret is not None:
                        self._apis[key] = ret
        return self._panels

    def get_api(self, key: str):
        """返回页面 render() 的返回值（如有）。"""
        return self._apis.get(key)

    def navigate(self, key: str) -> None:
        if self._panels is None or key not in self._routes:
            return
        self._panels.set_value(key)
        self.current = key
        for cb in self._listeners:
            cb(key)