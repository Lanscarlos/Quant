"""
Repository: saved_matches / saved_snapshots (history.db)

Save, load, and list user-saved match analysis records.
"""
import csv
import io
import json
import sqlite3
import datetime as dt

from src.db import get_conn
from src.db.history_connection import get_history_conn
from src.ui.page.conclusion.queries import (
    query_match, query_header_extras, query_recent_matches,
    query_h2h, query_odds, query_asian_odds,
)


def _fmt(v) -> str:
    return f"{v:.2f}" if v is not None else '-'


def save_match(mid: int) -> int:
    """Read all data for *mid* from quant.db, write to history.db.

    Returns the saved_matches.id. Uses INSERT OR REPLACE on schedule_id,
    so re-saving the same match overwrites.
    """
    # ── Gather data from quant.db ─────────────────────────────────────
    match = query_match(mid)
    if not match:
        raise ValueError(f"赛事 {mid} 在 quant.db 中不存在")

    extras = query_header_extras(mid)
    recent = query_recent_matches(mid)
    h2h = query_h2h(mid)
    odds = query_odds(mid)
    asian_odds = query_asian_odds(mid)

    # ── Read raw odds from quant.db for denormalized columns ──────────
    qconn = get_conn()
    wh = qconn.execute(
        "SELECT open_win, open_draw, open_lose, cur_win, cur_draw, cur_lose "
        "FROM odds_wh WHERE schedule_id = ?", (mid,)
    ).fetchone()
    wh_h30 = qconn.execute("""
        SELECT win, draw, lose FROM odds_wh_history
        WHERE schedule_id = ? AND is_opening = 0
          AND change_time <= datetime(
                (SELECT match_time FROM matches WHERE schedule_id = ?),
                '-30 minutes')
        ORDER BY change_time DESC
        LIMIT 1
    """, (mid, mid)).fetchone()
    coral = qconn.execute(
        "SELECT open_win, open_draw, open_lose, cur_win, cur_draw, cur_lose "
        "FROM odds_coral WHERE schedule_id = ?", (mid,)
    ).fetchone()
    asian = qconn.execute(
        "SELECT open_handicap, open_home, open_away, cur_handicap, cur_home, cur_away "
        "FROM asian_odds_365 WHERE schedule_id = ?", (mid,)
    ).fetchone()

    home_wdl = extras.get('home_wdl')
    away_wdl = extras.get('away_wdl')

    # ── Write to history.db ───────────────────────────────────────────
    hconn = get_history_conn()
    with hconn:
        hconn.execute("""
            INSERT OR REPLACE INTO saved_matches (
                schedule_id, match_time, home_team, away_team, league,
                home_rank, away_rank,
                home_score, away_score, home_half_score, away_half_score,
                wh_open_win, wh_open_draw, wh_open_lose,
                wh_h30_win, wh_h30_draw, wh_h30_lose,
                wh_cur_win, wh_cur_draw, wh_cur_lose,
                coral_open_win, coral_open_draw, coral_open_lose,
                coral_cur_win, coral_cur_draw, coral_cur_lose,
                asian_open_handicap, asian_open_home, asian_open_away,
                asian_cur_handicap, asian_cur_home, asian_cur_away,
                home_pts, away_pts,
                home_wdl_win, home_wdl_draw, home_wdl_loss,
                away_wdl_win, away_wdl_draw, away_wdl_loss
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?, ?
            )
        """, (
            mid, match['match_time'], match['home_team'], match['away_team'], match['league'],
            match['home_rank'], match['away_rank'],
            match['home_score'], match['away_score'], match['home_half_score'], match['away_half_score'],
            wh[0] if wh else None, wh[1] if wh else None, wh[2] if wh else None,
            wh_h30[0] if wh_h30 else None, wh_h30[1] if wh_h30 else None, wh_h30[2] if wh_h30 else None,
            wh[3] if wh else None, wh[4] if wh else None, wh[5] if wh else None,
            coral[0] if coral else None, coral[1] if coral else None, coral[2] if coral else None,
            coral[3] if coral else None, coral[4] if coral else None, coral[5] if coral else None,
            asian[0] if asian else None, asian[1] if asian else None, asian[2] if asian else None,
            asian[3] if asian else None, asian[4] if asian else None, asian[5] if asian else None,
            extras.get('home_pts'), extras.get('away_pts'),
            home_wdl[0] if home_wdl else None, home_wdl[1] if home_wdl else None, home_wdl[2] if home_wdl else None,
            away_wdl[0] if away_wdl else None, away_wdl[1] if away_wdl else None, away_wdl[2] if away_wdl else None,
        ))

        # Get the id (may be new or replaced)
        row = hconn.execute(
            "SELECT id FROM saved_matches WHERE schedule_id = ?", (mid,)
        ).fetchone()
        saved_id = row[0]

        # Snapshot JSON
        snapshot = {
            'match': match,
            'extras': extras,
            'recent': recent,
            'h2h': h2h,
            'odds': odds,
            'asian_odds': asian_odds,
        }
        hconn.execute("""
            INSERT OR REPLACE INTO saved_snapshots (
                saved_match_id, match_json, extras_json,
                recent_json, h2h_json, odds_json, asian_odds_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            saved_id,
            json.dumps(snapshot['match'], ensure_ascii=False),
            json.dumps(snapshot['extras'], ensure_ascii=False),
            json.dumps(snapshot['recent'], ensure_ascii=False),
            json.dumps(snapshot['h2h'], ensure_ascii=False),
            json.dumps(snapshot['odds'], ensure_ascii=False),
            json.dumps(snapshot['asian_odds'], ensure_ascii=False),
        ))

    return saved_id


def load_snapshot(schedule_id: int) -> dict | None:
    """Load a saved match snapshot from history.db.

    Returns a dict with the same structure as load_all_from_quant():
    {match, extras, recent, h2h, odds, asian_odds}
    """
    hconn = get_history_conn()
    row = hconn.execute("""
        SELECT s.match_json, s.extras_json, s.recent_json,
               s.h2h_json, s.odds_json, s.asian_odds_json
        FROM saved_snapshots s
        JOIN saved_matches m ON m.id = s.saved_match_id
        WHERE m.schedule_id = ?
    """, (schedule_id,)).fetchone()
    if not row:
        return None
    from src.ui.page.conclusion.queries import query_league_table
    return {
        'match':        json.loads(row[0]) if row[0] else None,
        'extras':       json.loads(row[1]) if row[1] else {},
        'recent':       json.loads(row[2]) if row[2] else {'home': [], 'away': []},
        'h2h':          json.loads(row[3]) if row[3] else {'rows': [], 'win': 0, 'draw': 0, 'loss': 0},
        'odds':         json.loads(row[4]) if row[4] else {},
        'asian_odds':   json.loads(row[5]) if row[5] else None,
        'league_table': query_league_table(schedule_id),
    }


_ODDS_COLS = frozenset({
    'wh_open_win', 'wh_open_draw', 'wh_open_lose',
    'wh_cur_win', 'wh_cur_draw', 'wh_cur_lose',
    'coral_open_win', 'coral_open_draw', 'coral_open_lose',
    'coral_cur_win', 'coral_cur_draw', 'coral_cur_lose',
})

# CSV 导出用的列字段和中文表头
_CSV_FIELDS = ['idx', 'match_time', 'home_team', 'away_team', 'league',
               'open_odds', 'h30_odds', 'cur_odds', 'asian', 'analysis', 'score']
_CSV_HEADERS = ['序号', '赛事时间', '主队', '客队', '联赛',
                '初始赔率(威廉)', '赛前半小时赔率', '最终赔率',
                '最终亚盘', '分析结论', '赛果']


def _build_where_clause(filters: dict | None) -> tuple[str, list]:
    """根据 filters 构建 SQL WHERE 子句和参数列表。

    不处理 limit，调用方自行处理。
    Returns:
        (where_sql, params) — where_sql 为完整的 "WHERE ..." 或空串。
    """
    conditions: list[str] = []
    params: list = []

    if filters:
        if 'time_from' in filters:
            conditions.append("match_time >= ?")
            params.append(filters['time_from'])
        if 'time_to' in filters:
            conditions.append("match_time <= ?")
            params.append(filters['time_to'] + ' 23:59:59')
        if 'league' in filters:
            vals = filters['league']
            ph = ','.join('?' * len(vals))
            conditions.append(f"league IN ({ph})")
            params.extend(vals)
        if 'team' in filters:
            vals = filters['team']
            ph = ','.join('?' * len(vals))
            role = filters.get('team_role', 'both')
            if role == 'home':
                conditions.append(f"home_team IN ({ph})")
                params.extend(vals)
            elif role == 'away':
                conditions.append(f"away_team IN ({ph})")
                params.extend(vals)
            else:
                conditions.append(f"(home_team IN ({ph}) OR away_team IN ({ph}))")
                params.extend(vals + vals)
        col = filters.get('odds_type')
        if col and col in _ODDS_COLS:
            if 'odds_min' in filters:
                conditions.append(f"{col} >= ?")
                params.append(filters['odds_min'])
            if 'odds_max' in filters:
                conditions.append(f"{col} <= ?")
                params.append(filters['odds_max'])

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    return where, params


def backfill_recent_h2h() -> int:
    """补全老快照中 recent/h2h 不足 8 条的记录。

    老版本每侧近期赛事最多 6 条、交手查询限 6 条。本函数扫描 saved_snapshots，
    若对应 quant.db 中仍保留完整原始数据，则重新生成 recent_json / h2h_json。
    quant.db 中数据已被清理的快照静默跳过。返回实际重写的记录数。
    """
    hconn = get_history_conn()

    rows = hconn.execute("""
        SELECT m.id, m.schedule_id, s.recent_json, s.h2h_json
        FROM saved_matches m
        JOIN saved_snapshots s ON s.saved_match_id = m.id
    """).fetchall()

    updated = 0
    for row in rows:
        saved_id, mid = row[0], row[1]
        recent_raw, h2h_raw = row[2], row[3]

        try:
            recent = json.loads(recent_raw) if recent_raw else {'home': [], 'away': []}
            h2h    = json.loads(h2h_raw) if h2h_raw else {'rows': []}
        except (TypeError, ValueError):
            continue

        home_len = len(recent.get('home') or [])
        away_len = len(recent.get('away') or [])
        h2h_len  = len((h2h or {}).get('rows') or [])

        need_recent = home_len < 8 or away_len < 8
        need_h2h    = h2h_len < 8
        if not need_recent and not need_h2h:
            continue

        new_recent_json = None
        new_h2h_json    = None

        if need_recent:
            fresh = query_recent_matches(mid)
            fresh_home = len(fresh.get('home') or [])
            fresh_away = len(fresh.get('away') or [])
            # 仅在 quant.db 有更多数据时重写，避免无意义覆盖
            if fresh_home > home_len or fresh_away > away_len:
                new_recent_json = json.dumps(fresh, ensure_ascii=False)

        if need_h2h:
            fresh_h2h = query_h2h(mid)
            if len(fresh_h2h.get('rows') or []) > h2h_len:
                new_h2h_json = json.dumps(fresh_h2h, ensure_ascii=False)

        if new_recent_json is None and new_h2h_json is None:
            continue

        sets, params = [], []
        if new_recent_json is not None:
            sets.append('recent_json = ?')
            params.append(new_recent_json)
        if new_h2h_json is not None:
            sets.append('h2h_json = ?')
            params.append(new_h2h_json)
        params.append(saved_id)

        with hconn:
            hconn.execute(
                f"UPDATE saved_snapshots SET {', '.join(sets)} WHERE saved_match_id = ?",
                params,
            )
        updated += 1

    return updated


def backfill_h30() -> int:
    """Backfill wh_h30_* columns for existing saved_matches rows that have NULL values.

    Queries quant.db for each affected schedule_id. Silently skips matches
    whose history is no longer in quant.db. Returns the number of rows updated.
    """
    hconn = get_history_conn()
    qconn = get_conn()

    null_rows = hconn.execute(
        "SELECT id, schedule_id FROM saved_matches WHERE wh_h30_win IS NULL"
    ).fetchall()
    if not null_rows:
        return 0

    updated = 0
    for row in null_rows:
        saved_id, mid = row[0], row[1]
        h30 = qconn.execute("""
            SELECT win, draw, lose FROM odds_wh_history
            WHERE schedule_id = ? AND is_opening = 0
              AND change_time <= datetime(
                    (SELECT match_time FROM matches WHERE schedule_id = ?),
                    '-30 minutes')
            ORDER BY change_time DESC
            LIMIT 1
        """, (mid, mid)).fetchone()
        if not h30:
            continue
        with hconn:
            hconn.execute(
                "UPDATE saved_matches SET wh_h30_win=?, wh_h30_draw=?, wh_h30_lose=? WHERE id=?",
                (h30[0], h30[1], h30[2], saved_id),
            )
        updated += 1
    return updated


def list_distinct_leagues() -> list[str]:
    """Return sorted list of distinct league names in saved_matches."""
    hconn = get_history_conn()
    rows = hconn.execute(
        "SELECT DISTINCT league FROM saved_matches WHERE league IS NOT NULL ORDER BY league"
    ).fetchall()
    return [r[0] for r in rows]


def list_distinct_teams() -> list[str]:
    """Return sorted list of distinct team names (home + away combined) in saved_matches."""
    hconn = get_history_conn()
    rows = hconn.execute("""
        SELECT DISTINCT team FROM (
            SELECT home_team AS team FROM saved_matches WHERE home_team IS NOT NULL
            UNION
            SELECT away_team FROM saved_matches WHERE away_team IS NOT NULL
        ) ORDER BY team
    """).fetchall()
    return [r[0] for r in rows]


def list_saved_matches(filters: dict | None = None) -> list[dict]:
    """Query saved matches for the history list page, with optional filtering.

    Supported filter keys:
      time_from  — match_time >= value
      time_to    — match_time <= value + ' 23:59:59'
      league     — list[str], exact IN match
      team       — list[str], exact IN match on home/away (controlled by team_role)
      team_role  — 'home' | 'away' | 'both' (default 'both')
      odds_type  — column name (must be in _ODDS_COLS whitelist)
      odds_min   — odds_type column >= value
      odds_max   — odds_type column <= value
      limit      — LIMIT n
    """
    hconn = get_history_conn()
    where, params = _build_where_clause(filters)
    limit = f"LIMIT {int(filters['limit'])}" if filters and 'limit' in filters else ""

    rows = hconn.execute(f"""
        SELECT id, schedule_id, saved_at, match_time,
               home_team, away_team, league,
               wh_open_win, wh_open_draw, wh_open_lose,
               wh_h30_win, wh_h30_draw, wh_h30_lose,
               wh_cur_win, wh_cur_draw, wh_cur_lose,
               asian_cur_handicap, asian_cur_home, asian_cur_away,
               home_score, away_score, analysis_note
        FROM saved_matches
        {where}
        ORDER BY saved_at DESC
        {limit}
    """, params).fetchall()

    result = []
    for i, r in enumerate(rows, 1):
        hs, as_ = r[19], r[20]
        score = f"{hs}:{as_}" if hs is not None and as_ is not None else '-'
        asian_str = '-'
        if r[16] is not None:
            asian_str = f"{_fmt(r[17])} / {r[16]} / {_fmt(r[18])}"
        h30_str = '-'
        if r[10] is not None:
            h30_str = f"{_fmt(r[10])} / {_fmt(r[11])} / {_fmt(r[12])}"
        result.append({
            'idx':        i,
            'id':         r[1],  # schedule_id — used for row click
            'match_time': r[3] or '-',
            'home_team':  r[4] or '',
            'away_team':  r[5] or '',
            'league':     r[6] or '',
            'open_odds':  f"{_fmt(r[7])} / {_fmt(r[8])} / {_fmt(r[9])}",
            'h30_odds':   h30_str,
            'cur_odds':   f"{_fmt(r[13])} / {_fmt(r[14])} / {_fmt(r[15])}",
            'asian':      asian_str,
            'analysis':   r[21] or '',
            'score':      score,
        })
    return result


def export_to_json(filters: dict | None) -> str:
    """将筛选后的 saved_matches + saved_snapshots 序列化为 JSON 字符串（UTF-8）。

    用于数据完整迁移，包含所有原始字段和 JSON 快照。
    """
    hconn = get_history_conn()
    where, params = _build_where_clause(filters)
    rows = hconn.execute(f"""
        SELECT m.*,
               s.match_json, s.extras_json, s.recent_json,
               s.h2h_json, s.odds_json, s.asian_odds_json
        FROM saved_matches m
        LEFT JOIN saved_snapshots s ON s.saved_match_id = m.id
        {where}
        ORDER BY m.saved_at DESC
    """, params).fetchall()

    records = []
    for r in rows:
        d = dict(r)
        snapshot = {}
        for key in ('match_json', 'extras_json', 'recent_json',
                    'h2h_json', 'odds_json', 'asian_odds_json'):
            raw = d.pop(key, None)
            field = key.replace('_json', '')
            snapshot[field] = json.loads(raw) if raw else None
        d['snapshot'] = snapshot
        records.append(d)

    payload = {
        'version':      1,
        'app':          'Quant',
        'exported_at':  dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'record_count': len(records),
        'records':      records,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


def export_to_csv(filters: dict | None) -> str:
    """将筛选后的数据序列化为 CSV 字符串（UTF-8-BOM，供 Excel/WPS 直接打开）。

    复用 list_saved_matches 的格式化输出，仅包含可读的平铺字段。
    """
    rows = list_saved_matches(filters)
    buf = io.StringIO()
    buf.write('\ufeff')  # BOM，确保 Excel/WPS 正确识别 UTF-8
    writer = csv.DictWriter(buf, fieldnames=_CSV_FIELDS, extrasaction='ignore')
    writer.writerow(dict(zip(_CSV_FIELDS, _CSV_HEADERS)))
    writer.writerows(rows)
    return buf.getvalue()


# saved_matches 中可导入的列（排除自增 id）
_IMPORT_MATCH_COLS = [
    'schedule_id', 'saved_at', 'match_time',
    'home_team', 'away_team', 'league',
    'home_rank', 'away_rank',
    'home_score', 'away_score', 'home_half_score', 'away_half_score',
    'wh_open_win', 'wh_open_draw', 'wh_open_lose',
    'wh_h30_win', 'wh_h30_draw', 'wh_h30_lose',
    'wh_cur_win', 'wh_cur_draw', 'wh_cur_lose',
    'coral_open_win', 'coral_open_draw', 'coral_open_lose',
    'coral_cur_win', 'coral_cur_draw', 'coral_cur_lose',
    'asian_open_handicap', 'asian_open_home', 'asian_open_away',
    'asian_cur_handicap', 'asian_cur_home', 'asian_cur_away',
    'home_pts', 'away_pts',
    'home_wdl_win', 'home_wdl_draw', 'home_wdl_loss',
    'away_wdl_win', 'away_wdl_draw', 'away_wdl_loss',
    'analysis_note', 'tags',
]

_SNAPSHOT_KEYS = ('match', 'extras', 'recent', 'h2h', 'odds', 'asian_odds')


def import_from_json(content: str, overwrite: bool = False) -> dict:
    """将 JSON 字符串导入到 history.db 的 saved_matches + saved_snapshots 中。

    仅接受 export_to_json 生成的格式（version=1）。

    Args:
        content:   JSON 文件内容字符串。
        overwrite: True 时覆盖已存在的同 schedule_id 记录；
                   False（默认）时跳过已存在记录。

    返回：{'imported': int, 'skipped': int, 'existed': int, 'errors': list[str]}
    """
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败：{e}") from e

    if payload.get('version') != 1:
        raise ValueError(
            f"不支持的文件版本（version={payload.get('version')}），仅支持 version=1"
        )

    records = payload.get('records')
    if not isinstance(records, list):
        raise ValueError("文件格式错误：缺少 records 字段")

    hconn = get_history_conn()
    cols_sql = ', '.join(_IMPORT_MATCH_COLS)
    placeholders = ', '.join('?' * len(_IMPORT_MATCH_COLS))
    conflict_clause = 'REPLACE' if overwrite else 'IGNORE'

    imported = 0
    skipped = 0
    existed = 0
    errors: list[str] = []

    with hconn:
        for rec in records:
            sid = rec.get('schedule_id')
            if not sid:
                skipped += 1
                errors.append("跳过一条缺少 schedule_id 的记录")
                continue

            try:
                values = [rec.get(col) for col in _IMPORT_MATCH_COLS]
                cur = hconn.execute(
                    f"INSERT OR {conflict_clause} INTO saved_matches ({cols_sql}) VALUES ({placeholders})",
                    values,
                )

                # INSERT OR IGNORE 在已有记录时 rowcount=0，跳过快照写入
                if cur.rowcount == 0:
                    existed += 1
                    continue

                row = hconn.execute(
                    "SELECT id FROM saved_matches WHERE schedule_id = ?", (sid,)
                ).fetchone()
                saved_id = row[0]

                snapshot = rec.get('snapshot')
                if snapshot and isinstance(snapshot, dict):
                    json_vals = [
                        json.dumps(snapshot.get(k), ensure_ascii=False) if snapshot.get(k) is not None else None
                        for k in _SNAPSHOT_KEYS
                    ]
                    hconn.execute("""
                        INSERT OR REPLACE INTO saved_snapshots (
                            saved_match_id, match_json, extras_json,
                            recent_json, h2h_json, odds_json, asian_odds_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, [saved_id] + json_vals)

                imported += 1

            except Exception as e:
                skipped += 1
                errors.append(f"赛事 {sid} 写入失败：{e}")

    return {'imported': imported, 'skipped': skipped, 'existed': existed, 'errors': errors}
