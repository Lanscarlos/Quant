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


_ODDS_EMPTY  = {'tag': '', 'win': '-', 'draw': '-', 'lose': '-', 'payout': '-', 'time': '-'}
_ASIAN_EMPTY = {'tag': '', 'home': '-', 'hc': '-', 'away': '-', 'time': '-', 'data': '-'}

_TAG_SLOT = '<q-td :props="props"><q-badge v-if="props.value" color="amber-8" :label="props.value" /></q-td>'


def _dir_slot(dir_field: str) -> str:
    cls = (
        f"props.row.{dir_field} === 'up' ? 'text-positive' : "
        f"props.row.{dir_field} === 'down' ? 'text-negative' : ''"
    )
    return f'<q-td :props="props"><span :class="{cls}">{{{{ props.value }}}}</span></q-td>'


def render_odds_section(odds: dict, label: str, company_key: str, border_right: bool = True):
    border_cls = 'border-r border-slate-200' if border_right else ''
    with ui.column().classes(f'flex-1 {border_cls} p-2 gap-1 min-w-0'):
        ui.label(label).classes('text-xs font-semibold text-slate-600')
        company_data = odds.get(company_key) if odds else None
        if company_data:
            history = company_data['history']
            padded  = (history + [_ODDS_EMPTY] * 5)[:5]
            open_r  = {**company_data['open'], 'tag': '初始'}
            hist_rs = [{**r, 'tag': ''} for r in padded]
            t = ui.table(columns=ODDS_COLS, rows=[open_r] + hist_rs).classes('w-full text-xs').props('dense flat')
            t.add_slot('body-cell-tag',  _TAG_SLOT)
            t.add_slot('body-cell-win',  _dir_slot('win_dir'))
            t.add_slot('body-cell-draw', _dir_slot('draw_dir'))
            t.add_slot('body-cell-lose', _dir_slot('lose_dir'))
        else:
            no_data_hint()


def render_asian_section(asian_row: dict | None):
    with ui.column().classes('flex-1 p-2 gap-1 min-w-0'):
        ui.label('365亚盘').classes('text-xs font-semibold text-slate-600')
        if asian_row:
            history = asian_row['history']
            padded  = (history + [_ASIAN_EMPTY] * 3)[:3]
            open_r  = {**asian_row['open'], 'tag': '初始', 'data': '-'}
            rows    = [open_r] + [{**r, 'tag': '', 'data': '-'} for r in padded]
            t = ui.table(columns=ASIAN_COLS, rows=rows).classes('w-full text-xs').props('dense flat')
            t.add_slot('body-cell-tag',  _TAG_SLOT)
            t.add_slot('body-cell-home', _dir_slot('home_dir'))
            t.add_slot('body-cell-away', _dir_slot('away_dir'))
        else:
            no_data_hint()
