"""赛事列表的 DB 查询辅助函数。"""
from src.db import get_conn


def _f(v) -> str:
    """将数值格式化为两位小数，None 转 '-'。"""
    return f"{v:.2f}" if v is not None else '-'


def _fmt_asian(home, handicap, away) -> str:
    """亚盘格式化为 '主水 / 盘口 / 客水'，任一字段缺失则显示 '-'。"""
    if handicap is None or home is None or away is None:
        return '-'
    return f"{home:.2f} / {handicap} / {away:.2f}"


def query_filtered(ids: list) -> list[dict]:
    """按筛选白名单 ID 查询赛事列表所需的表格数据。"""
    conn = get_conn()
    if ids:
        placeholders = ",".join("?" * len(ids))
        rows = conn.execute(f"""
            SELECT
                m.schedule_id,
                m.match_time,
                COALESCE(ht.team_name_cn, '') AS home_team,
                COALESCE(at.team_name_cn, '') AS away_team,
                COALESCE(m.league_name_cn, '') AS league,
                o.open_win,  o.open_draw,  o.open_lose,
                (SELECT win  FROM odds_wh_history
                 WHERE schedule_id = m.schedule_id AND is_opening = 0
                   AND change_time <= datetime(m.match_time, '-30 minutes')
                 ORDER BY change_time DESC LIMIT 1) AS h30_win,
                (SELECT draw FROM odds_wh_history
                 WHERE schedule_id = m.schedule_id AND is_opening = 0
                   AND change_time <= datetime(m.match_time, '-30 minutes')
                 ORDER BY change_time DESC LIMIT 1) AS h30_draw,
                (SELECT lose FROM odds_wh_history
                 WHERE schedule_id = m.schedule_id AND is_opening = 0
                   AND change_time <= datetime(m.match_time, '-30 minutes')
                 ORDER BY change_time DESC LIMIT 1) AS h30_lose,
                o.cur_win,   o.cur_draw,   o.cur_lose,
                ao.cur_home, ao.cur_handicap, ao.cur_away,
                m.home_score, m.away_score
            FROM matches m
            LEFT JOIN teams           ht ON m.home_team_id = ht.team_id
            LEFT JOIN teams           at ON m.away_team_id = at.team_id
            LEFT JOIN odds_wh         o  ON o.schedule_id  = m.schedule_id
            LEFT JOIN asian_odds_365  ao ON ao.schedule_id = m.schedule_id
            WHERE CAST(m.schedule_id AS TEXT) IN ({placeholders})
            ORDER BY m.match_time ASC
        """, (*ids,)).fetchall()
    else:
        rows = []

    result = []
    for i, r in enumerate(rows, 1):
        hs, as_ = r[17], r[18]
        score = f"{hs}:{as_}" if hs is not None and as_ is not None else '-'
        h30_str = f"{_f(r[8])} / {_f(r[9])} / {_f(r[10])}" if r[8] is not None else '-'
        result.append({
            'idx':       i,
            'id':        r[0],
            'match_time': r[1] or '-',
            'home_team': r[2],
            'away_team': r[3],
            'league':    r[4],
            'open_odds': f"{_f(r[5])} / {_f(r[6])} / {_f(r[7])}",
            'h30_odds':  h30_str,
            'cur_odds':  f"{_f(r[11])} / {_f(r[12])} / {_f(r[13])}",
            'asian':     _fmt_asian(r[14], r[15], r[16]),
            'analysis':  '',
            'score':     score,
        })
    return result