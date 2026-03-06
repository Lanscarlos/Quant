from nicegui import ui

@ui.page('/dashboard')
def render():
    ui.label('你好')