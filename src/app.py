from nicegui import ui
from src import match_view

PORT = 19193
NAME = "Quant"
ICON = "assets/icon.ico"
SIZE = (1080, 720)

@ui.page('/')
def index():
    ui.query('body').style('background-color: #f8fafc')
    with ui.column().classes('w-full max-w-5xl mx-auto p-4 gap-0'):
        match_view.render()