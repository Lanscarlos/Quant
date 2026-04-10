# main.py

from nicegui import ui
import src.ui.index as app
from src.db import init_db, init_history_db

init_db()
init_history_db()

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        port = app.PORT,
        title = app.NAME,
        favicon = app.ICON,
        window_size = app.SIZE,
        fullscreen = False,
        native = True,
        reload = False
    )