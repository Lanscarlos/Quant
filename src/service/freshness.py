"""
新鲜度决策助手。

should_fetch_*() 只做一件事：回答"要不要发 HTTP 请求"。
UI 层在调用 service 前先问一下，避免冗余抓取。

新鲜度阈值策略：
  完场 (-1):    detail/odds 只抓一次，有数据就永不重抓
  进行中 (1/3): odds 2 分钟过期；detail 不重抓
  未开赛 (0):   odds 10 分钟过期；detail 6 小时过期
"""
from datetime import datetime, timedelta

from src.db import get_conn


def _is_stale(fetched_at: str | None, threshold: timedelta) -> bool:
    """fetched_at 为空或超过 threshold 则视为过期。"""
    if fetched_at is None:
        return True
    return datetime.now() - datetime.fromisoformat(fetched_at) > threshold


def _match_status(schedule_id: int) -> int | None:
    row = get_conn().execute(
        "SELECT status FROM matches WHERE schedule_id = ?", (schedule_id,)
    ).fetchone()
    return int(row[0]) if row else None


# ── match_list ────────────────────────────────────────────────────────────────

_LIST_THRESHOLDS: dict[int, timedelta] = {
    1: timedelta(minutes=2),   # 上半场
    3: timedelta(minutes=2),   # 下半场
    0: timedelta(minutes=10),  # 未开赛
}


def match_ids_needing_refresh(filter_ids: list[int]) -> list[int]:
    """返回 filter_ids 中需要重新抓取的 ID 子集。

    规则：
      - 在 DB 中找不到记录 → 需抓
      - status = -1（完场）    → 跳过（永不重抓）
      - 其他状态              → 按 _LIST_THRESHOLDS 判断 fetched_at 是否过期
    """
    if not filter_ids:
        return []

    # 统一转为 int，避免外部传入字符串时导致 key 类型不匹配
    int_ids = [int(mid) for mid in filter_ids]
    placeholders = ",".join("?" * len(int_ids))
    rows = get_conn().execute(
        f"SELECT schedule_id, status, fetched_at FROM matches"
        f" WHERE schedule_id IN ({placeholders})",
        int_ids,
    ).fetchall()

    found = {int(r[0]): (int(r[1]), r[2]) for r in rows}
    result = []
    for mid in int_ids:
        if mid not in found:
            result.append(mid)   # 库里没有 → 需抓
            continue
        status, fetched_at = found[mid]
        if status == -1:
            continue             # 完场 → 永不重抓
        threshold = _LIST_THRESHOLDS.get(status, timedelta(minutes=10))
        if _is_stale(fetched_at, threshold):
            result.append(mid)
    return result


# ── match_detail ──────────────────────────────────────────────────────────────

_DETAIL_STALE = timedelta(hours=6)


def should_fetch_detail(schedule_id: int, *, status: int | None = None) -> bool:
    """True → 调用 fetch_match_detail()；False → 直接读 DB。"""
    conn = get_conn()
    row = conn.execute(
        "SELECT fetched_at FROM match_standings WHERE schedule_id = ? LIMIT 1",
        (schedule_id,),
    ).fetchone()
    if status is None:
        status = _match_status(schedule_id)
    if status == -1:
        if row is None:
            return True   # 完场：standings 完全没有，需要抓
        # standings 有，但积分榜快照尚未用新代码处理过 → 补抓一次
        lt_flag = conn.execute(
            "SELECT league_table_fetched FROM matches WHERE schedule_id = ?",
            (schedule_id,),
        ).fetchone()
        if not lt_flag or not lt_flag[0]:
            return True
        return False
    return _is_stale(row[0] if row else None, _DETAIL_STALE)


# ── match_odds_list ───────────────────────────────────────────────────────────

_ODDS_THRESHOLDS: dict[int, timedelta] = {
    1: timedelta(minutes=2),    # 上半场
    3: timedelta(minutes=2),    # 下半场
    0: timedelta(minutes=10),   # 未开赛
}
_ODDS_STALE_DEFAULT = timedelta(minutes=30)


def should_fetch_odds(schedule_id: int, *, status: int | None = None) -> bool:
    """True → 调用 fetch_match_odds_list()；False → 直接读 DB。"""
    conn = get_conn()
    if status is None:
        status = _match_status(schedule_id)
    if status == -1:
        count = conn.execute(
            "SELECT COUNT(*) FROM odds_wh WHERE schedule_id = ?", (schedule_id,)
        ).fetchone()[0]
        return count == 0       # 完场：有数据就不再抓
    row = conn.execute(
        "SELECT fetched_at FROM odds_wh WHERE schedule_id = ?", (schedule_id,)
    ).fetchone()
    threshold = _ODDS_THRESHOLDS.get(status, _ODDS_STALE_DEFAULT)
    return _is_stale(row[0] if row else None, threshold)


# ── match_asian_odds ──────────────────────────────────────────────────────────

def should_fetch_asian_odds(schedule_id: int, *, status: int | None = None) -> bool:
    """True → 调用 fetch_match_asian_handicap_list()；False → 直接读 DB。"""
    conn = get_conn()
    if status is None:
        status = _match_status(schedule_id)
    if status == -1:
        count = conn.execute(
            "SELECT COUNT(*) FROM asian_odds_365 WHERE schedule_id = ?", (schedule_id,)
        ).fetchone()[0]
        return count == 0
    row = conn.execute(
        "SELECT fetched_at FROM asian_odds_365 WHERE schedule_id = ?", (schedule_id,)
    ).fetchone()
    threshold = _ODDS_THRESHOLDS.get(status, _ODDS_STALE_DEFAULT)
    return _is_stale(row[0] if row else None, threshold)


# ── odds_history ──────────────────────────────────────────────────────────────

def should_fetch_history(schedule_id: int) -> bool:
    """True → 调用 fetch_odds_history()；False → 直接读 DB。"""
    count = get_conn().execute(
        "SELECT COUNT(*) FROM odds_wh_history WHERE schedule_id = ?", (schedule_id,)
    ).fetchone()[0]
    if _match_status(schedule_id) == -1:
        return count == 0       # 完场：抓过一次就不再抓
    return True                 # 进行中/未开赛：用户主动点击则总是刷新


# ── asian_odds_history ───────────────────────────────────────────────────────

def should_fetch_asian_history(schedule_id: int) -> bool:
    """True → 调用 fetch_asian_handicap_history()；False → 直接读 DB。"""
    count = get_conn().execute(
        "SELECT COUNT(*) FROM asian_odds_365_history WHERE schedule_id = ?", (schedule_id,)
    ).fetchone()[0]
    if _match_status(schedule_id) == -1:
        return count == 0   # 完场：抓过一次就不再抓
    return True