"""
league_table_snapshot 表的读写操作。

存储赛前联赛积分榜快照，包含总榜/主场榜/客场榜三个维度。
仅对 isShowIntegral == 1 的联赛赛事有数据。
"""
import sqlite3


def upsert_league_table(conn: sqlite3.Connection, record: dict) -> int:
    """将解析好的积分榜数据写入 league_table_snapshot 表。

    Args:
        conn: 数据库连接。
        record: 由 match_detail._parse_detail() 填充的字段，包含：
            - schedule_id (int)
            - home_team_id (int)  用于标记 is_focus
            - away_team_id (int)  用于标记 is_focus
            - league_table_total  (list[dict]) 总榜
            - league_table_home   (list[dict]) 主场榜
            - league_table_away   (list[dict]) 客场榜

    Returns:
        写入的行数。
    """
    total   = record.get("league_table_total")  or []
    home_lb = record.get("league_table_home")   or []
    away_lb = record.get("league_table_away")   or []

    if not (total or home_lb or away_lb):
        return 0

    sid      = int(record.get("schedule_id")   or 0)
    home_id  = int(record.get("home_team_id")  or 0)
    away_id  = int(record.get("away_team_id")  or 0)
    focus    = {home_id, away_id} - {0}

    rows: list[tuple] = []

    # ── total ────────────────────────────────────────────────────────────
    for entry in total:
        rows.append((
            sid,
            "total",
            entry["rank"],
            entry["team_id"],
            entry["team_name"],
            entry.get("points"),
            entry.get("zone_flag", -1),
            1 if entry["team_id"] in focus else 0,
        ))

    # ── home / away ───────────────────────────────────────────────────────
    for scope, lb in [("home", home_lb), ("away", away_lb)]:
        for entry in lb:
            rows.append((
                sid,
                scope,
                entry["rank"],
                entry["team_id"],
                entry["team_name"],
                entry.get("points"),
                -1,
                1 if entry["team_id"] in focus else 0,
            ))

    sql = """
        INSERT OR REPLACE INTO league_table_snapshot
            (schedule_id, scope, rank, team_id, team_name, points, zone_flag, is_focus)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    with conn:
        conn.executemany(sql, rows)
    return len(rows)


def load_league_table(
    conn: sqlite3.Connection,
    schedule_id: int,
    scope: str = "total",
) -> list[dict]:
    """读取指定赛事的积分榜快照。

    Args:
        schedule_id: 赛事 ID。
        scope: 'total' / 'home' / 'away'。

    Returns:
        按 rank 升序排列的行列表，每行为 dict。
    """
    rows = conn.execute(
        """
        SELECT rank, team_id, team_name, points, zone_flag, is_focus
        FROM   league_table_snapshot
        WHERE  schedule_id = ? AND scope = ?
        ORDER  BY rank
        """,
        (schedule_id, scope),
    ).fetchall()
    return [dict(r) for r in rows]
