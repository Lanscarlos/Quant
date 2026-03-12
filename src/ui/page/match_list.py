from nicegui import ui, run

from src.db import get_conn
from src.service.match_list import fetch_match_list
from src.sync.coordinator import should_fetch_match_list

_STATUS_LABEL = {
    0:   "未开赛",
    1:   "上半场",
    3:   "下半场",
    -1:  "完场",
    -11: "中断",
    -12: "腰斩",
    -14: "推迟",
}

_FILTER_OPTS = [
    ('全部',   None),
    ('未开赛', [0]),
    ('进行中', [1, 3]),
    ('完场',   [-1]),
]

_COLS = [
    {'name': 'match_time',   'label': '时间',   'field': 'match_time',   'align': 'left',   'sortable': True},
    {'name': 'league',       'label': '联赛',   'field': 'league',       'align': 'left'},
    {'name': 'home_team',    'label': '主队',   'field': 'home_team',    'align': 'right'},
    {'name': 'score',        'label': '比分',   'field': 'score',        'align': 'center'},
    {'name': 'away_team',    'label': '客队',   'field': 'away_team',    'align': 'left'},
    {'name': 'status_label', 'label': '状态',   'field': 'status_label', 'align': 'center'},
]


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
        hs, as_ = r[8], r[9]
        score = f"{hs} : {as_}" if hs is not None and as_ is not None else "- : -"
        home_rank = f" [{r[5]}]" if r[5] else ""
        away_rank = f"[{r[7]}] " if r[7] else ""
        result.append({
            'id':           r[0],
            'match_time':   r[1],
            'status':       status,
            'status_label': _STATUS_LABEL.get(status, str(status)),
            'league':       r[3],
            'home_team':    f"{r[4] or ''}{home_rank}",
            'away_team':    f"{away_rank}{r[6] or ''}",
            'score':        score,
        })
    return result


def render():
    current_filter: list[list[int] | None] = [None]

    with ui.column().classes('w-full h-full p-4 gap-3'):
        # ── 顶部工具栏 ────────────────────────────────────────────────
        with ui.row().classes('w-full items-center gap-3'):
            ui.label('赛事列表').classes('text-xl font-bold text-gray-700')
            ui.space()
            spinner = ui.spinner(size='sm').classes('hidden')
            err_label = ui.label('').classes('text-sm text-red-500')
            refresh_btn = ui.button('刷新', icon='refresh').props('unelevated')

        # ── 状态筛选 ──────────────────────────────────────────────────
        filter_btns: dict[str, ui.button] = {}
        with ui.row().classes('gap-2'):
            for label, _ in _FILTER_OPTS:
                btn = ui.button(label).props('unelevated') \
                    .classes('!bg-gray-100 !text-gray-500')
                filter_btns[label] = btn

        # ── 统计行 ────────────────────────────────────────────────────
        count_label = ui.label('').classes('text-sm text-gray-500')

        # ── 数据表 ────────────────────────────────────────────────────
        table = ui.table(columns=_COLS, rows=[], row_key='id') \
            .classes('w-full') \
            .props('dense flat bordered')

        def _set_filter(label: str, statuses: list[int] | None):
            current_filter[0] = statuses
            for lbl, btn in filter_btns.items():
                if lbl == label:
                    btn.classes(remove='!bg-gray-100 !text-gray-500',
                                add='!bg-blue-100 !text-blue-600')
                else:
                    btn.classes(remove='!bg-blue-100 !text-blue-600',
                                add='!bg-gray-100 !text-gray-500')
            _reload_table()

        def _reload_table():
            rows = _query_matches(current_filter[0])
            table.rows = rows
            count_label.set_text(f'共 {len(rows)} 场')

        async def _on_refresh():
            err_label.set_text('')
            spinner.classes(remove='hidden')
            refresh_btn.disable()
            try:
                counts = await run.io_bound(fetch_match_list)
                _reload_table()
                err_label.set_text(f'更新成功 leagues={counts["leagues"]} '
                                   f'teams={counts["teams"]} matches={counts["matches"]}')
            except Exception as exc:
                err_label.set_text(f'刷新失败：{exc}')
            finally:
                spinner.classes(add='hidden')
                refresh_btn.enable()

        # 绑定筛选按钮事件
        for label, statuses in _FILTER_OPTS:
            filter_btns[label].on_click(
                lambda lbl=label, st=statuses: _set_filter(lbl, st)
            )

        refresh_btn.on_click(_on_refresh)

        # 初始加载
        _set_filter('全部', None)

        # 若数据陈旧（DB 为空或超过 10 分钟），页面渲染后立即自动拉取一次
        async def _auto_fetch_if_stale():
            if should_fetch_match_list():
                await _on_refresh()

        ui.timer(0, _auto_fetch_if_stale, once=True)

        # 每 60 秒从 DB 刷新一次表格显示（跟进后台或手动刷新写入的新数据）
        ui.timer(60, _reload_table)