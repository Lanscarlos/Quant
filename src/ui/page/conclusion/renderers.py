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


# zone_flag → Tailwind 背景色类（透明度低，不影响文字可读性）
_ZONE_BG = {0: 'bg-blue-100', 1: 'bg-teal-100', 2: 'bg-stone-200'}


def render_league_table_section(league_table: dict):
    """渲染右侧联赛积分榜面板。

    仅在 league_table['total'] 非空时渲染（联赛赛事）。
    显示总/主/客三个分页，各队积分按位次排列，主客队高亮标注。
    """
    total = league_table.get('total') if league_table else []
    if not total:
        with ui.column().classes('w-full items-center gap-2 py-4'):
            ui.label('联赛积分榜').classes('text-xs font-semibold text-slate-600 w-full')
            ui.icon('info_outline').classes('text-slate-300 text-2xl')
            ui.label('暂无数据').classes('text-xs text-slate-400')
        return

    with ui.column().classes('w-full gap-1'):
        with ui.row().classes('w-full items-center gap-1 pb-0.5'):
            ui.label('联赛积分榜').classes('text-xs font-semibold text-slate-600 flex-1')
            sel = ui.select(
                {'total': '总榜', 'home': '主场', 'away': '客场'},
                value='total',
            ).classes('text-xs').props('dense borderless options-dense')

        with ui.row().classes(
            'w-full items-center px-1 py-0.5 gap-0 text-xs '
            'font-semibold text-slate-400 border-b border-slate-200'
        ):
            ui.label('#').classes('w-5 text-right shrink-0')
            ui.label('球队').classes('flex-1 px-1')
            ui.label('积分').classes('w-8 text-right shrink-0')

        for scope_key in ('total', 'home', 'away'):
            rows = league_table.get(scope_key) or []
            with ui.column().classes('w-full gap-0') as scope_col:
                scope_col.bind_visibility_from(sel, 'value', backward=lambda v, k=scope_key: v == k)
                for r in rows:
                    zone      = r.get('zone_flag', -1)
                    zone_bg   = _ZONE_BG.get(zone, '')
                    is_focus  = r.get('is_focus', 0)
                    bold_cls  = 'font-bold text-slate-800' if is_focus else 'text-slate-600'
                    rank_cls  = 'font-bold text-slate-700' if is_focus else 'text-slate-400'
                    pts_str   = str(r['points']) if r['points'] is not None else '-'
                    with ui.row().classes(
                        f'w-full items-center px-1 py-px gap-0 text-xs {zone_bg}'
                    ):
                        ui.label(str(r['rank'])).classes(f'w-5 text-right shrink-0 {rank_cls}')
                        name_lbl = ui.label(r['team_name']).classes(
                            f'flex-1 px-1 truncate {bold_cls}'
                        )
                        if is_focus:
                            name_lbl.tooltip('本场参赛队')
                        ui.label(pts_str).classes(f'w-8 text-right shrink-0 {bold_cls}')
