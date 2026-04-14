"""
Repository: matches

Writes match snapshot records from match_list results.
Strategy: INSERT OR REPLACE — re-fetching updates scores, status, cards in place.
"""
import sqlite3


def upsert_matches(conn: sqlite3.Connection, records: list[dict]) -> int:
    """Insert or replace match rows from match_list records.

    Each dict is the raw output from match_list.fetch_match_list() —
    field names match the _FIELDS mapping in that module (e.g. "scheduleID").
    Returns the number of rows written.
    """
    rows = []
    for r in records:
        sid = _int(r.get("scheduleID"))
        home_tid = _int(r.get("home_team_id"))
        away_tid = _int(r.get("away_team_id"))
        if not (sid and home_tid and away_tid):
            continue
        rows.append((
            sid,
            r.get("match_time") or "",
            _int(r.get("status")) or 0,
            r.get("league_abbr") or None,
            home_tid,
            _int(r.get("home_rank")),
            away_tid,
            _int(r.get("away_rank")),
            _int(r.get("home_score")),
            _int(r.get("away_score")),
            _int(r.get("home_half_score")),
            _int(r.get("away_half_score")),
            _int(r.get("home_red_cards")) or 0,
            _int(r.get("away_red_cards")) or 0,
            _int(r.get("home_yellow_cards")) or 0,
            _int(r.get("away_yellow_cards")) or 0,
        ))

    if not rows:
        return 0

    with conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO matches (
                schedule_id, match_time, status, league_abbr,
                home_team_id, home_rank, away_team_id, away_rank,
                home_score, away_score, home_half_score, away_half_score,
                home_red_cards, away_red_cards, home_yellow_cards, away_yellow_cards
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
    return len(rows)


def upsert_match_basics(
    conn: sqlite3.Connection,
    schedule_id: int,
    match_time: str,
    home_team_id: int,
    away_team_id: int,
    league_name_cn: str | None = None,
) -> None:
    """插入或更新赛事基础信息（列表页专用）。

    使用 INSERT ... ON CONFLICT DO UPDATE，对已有行只更新非空字段，
    同时刷新 fetched_at（供 freshness 判断是否需要重抓）。
    """
    with conn:
        conn.execute(
            """
            INSERT INTO matches
                (schedule_id, match_time, status, home_team_id, away_team_id, league_name_cn)
            VALUES (?, ?, 0, ?, ?, ?)
            ON CONFLICT(schedule_id) DO UPDATE SET
                match_time     = excluded.match_time,
                home_team_id   = excluded.home_team_id,
                away_team_id   = excluded.away_team_id,
                league_name_cn = COALESCE(excluded.league_name_cn, matches.league_name_cn),
                fetched_at     = datetime('now', '+8 hours')
            """,
            (schedule_id, match_time, home_team_id, away_team_id, league_name_cn),
        )


def upsert_match_score(
    conn: sqlite3.Connection,
    schedule_id: int,
    home_score: int,
    away_score: int,
    status: int,
) -> None:
    """更新赛事比分与状态。

    若数据库中已是完赛状态（status=-1），则不再覆盖（幂等）。
    """
    with conn:
        conn.execute(
            """
            UPDATE matches
            SET home_score = ?, away_score = ?, status = ?
            WHERE schedule_id = ?
              AND (status != -1 OR ? = -1)
            """,
            (home_score, away_score, status, schedule_id, status),
        )


def ensure_match_stub(
    conn: sqlite3.Connection,
    schedule_id: int,
    match_time: str,
    home_team_id: int,
    away_team_id: int,
) -> None:
    """仅在赛事不存在时插入一行最小骨架记录，不覆盖已有数据。

    用于详情页流水线外键约束所需的最小占位行，
    不覆盖已有数据（INSERT OR IGNORE）。
    """
    with conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO matches
                (schedule_id, match_time, status, home_team_id, away_team_id)
            VALUES (?, ?, 0, ?, ?)
            """,
            (schedule_id, match_time, home_team_id, away_team_id),
        )


def _int(val) -> int | None:
    try:
        return int(val)
    except (TypeError, ValueError):
        return None