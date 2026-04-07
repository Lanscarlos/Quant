"""为近六场 & 交手子比赛批量抓取欧赔快照 + 变赔历史."""
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.db import get_conn
from src.service.match_detail import fetch_match_time
from src.service.euro_odds_history import fetch_euro_odds_history
from src.service.euro_odds import fetch_euro_odds

from src.ui.page.conclusion.formatters import parse_year

_WH_COMPANY_ID = 115


def fetch_sub_odds(mid: int) -> None:
    conn = get_conn()

    # 近六场子比赛
    recent_rows = conn.execute(
        "SELECT match_id, MAX(date), MAX(match_time) "
        "FROM match_recent WHERE schedule_id = ? GROUP BY match_id",
        (mid,),
    ).fetchall()

    # 交手子比赛
    h2h_rows = conn.execute(
        "SELECT match_id, MAX(date) "
        "FROM match_h2h WHERE schedule_id = ? GROUP BY match_id",
        (mid,),
    ).fetchall()

    # 合并去重: {match_id: (date_str, match_time_or_None, is_recent)}
    tasks: dict[int, tuple[str | None, str | None, bool]] = {}
    for r in recent_rows:
        tasks[r[0]] = (r[1], r[2], True)
    for r in h2h_rows:
        if r[0] not in tasks:
            tasks[r[0]] = (r[1], None, False)

    def _process_one(match_id: int, date_str: str | None,
                     existing_time: str | None, is_recent: bool) -> None:
        c = get_conn()

        # 1) 欧赔快照
        has_odds = c.execute(
            "SELECT 1 FROM odds_wh WHERE schedule_id = ? LIMIT 1", (match_id,)
        ).fetchone()
        if not has_odds:
            try:
                fetch_euro_odds(match_id)
            except Exception:
                return

        # 2) 欧赔变赔历史
        has_history = c.execute(
            "SELECT 1 FROM odds_wh_history WHERE schedule_id = ? LIMIT 1", (match_id,)
        ).fetchone()
        if not has_history:
            odds_row = c.execute(
                "SELECT record_id FROM odds_wh WHERE schedule_id = ?", (match_id,)
            ).fetchone()
            if odds_row and odds_row[0]:
                try:
                    fetch_euro_odds_history(
                        odds_row[0], match_id, _WH_COMPANY_ID,
                        parse_year(date_str),
                    )
                except Exception:
                    pass

        # 3) 近六场的 match_time 补全（赛前半小时赔率计算依赖）
        if is_recent and existing_time is None:
            mt = fetch_match_time(match_id)
            with c:
                c.execute(
                    "UPDATE match_recent SET match_time = ? "
                    "WHERE schedule_id = ? AND match_id = ?",
                    (mt or "", mid, match_id),
                )

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [
            pool.submit(_process_one, mid_, *info)
            for mid_, info in tasks.items()
        ]
        for f in as_completed(futures):
            try:
                f.result()
            except Exception:
                pass
