from collections import defaultdict
from datetime import datetime, date

from nicegui import ui, run

from src.db import get_conn
from src.service.match_list import fetch_match_list
from src.sync.coordinator import should_fetch_match_list

_PAGE_SIZE = 8   # 每页显示的联赛数

_STATUS_CONFIG = {
    0:   {'label': '未开赛', 'color': 'grey-5',      'live': False},
    1:   {'label': '上半场', 'color': 'green-6',     'live': True},
    3:   {'label': '下半场', 'color': 'green-6',     'live': True},
    -1:  {'label': '完场',   'color': 'blue-grey-4', 'live': False},
    -11: {'label': '中断',   'color': 'red-4',       'live': False},
    -12: {'label': '腰斩',   'color': 'red-4',       'live': False},
    -14: {'label': '推迟',   'color': 'orange-6',    'live': False},
}

_FILTER_OPTS = [
    ('全部',   None),
    ('未开赛', [0]),
    ('进行中', [1, 3]),
    ('完场',   [-1]),
]


def _fmt_time(dt_str: str) -> str:
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime('%H:%M') if dt.date() == date.today() else dt.strftime('%m/%d %H:%M')
    except Exception:
        return dt_str or '-'


def _query_matches(statuses: list[int] | None = None) -> list[dict]:
    conn = get_conn()
    rows = conn.execute("""
        SELECT
            m.schedule_id,
            m.match_time,
            m.status,
            COALESCE(l.league_name_cn, m.league_abbr, '') AS league,
            ht.team_name_cn AS home_team,
            m.home_rank,
            at.team_name_cn AS away_team,
            m.away_rank,
            m.home_score,
            m.away_score
        FROM matches m
        LEFT JOIN leagues l  ON m.league_abbr  = l.league_abbr
        LEFT JOIN teams   ht ON m.home_team_id = ht.team_id
        LEFT JOIN teams   at ON m.away_team_id = at.team_id
        ORDER BY m.match_time
    """).fetchall()

    result = []
    for r in rows:
        status = r[2]
        if statuses is not None and status not in statuses:
            continue
        cfg = _STATUS_CONFIG.get(status, {'label': str(status), 'color': 'grey', 'live': False})
        hs, as_ = r[8], r[9]
        score = f"{hs} : {as_}" if hs is not None and as_ is not None else "- : -"
        result.append({
            'id':           r[0],
            'match_time':   _fmt_time(r[1]),
            'status':       status,
            'status_label': cfg['label'],
            'status_color': cfg['color'],
            'is_live':      cfg['live'],
            'league':       r[3] or '未知联赛',
            'home_team':    r[4] or '',
            'home_rank':    r[5] or '',
            'away_team':    r[6] or '',
            'away_rank':    r[7] or '',
            'score':        score,
        })
    return result


