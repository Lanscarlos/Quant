from nicegui import ui

# 你的页面代码
@ui.page('/')
def index():
    ui.label('Hello World')

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(native=True, reload=False, window_size=(800, 600), fullscreen=False)