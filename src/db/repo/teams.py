"""
Repository: teams

Writes team dictionary records extracted from match_list results.
Both home and away teams from each match are written.
Strategy: INSERT OR IGNORE — team names are written once and never overwritten.
"""
import sqlite3


def upsert_teams(conn: sqlite3.Connection, records: list[dict]) -> int:
    """Insert team rows from home/away fields of match_list records.

    Each dict must contain: home_team_id, home_team_cn, home_team_en,
                            away_team_id, away_team_cn, away_team_en.
    Returns the number of unique team rows inserted.
    """
    seen: set[int] = set()
    rows: list[tuple] = []

    for r in records:
        for side in ("home", "away"):
            tid = _int(r.get(f"{side}_team_id"))
            if tid is None or tid in seen:
                continue
            seen.add(tid)
            rows.append((
                tid,
                r.get(f"{side}_team_cn") or None,
                r.get(f"{side}_team_en") or None,
            ))

    if not rows:
        return 0

    with conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO teams (team_id, team_name_cn, team_name_en)
            VALUES (?, ?, ?)
            """,
            rows,
        )
    return len(rows)


def ensure_team(conn: sqlite3.Connection, team_id: int, name_cn: str) -> None:
    """仅在球队不存在时插入一行最小骨架记录，不覆盖已有数据。

    用于"直接 URL 抓取"场景：match_detail 页面能获取到 team_id 和中文队名，
    但没有英文名；INSERT OR IGNORE 保证不会降级已有的完整行。
    """
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO teams (team_id, team_name_cn) VALUES (?, ?)",
            (team_id, name_cn or None),
        )


def refresh_team_name(conn: sqlite3.Connection, team_id: int, name_cn: str) -> None:
    """插入或刷新球队中文名。

    与 ensure_team 不同，此函数在球队已存在时也会更新 team_name_cn，
    适用于从 match_detail 页面取到权威队名的场景。
    name_cn 为空时不覆盖已有值。
    """
    with conn:
        conn.execute(
            """
            INSERT INTO teams (team_id, team_name_cn) VALUES (?, ?)
            ON CONFLICT(team_id) DO UPDATE SET
                team_name_cn = CASE
                    WHEN excluded.team_name_cn IS NOT NULL AND excluded.team_name_cn != ''
                    THEN excluded.team_name_cn
                    ELSE teams.team_name_cn
                END
            """,
            (team_id, name_cn or None),
        )


def _int(val) -> int | None:
    try:
        return int(val)
    except (TypeError, ValueError):
        return None
