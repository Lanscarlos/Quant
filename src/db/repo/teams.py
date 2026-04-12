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


def _int(val) -> int | None:
    try:
        return int(val)
    except (TypeError, ValueError):
        return None
