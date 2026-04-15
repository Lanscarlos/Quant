"""赛事列表网络抓取辅助：顺序抓取缺失/过期赛事数据，随机间隔避免触发反爬。

覆盖范围：
  1. 基础信息 + 实时比分
  2. 主赛事欧赔快照（威廉 + 立博）
  3. 威廉希尔欧赔变盘历史（h30 赛前半小时赔率列依赖）
  4. Bet365 亚盘快照

各类数据各自按新鲜度独立判断，不抓子赛事赔率。
"""
import random
import time
from datetime import datetime

from src.service.freshness import (
    match_ids_needing_refresh,
    should_fetch_odds,
    should_fetch_asian_odds,
    should_fetch_history,
)
from src.service.match_detail import fetch_match_basics
from src.service.live_score import fetch_live_score
from src.service.euro_odds import fetch_euro_odds_with_record_ids, COMPANY_WH
from src.service.euro_odds_history import fetch_euro_odds_history
from src.service.asian_odds import fetch_asian_odds


def hydrate_ids(ids: list, on_progress=None) -> None:
    """顺序抓取列表页所需数据，每次 HTTP 请求间随机间隔 2-5 秒。

    Args:
        ids: 需处理的赛事 ID 列表。
        on_progress: 可选回调 on_progress(done, total, mid)，每条赛事处理完后触发。
    """
    if not ids:
        return

    total = len(ids)
    stale_basics = set(match_ids_needing_refresh(ids))
    print(f"[hydrate_ids] ids={ids}  stale_basics={stale_basics}")
    req_count = [0]  # 已发 HTTP 请求计数，用于决定是否插入间隔

    def _throttle() -> None:
        """发起新 HTTP 请求前等待 2-5 秒随机间隔，首次不等待。"""
        if req_count[0] > 0:
            time.sleep(random.uniform(2.0, 5.0))
        req_count[0] += 1

    def _notify(done: int, mid: str) -> None:
        """安全触发进度回调，异常不外溢。"""
        if on_progress is None:
            return
        try:
            on_progress(done, total, mid)
        except Exception:
            pass

    for idx, mid in enumerate(ids, 1):
        mid_int = int(mid)
        needs_basics = mid_int in stale_basics
        needs_odds   = should_fetch_odds(mid_int)
        needs_asian  = should_fetch_asian_odds(mid_int)
        needs_hist   = should_fetch_history(mid_int)

        # 四类数据全部新鲜 → 跳过本赛事，不发请求
        if not (needs_basics or needs_odds or needs_asian or needs_hist):
            _notify(idx, mid)
            continue

        # 1) 基础信息 + 实时比分
        match_time: str | None = None
        if needs_basics:
            _throttle()
            try:
                basics = fetch_match_basics(mid)
                match_time = basics.get('match_time') if basics else None
                print(f"[hydrate_ids] fetch_match_basics({mid}) -> {basics}")
            except Exception as e:
                print(f"[hydrate_ids] fetch_match_basics({mid}) 异常: {e}")
            _throttle()
            try:
                fetch_live_score(mid, match_time)
            except Exception:
                pass
        else:
            match_time = _load_match_time(mid_int)

        # 2) 主赛事欧赔快照（威廉 + 立博）
        wh_record_id: int | None = None
        if needs_odds:
            _throttle()
            try:
                record_ids = fetch_euro_odds_with_record_ids(mid)
                wh_record_id = record_ids.get(COMPANY_WH)
            except Exception:
                pass

        # 3) 威廉希尔欧赔变盘历史（用于 h30 列）
        if needs_hist:
            if wh_record_id is None:
                wh_record_id = _load_wh_record_id(mid_int)
            if wh_record_id:
                _throttle()
                try:
                    fetch_euro_odds_history(
                        wh_record_id, mid, COMPANY_WH, _parse_year(match_time)
                    )
                except Exception:
                    pass

        # 4) Bet365 亚盘快照
        if needs_asian:
            _throttle()
            try:
                fetch_asian_odds(mid)
            except Exception:
                pass

        _notify(idx, mid)


def _load_match_time(mid: int) -> str | None:
    """从 DB 读取赛事开球时间，供跳过基础信息抓取时回退使用。"""
    from src.db import get_conn
    row = get_conn().execute(
        "SELECT match_time FROM matches WHERE schedule_id = ?", (mid,)
    ).fetchone()
    return row[0] if row and row[0] else None


def _load_wh_record_id(mid: int) -> int | None:
    """欧赔步骤因新鲜度跳过时，从 DB 反查威廉希尔的 record_id。"""
    from src.db import get_conn
    row = get_conn().execute(
        "SELECT record_id FROM odds_wh WHERE schedule_id = ? AND record_id IS NOT NULL",
        (mid,),
    ).fetchone()
    return row[0] if row else None


def _parse_year(match_time: str | None) -> int:
    """从 'YYYY-MM-DD HH:MM' 提取年份，失败则回退当前年份。"""
    if match_time and len(match_time) >= 4:
        try:
            return int(match_time[:4])
        except ValueError:
            pass
    return datetime.now().year
