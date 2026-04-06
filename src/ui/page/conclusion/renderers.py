"""UI helpers and section renderers for the conclusion page."""
from nicegui import ui

from .columns import ASIAN_COLS, H2H_COLS, ODDS_COLS, RECENT_COLS


# ── Micro helpers ──────────────────────────────────────────────────────────────

def no_data_hint():
    with ui.row().classes('w-full items-center gap-1 py-3 justify-center'):
        ui.icon('info_outline').classes('text-slate-300 text-base')
        ui.label('暂无数据，请点击「抓取数据」').classes('text-xs text-slate-400')


def wdl_badges(win: int, draw: int, loss: int):
    ui.label(f'胜{win}').classes('text-xs font-bold text-green-600')
    ui.label(f'平{draw}').classes('text-xs font-bold text-slate-500')
    ui.label(f'负{loss}').classes('text-xs font-bold text-red-500')


# ── Section renderers ──────────────────────────────────────────────────────────

def render_recent_section(rows: list, wdl: tuple | None, is_home: bool, border_right: bool = True):
    color_cls  = 'text-blue-700' if is_home else 'text-red-600'
    title      = '主队近六场比赛:' if is_home else '客队近六场比赛:'
    border_cls = 'border-r border-slate-200' if border_right else ''

    with ui.column().classes(f'flex-1 {border_cls} p-2 gap-1 min-w-0'):
        with ui.row().classes('w-full items-center gap-2'):
            ui.label(title).classes(f'text-xs font-semibold {color_cls} flex-1 truncate')
            if wdl:
                wdl_badges(*wdl)
        if rows:
            ui.table(columns=RECENT_COLS, rows=rows).classes('w-full text-xs').props('dense flat')
        else:
            no_data_hint()


def render_h2h_section(h2h: dict, fetched: bool = False, border_right: bool = True):
    border_cls = 'border-r border-slate-200' if border_right else ''
    with ui.column().classes(f'flex-1 {border_cls} p-2 gap-1 min-w-0'):
        with ui.row().classes('w-full items-center gap-2'):
            ui.label('近六场交手:').classes('text-xs font-semibold text-slate-600 flex-1')
            if h2h['rows']:
                wdl_badges(h2h['win'], h2h['draw'], h2h['loss'])
        if h2h['rows']:
            ui.table(columns=H2H_COLS, rows=h2h['rows']).classes('w-full text-xs').props('dense flat')
        elif fetched:
            with ui.row().classes('items-center gap-1 py-3 justify-center'):
                ui.icon('info_outline').classes('text-slate-300 text-base')
                ui.label('暂无历史交手记录').classes('text-xs text-slate-400')
        else:
            no_data_hint()


def render_odds_section(odds_rows: list[dict], label: str, company_key: str, border_right: bool = True):
    border_cls = 'border-r border-slate-200' if border_right else ''
    with ui.column().classes(f'flex-1 {border_cls} p-2 gap-1 min-w-0'):
        ui.label(label).classes('text-xs font-semibold text-slate-600')
        row = next((r for r in odds_rows if r['company'] == company_key), None)
        if row:
            table_rows = [
                {'win': row['open_win'],  'draw': row['open_draw'],  'lose': row['open_lose'],
                 'payout': row['open_payout'],  'time': '-'},
                {'win': row['cur_win'],   'draw': row['cur_draw'],   'lose': row['cur_lose'],
                 'payout': row['cur_payout'],   'time': '-'},
                {'win': row['kelly_win'], 'draw': row['kelly_draw'], 'lose': row['kelly_lose'],
                 'payout': '-',                 'time': '-'},
            ]
            ui.table(columns=ODDS_COLS, rows=table_rows).classes('w-full text-xs').props('dense flat')
        else:
            no_data_hint()


def render_asian_section(asian_row: dict | None):
    with ui.column().classes('flex-1 p-2 gap-1 min-w-0'):
        ui.label('365亚盘').classes('text-xs font-semibold text-slate-600')
        if asian_row:
            table_rows = [
                {'home': asian_row['open_home'], 'hc': asian_row['open_handicap'],
                 'away': asian_row['open_away'], 'time': '-', 'data': '-'},
                {'home': asian_row['cur_home'],  'hc': asian_row['cur_handicap'],
                 'away': asian_row['cur_away'],  'time': '-', 'data': '-'},
            ]
            ui.table(columns=ASIAN_COLS, rows=table_rows).classes('w-full text-xs').props('dense flat')
        else:
            no_data_hint()