def render():
    # 消除 ui.expansion 内容区域的默认内边距
    ui.add_css('.q-expansion-item__content { padding: 0 !important; }')

    current_filter: list[list[int] | None] = [None]
    current_page:   list[int]              = [0]
    cached_rows:    list[list[dict]]       = [[]]

    with ui.column().classes('w-full h-full gap-0'):

        # ── 顶部工具栏 ────────────────────────────────────────────────
        with ui.row().classes('w-full items-center gap-2 px-4 py-3 bg-white border-b border-slate-200'):
            ui.icon('sports_soccer').classes('text-xl text-blue-600')
            ui.label('赛事列表').classes('text-lg font-bold text-slate-700')
            ui.space()
            spinner     = ui.spinner(size='sm').classes('hidden')
            err_label   = ui.label('').classes('text-xs text-red-500')
            refresh_btn = ui.button('刷新', icon='refresh') \
                .props('unelevated size=sm') \
                .classes('!bg-blue-600 !text-white')

        # ── 状态筛选 + 统计 ───────────────────────────────────────────
        with ui.row().classes('w-full items-center gap-2 px-4 py-2 bg-white border-b border-slate-100'):
            filter_btns: dict[str, ui.button] = {}
            for lbl, _ in _FILTER_OPTS:
                btn = ui.button(lbl) \
                    .props('unelevated rounded size=sm') \
                    .classes('!bg-slate-100 !text-slate-500')
                filter_btns[lbl] = btn
            ui.space()
            count_label = ui.label('').classes('text-xs text-slate-400 pr-1')

        # ── 分页栏（固定在列表上方）─────────────────────────────────
        with ui.row().classes('w-full items-center justify-center gap-2 px-4 py-2 bg-white border-b border-slate-100'):
            prev_btn = ui.button(icon='chevron_left') \
                .props('unelevated round size=sm') \
                .classes('!bg-slate-100 !text-slate-500')
            page_label = ui.label('').classes('text-sm text-slate-400 w-16 text-center')
            next_btn = ui.button(icon='chevron_right') \
                .props('unelevated round size=sm') \
                .classes('!bg-slate-100 !text-slate-500')

        # ── 赛事列表 ─────────────────────────────────────────────────
        with ui.scroll_area().classes('w-full flex-1'):

            @ui.refreshable
            def match_area():
                rows   = cached_rows[0]
                groups: dict[str, list[dict]] = defaultdict(list)
                for row in rows:
                    groups[row['league']].append(row)

                league_names = list(groups.keys())
                total        = len(league_names)
                total_pages  = max(1, (total + _PAGE_SIZE - 1) // _PAGE_SIZE)
                page         = max(0, min(current_page[0], total_pages - 1))
                current_page[0] = page

                count_label.set_text(f'共 {total} 个联赛 · {len(rows)} 场')
                page_label.set_text(f'{page + 1}  /  {total_pages}')
                prev_btn.set_enabled(page > 0)
                next_btn.set_enabled(page < total_pages - 1)

                if not rows:
                    with ui.column().classes('w-full items-center py-20 gap-3'):
                        ui.icon('search_off').classes('text-5xl text-slate-300')
                        ui.label('暂无赛事数据').classes('text-slate-400 text-sm')
                    return

                page_leagues = league_names[page * _PAGE_SIZE:(page + 1) * _PAGE_SIZE]

                with ui.column().classes('w-full gap-0'):
                    for league in page_leagues:
                        _render_league_expansion(league, groups[league])

            def _prev_page():
                if current_page[0] > 0:
                    current_page[0] -= 1
                    match_area.refresh()

            def _next_page():
                n_leagues   = len(set(r['league'] for r in cached_rows[0]))
                total_pages = max(1, (n_leagues + _PAGE_SIZE - 1) // _PAGE_SIZE)
                if current_page[0] < total_pages - 1:
                    current_page[0] += 1
                    match_area.refresh()

            def _reload():
                cached_rows[0] = _query_matches(current_filter[0])
                current_page[0] = 0
                match_area.refresh()

            match_area()

    # ── 事件绑定 ──────────────────────────────────────────────────────

    def _set_filter(label: str, statuses: list[int] | None):
        current_filter[0] = statuses
        for lbl, btn in filter_btns.items():
            if lbl == label:
                btn.classes(remove='!bg-slate-100 !text-slate-500',
                            add='!bg-blue-100 !text-blue-600')
            else:
                btn.classes(remove='!bg-blue-100 !text-blue-600',
                            add='!bg-slate-100 !text-slate-500')
        _reload()

    async def _on_refresh():
        err_label.set_text('')
        spinner.classes(remove='hidden')
        refresh_btn.disable()
        try:
            counts = await run.io_bound(fetch_match_list)
            _reload()
            err_label.set_text(
                f'leagues={counts["leagues"]}  teams={counts["teams"]}  matches={counts["matches"]}'
            )
        except Exception as exc:
            err_label.set_text(f'刷新失败：{exc}')
        finally:
            spinner.classes(add='hidden')
            refresh_btn.enable()

    for lbl, statuses in _FILTER_OPTS:
        filter_btns[lbl].on_click(
            lambda lb=lbl, st=statuses: _set_filter(lb, st)
        )

    refresh_btn.on_click(_on_refresh)
    prev_btn.on_click(_prev_page)
    next_btn.on_click(_next_page)
    _set_filter('全部', None)

    async def _auto_fetch_if_stale():
        if should_fetch_match_list():
            await _on_refresh()

    ui.timer(0, _auto_fetch_if_stale, once=True)
    ui.timer(60, _reload)


def _render_league_expansion(league: str, matches: list[dict]):
    # header slot 使用 Vue 模板字符串，让 Quasar 的 expanded 变量控制图标方向
    header_slot = (
        f'<div style="display:flex;align-items:center;gap:8px;width:100%;'
        f'padding:8px 12px;background:#eff6ff;border-left:3px solid #3b82f6;cursor:pointer">'
        f'<q-icon name="emoji_events" style="font-size:14px;color:#3b82f6;flex-shrink:0" />'
        f'<span style="font-size:13px;font-weight:600;color:#1e40af;flex:1">{league}</span>'
        f'<span style="font-size:11px;color:#60a5fa;margin-right:4px">{len(matches)} 场</span>'
        f'<q-icon :name="expanded ? \'expand_less\' : \'expand_more\'"'
        f' style="font-size:18px;color:#93c5fd;flex-shrink:0;transition:transform .25s"'
        f' :style="{{transform: expanded ? \'rotate(0deg)\' : \'rotate(-90deg)\'}}" />'
        f'</div>'
    )

    exp = ui.expansion(value=True) \
        .props('dense hide-expand-icon') \
        .classes('w-full') \
        .style('border-bottom:1px solid #dbeafe')
    exp.add_slot('header', header_slot)

    with exp:
        with ui.column().classes('w-full gap-0'):
            for i, m in enumerate(matches):
                _render_match_row(m, odd=i % 2 == 1)


def _render_match_row(m: dict, odd: bool):
    is_live = m['is_live']
    row_bg  = '#f8fafc' if odd else '#ffffff'

    with ui.row().classes('w-full items-center') \
            .style(f'background:{row_bg};border-bottom:1px solid #f1f5f9;'
                   f'border-left:3px solid {"#16a34a" if is_live else "transparent"};'
                   f'padding:8px 12px 8px 10px') \
            .on('mouseover', js_handler='(e) => e.currentTarget.style.background="#eff6ff"') \
            .on('mouseout',  js_handler=f'(e) => e.currentTarget.style.background="{row_bg}"'):

        ui.label(m['match_time']) \
            .style('width:64px;font-size:12px;color:#94a3b8;flex-shrink:0')

        with ui.row().classes('items-center justify-end gap-1').style('flex:1;min-width:0'):
            ui.label(m['home_team']) \
                .style('font-size:13px;color:#1e293b;font-weight:500;'
                       'overflow:hidden;text-overflow:ellipsis;white-space:nowrap')
            if m['home_rank']:
                ui.label(str(m['home_rank'])) \
                    .style('font-size:10px;color:#94a3b8;background:#f1f5f9;'
                           'padding:1px 4px;border-radius:3px;flex-shrink:0')

        score_style = (
            'width:88px;text-align:center;font-size:15px;font-weight:700;'
            'letter-spacing:.08em;color:#15803d;flex-shrink:0'
            if is_live else
            'width:88px;text-align:center;font-size:14px;font-weight:600;'
            'letter-spacing:.06em;color:#374151;flex-shrink:0'
        )
        ui.label(m['score']).style(score_style)

        with ui.row().classes('items-center gap-1').style('flex:1;min-width:0'):
            if m['away_rank']:
                ui.label(str(m['away_rank'])) \
                    .style('font-size:10px;color:#94a3b8;background:#f1f5f9;'
                           'padding:1px 4px;border-radius:3px;flex-shrink:0')
            ui.label(m['away_team']) \
                .style('font-size:13px;color:#1e293b;font-weight:500;'
                       'overflow:hidden;text-overflow:ellipsis;white-space:nowrap')

        with ui.row().classes('items-center justify-end gap-1').style('width:72px;flex-shrink:0'):
            if is_live:
                ui.element('span') \
                    .classes('animate-pulse') \
                    .style('width:6px;height:6px;border-radius:50%;'
                           'background:#16a34a;display:inline-block;flex-shrink:0')
            ui.badge(m['status_label'], color=m['status_color']) \
                .style('font-size:11px;padding:2px 6px;border-radius:4px')
