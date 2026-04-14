"""赛事列表网络抓取辅助：并发补抓缺失/过期赛事。"""
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.service.freshness import match_ids_needing_refresh
from src.service.match_detail import fetch_match_basics
from src.service.live_score import fetch_live_score


def hydrate_ids(ids: list) -> None:
    """并发抓取缺失/过期赛事的基础信息与实时比分（最多 6 线程）。"""
    stale = match_ids_needing_refresh(ids)
    if not stale:
        return

    def _one(mid) -> None:
        basics = fetch_match_basics(mid)
        mt = basics.get('match_time') if basics else None
        fetch_live_score(mid, mt)

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(_one, mid) for mid in stale]
        for f in as_completed(futures):
            try:
                f.result()
            except Exception:
                pass
