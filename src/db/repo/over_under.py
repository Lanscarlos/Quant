"""
Repository: over_under_365

写入 Bet365 大小球快照。
策略：INSERT OR REPLACE on schedule_id (PRIMARY KEY)。
"""
import sqlite3


def upsert_over_under_365(conn: sqlite3.Connection, schedule_id: int, r: dict) -> bool:
    """插入或替换一条 Bet365 大小球快照。

    若 matches 表中无对应记录（FK 守卫），返回 False。
    """
    if not conn.execute(
        "SELECT 1 FROM matches WHERE schedule_id = ?", (schedule_id,)
    ).fetchone():
        return False

    with conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO over_under_365 (
                schedule_id,
                open_goals, open_over, open_under,
                cur_goals,  cur_over,  cur_under
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                schedule_id,
                r.get("open_goals") or None,
                _float(r.get("open_over")),
                _float(r.get("open_under")),
                r.get("cur_goals") or None,
                _float(r.get("cur_over")),
                _float(r.get("cur_under")),
            ),
        )
    return True


def _float(val) -> float | None:
    try:
        v = str(val).strip()
        return float(v) if v else None
    except (TypeError, ValueError):
        return None
