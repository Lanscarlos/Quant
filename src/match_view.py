import os
from nicegui import ui
from src.parse_analysis import parse_match_data

# 从本地 HTML 加载真实数据（后续替换为网络请求）
_HTML_PATH = os.path.join(os.path.dirname(__file__), "view-source_https___zq.titan007.com_analysis_2911120sb.html")
with open(_HTML_PATH, encoding="utf-8") as _f:
    _DATA = parse_match_data(_f.read())

_ODDS_COLS = [
    {'name': 'home',     'label': '主场',         'field': '主场',         'align': 'center'},
    {'name': 'away',     'label': '客场',         'field': '客场',         'align': 'center'},
    {'name': 'score',    'label': '比分',         'field': '比分',         'align': 'center'},
    {'name': 'pre_odds', 'label': '赔率(赛前半小时)', 'field': '赔率(赛前半小时)', 'align': 'center'},
    {'name': 'fin_odds', 'label': '赔率(最终)',    'field': '赔率(最终)',    'align': 'center'},
]

_BOOK_COLS = [
    {'name': 'win',    'label': '胜',   'field': '胜',   'align': 'center'},
    {'name': 'lose',   'label': '负',   'field': '负',   'align': 'center'},
    {'name': 'draw',   'label': '平',   'field': '平',   'align': 'center'},
    {'name': 'return', 'label': '返还率', 'field': '返还率', 'align': 'center'},
    {'name': 'time',   'label': '时间', 'field': '时间', 'align': 'center'},
]


def render():
    d = _DATA

    # ── 1. 头部：类型 + 时间 ─────────────────────────────────────────
    with ui.row().classes('w-full items-center gap-6 px-4 py-3 bg-blue-50 rounded-lg'):
        ui.label('比赛类型：').classes('font-bold text-gray-600')
        ui.label(d['type']).classes('font-bold text-blue-700')
        ui.label('比赛时间：').classes('font-bold text-gray-600 ml-10')
        ui.label(d['time']).classes('font-bold text-blue-700')

    ui.separator().classes('my-3')

    # ── 2. 主队 / 客队 信息 ──────────────────────────────────────────
    with ui.row().classes('w-full gap-4'):
        for side, team, rank, pts, w, d_, l in [
            ('主队', d['home_team'], d['home_rank'], d['home_points'],
             d['home_wins'], d['home_draws'], d['home_losses']),
            ('客队', d['away_team'], d['away_rank'], d['away_points'],
             d['away_wins'], d['away_draws'], d['away_losses']),
        ]:
            color = 'blue' if side == '主队' else 'red'
            with ui.card().classes('flex-1 p-3'):
                with ui.row().classes('items-center gap-2 mb-2'):
                    ui.badge(side, color=color).classes('text-xs')
                    ui.label(team).classes(f'font-bold text-lg text-{color}-700')

                with ui.row().classes('gap-8 mb-2'):
                    with ui.column().classes('items-center gap-0'):
                        ui.label('排名').classes('text-xs text-gray-400')
                        ui.label(str(rank)).classes('text-2xl font-bold')
                    with ui.column().classes('items-center gap-0'):
                        ui.label('积分').classes('text-xs text-gray-400')
                        ui.label(str(pts)).classes('text-2xl font-bold')

                with ui.row().classes('items-center gap-1'):
                    ui.label('近六场：').classes('text-xs text-gray-500')
                    ui.label(f'{w}胜').classes('text-xs font-bold text-green-600 bg-green-50 px-1 rounded')
                    ui.label(f'{d_}平').classes('text-xs font-bold text-yellow-600 bg-yellow-50 px-1 rounded')
                    ui.label(f'{l}负').classes('text-xs font-bold text-red-600 bg-red-50 px-1 rounded')

    ui.separator().classes('my-3')

    # ── 3. 赔率表：全场 / 半场 ──────────────────────────────────────
    with ui.row().classes('w-full gap-4'):
        for label, rows in [('全场赔率', d['full_odds']), ('半场赔率', d['half_odds'])]:
            with ui.column().classes('flex-1'):
                ui.label(label).classes('font-bold text-sm text-gray-600 mb-1')
                ui.table(
                    columns=_ODDS_COLS,
                    rows=rows,
                ).classes('w-full text-sm').props('dense flat bordered')

    ui.separator().classes('my-3')

    # ── 4. 投注公司赔率：威廉希尔 / 立博 ────────────────────────────
    with ui.row().classes('w-full gap-4'):
        for bookie, rows in [('威廉希尔', d['wlh_odds']), ('立博', d['lb_odds'])]:
            with ui.column().classes('flex-1'):
                ui.label(bookie).classes('font-bold text-sm text-gray-600 mb-1')
                ui.table(
                    columns=_BOOK_COLS,
                    rows=rows,
                ).classes('w-full text-sm').props('dense flat bordered')