"""
Repository: over_under_365_history

写入 Bet365 大小球变盘历史。
策略：INSERT OR IGNORE on UNIQUE(schedule_id, change_time)，历史不可变。
"""
import sqlite3


def upsert_over_under_365_history(
    conn: sqlite3.Connection,
    schedule_id: int,
    records: list[dict],
    match_year: int,
) -> int:
    """插入 Bet365 大小球变盘历史行。

    Args:
        schedule_id: 赛事 schedule_id
        records:     over_under_history._fetch_and_parse() 的原始输出
        match_year:  赛事年份，用于补全 "MM-DD HH:MM" 时间戳
    Returns: 写入行数
    """
    from src.db.repo.asian_odds_history import _complete_time

    rows = []
    for r in records:
        raw_time = (r.get("change_time") or "").strip()
        change_time = _complete_time(raw_time, match_year)
        if not change_time:
            continue
        rows.append((
            schedule_id,
            change_time,
            r.get("score") or None,
            _float(r.get("over_odds")),
            r.get("goals_line") or None,
            _float(r.get("under_odds")),
            int(r.get("is_opening") or 0),
            r.get("over_dir") or None,
            r.get("under_dir") or None,
        ))

    if not rows:
        return 0

    with conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO over_under_365_history (
                schedule_id,
                change_time, score,
                over_odds, goals_line, under_odds,
                is_opening, over_dir, under_dir
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
    return len(rows)


def _float(val) -> float | None:
    try:
        v = str(val).strip()
        return float(v) if v else None
    except (TypeError, ValueError):
        return None
