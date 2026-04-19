"""
抓取步骤定义 — 分阶段、可并行、带依赖和新鲜度检查.

每个步骤包含:
  KEY / LABEL / ICON    — UI 展示
  PHASE                 — 执行阶段号，同阶段步骤并行执行
  DEPENDS_ON            — 依赖的步骤 KEY 列表，依赖失败则跳过
  should_skip(mid)      — 新鲜度检查，返回 (skip, reason)
  fetch(mid, ctx)       — 异步抓取，ctx 为步骤间共享上下文
"""
import asyncio
from datetime import datetime

from nicegui import run

from src.service.freshness import (
    should_fetch_detail,
    should_fetch_odds,
    should_fetch_asian_odds,
    should_fetch_over_under,
    should_fetch_history,
    should_fetch_asian_history,
    should_fetch_over_under_history,
)


# ── 阶段 1: 赛事详情 (排名 + 近期 + 交手) ──────────────────────────────────────

class StepMatchDetail:
    KEY   = 'match_detail'
    ICON  = 'sports_soccer'
    LABEL = '赛事详情 (排名 + 近期 + 交手)'
    PHASE = 1
    DEPENDS_ON: list[str] = []

    @staticmethod
    def should_skip(mid: int, force: bool = False) -> tuple[bool, str]:
        if force:
            return False, ''
        if not should_fetch_detail(mid):
            return True, '数据仍然新鲜，已跳过'
        return False, ''

    @staticmethod
    async def fetch(mid: str, ctx: dict, tracker=None) -> None:
        from src.service.match_detail import fetch_match_all
        result = await run.io_bound(fetch_match_all, mid, tracker)
        ctx.update(result)


# ── 阶段 2: 欧赔数据 ────────────────────────────────────────────────────────────

class StepSubOdds:
    KEY        = 'sub_odds'
    ICON       = 'query_stats'
    LABEL      = '子比赛赔率 (近六场 + 交手)'
    PHASE      = 2
    DEPENDS_ON: list[str] = ['match_detail']
    BACKGROUND = True   # 后台并发执行，不阻塞后续阶段

    @staticmethod
    def should_skip(mid: int, force: bool = False) -> tuple[bool, str]:
        if force:
            return False, ''
        from src.db import get_conn
        conn = get_conn()
        total = conn.execute(
            """
            SELECT COUNT(*) FROM (
                SELECT match_id FROM match_recent WHERE schedule_id = ?
                UNION
                SELECT match_id FROM match_h2h    WHERE schedule_id = ?
            )
            """, (mid, mid)
        ).fetchone()[0]
        if total == 0:
            return False, ''
        covered = conn.execute(
            """
            SELECT COUNT(*) FROM (
                SELECT match_id FROM match_recent WHERE schedule_id = ?
                UNION
                SELECT match_id FROM match_h2h    WHERE schedule_id = ?
            ) sub
            JOIN odds_wh ow ON ow.schedule_id = sub.match_id
            """, (mid, mid)
        ).fetchone()[0]
        if covered >= total:
            # 还需确认近期赛事的 match_time 已全部填充（h30 赔率依赖）
            missing_time = conn.execute(
                """
                SELECT COUNT(*) FROM match_recent
                WHERE schedule_id = ?
                  AND (match_time IS NULL OR match_time = '')
                """, (mid,)
            ).fetchone()[0]
            if missing_time == 0:
                return True, '子比赛赔率已存在，已跳过'
        return False, ''

    @staticmethod
    async def fetch(mid: str, ctx: dict, tracker=None) -> None:
        from ._sub_odds import fetch_sub_odds
        await run.io_bound(fetch_sub_odds, int(mid), tracker)


class StepEuroOdds:
    KEY   = 'euro_odds'
    ICON  = 'analytics'
    LABEL = '欧赔数据 (威廉 / 立博 / 365)'
    PHASE = 3
    DEPENDS_ON: list[str] = []

    @staticmethod
    def should_skip(mid: int, force: bool = False) -> tuple[bool, str]:
        if force:
            return False, ''
        if not should_fetch_odds(mid):
            return True, '数据仍然新鲜，已跳过'
        return False, ''

    @staticmethod
    async def fetch(mid: str, ctx: dict, tracker=None) -> None:
        from src.service.euro_odds import fetch_euro_odds_with_record_ids
        record_ids = await run.io_bound(fetch_euro_odds_with_record_ids, mid, tracker)
        ctx['record_ids'] = record_ids


# ── 阶段 3: 365 亚盘数据 ────────────────────────────────────────────────────────

class StepAsianOdds:
    KEY   = 'asian_odds'
    ICON  = 'filter_list'
    LABEL = '365 亚盘数据'
    PHASE = 3
    DEPENDS_ON: list[str] = []

    @staticmethod
    def should_skip(mid: int, force: bool = False) -> tuple[bool, str]:
        if force:
            return False, ''
        if not should_fetch_asian_odds(mid):
            return True, '数据仍然新鲜，已跳过'
        return False, ''

    @staticmethod
    async def fetch(mid: str, ctx: dict, tracker=None) -> None:
        from src.service.asian_odds import fetch_asian_odds
        await run.io_bound(fetch_asian_odds, mid, tracker)


# ── 阶段 3: 365 大小球数据 ──────────────────────────────────────────────────────

class StepOverUnder:
    KEY   = 'over_under'
    ICON  = 'straighten'
    LABEL = '365 大小球数据'
    PHASE = 3
    DEPENDS_ON: list[str] = []

    @staticmethod
    def should_skip(mid: int, force: bool = False) -> tuple[bool, str]:
        if force:
            return False, ''
        if not should_fetch_over_under(mid):
            return True, '数据仍然新鲜，已跳过'
        return False, ''

    @staticmethod
    async def fetch(mid: str, ctx: dict, tracker=None) -> None:
        from src.service.over_under import fetch_over_under
        await run.io_bound(fetch_over_under, mid, tracker)


# ── 阶段 4: 欧赔变盘历史 ────────────────────────────────────────────────────────

class StepEuroHistory:
    KEY   = 'euro_history'
    ICON  = 'timeline'
    LABEL = '欧赔变盘历史 (威廉 / 立博 / 365)'
    PHASE = 4
    DEPENDS_ON: list[str] = ['euro_odds']

    @staticmethod
    def should_skip(mid: int, force: bool = False) -> tuple[bool, str]:
        if force:
            return False, ''
        if not should_fetch_history(mid):
            return True, '数据仍然新鲜，已跳过'
        return False, ''

    @staticmethod
    async def fetch(mid: str, ctx: dict, tracker=None) -> None:
        from src.service.euro_odds_history import (
            fetch_euro_odds_history, COMPANY_WH, COMPANY_CORAL, COMPANY_365,
        )

        record_ids = ctx.get('record_ids') or _load_record_ids_from_db(int(mid))
        match_year = ctx.get('match_year') or _get_match_year(int(mid))

        tasks = []
        for cid in (COMPANY_WH, COMPANY_CORAL, COMPANY_365):
            rid = record_ids.get(cid)
            if rid:
                tasks.append(run.io_bound(fetch_euro_odds_history, rid, mid, cid, match_year, tracker))

        if tasks:
            await asyncio.gather(*tasks)
        else:
            raise ValueError('未找到欧赔 record_id')


# ── 阶段 4: 365 亚盘变盘历史 ────────────────────────────────────────────────────

class StepAsianHistory:
    KEY   = 'asian_history'
    ICON  = 'swap_vert'
    LABEL = '365 亚盘变盘历史'
    PHASE = 4
    DEPENDS_ON: list[str] = []

    @staticmethod
    def should_skip(mid: int, force: bool = False) -> tuple[bool, str]:
        if force:
            return False, ''
        if not should_fetch_asian_history(mid):
            return True, '数据仍然新鲜，已跳过'
        return False, ''

    @staticmethod
    async def fetch(mid: str, ctx: dict, tracker=None) -> None:
        from src.service.asian_odds_history import fetch_asian_odds_history
        match_year = ctx.get('match_year') or _get_match_year(int(mid))
        await run.io_bound(fetch_asian_odds_history, mid, match_year, tracker)


# ── 阶段 4: 365 大小球变盘历史 ──────────────────────────────────────────────────

class StepOverUnderHistory:
    KEY   = 'over_under_history'
    ICON  = 'trending_flat'
    LABEL = '365 大小球变盘历史'
    PHASE = 4
    DEPENDS_ON: list[str] = []

    @staticmethod
    def should_skip(mid: int, force: bool = False) -> tuple[bool, str]:
        if force:
            return False, ''
        if not should_fetch_over_under_history(mid):
            return True, '数据仍然新鲜，已跳过'
        return False, ''

    @staticmethod
    async def fetch(mid: str, ctx: dict, tracker=None) -> None:
        from src.service.over_under_history import fetch_over_under_history
        match_year = ctx.get('match_year') or _get_match_year(int(mid))
        await run.io_bound(fetch_over_under_history, mid, match_year, tracker)


# ── 有序步骤列表 & 分阶段分组 ────────────────────────────────────────────────────

STEPS = [
    StepMatchDetail, StepSubOdds,
    StepEuroOdds, StepAsianOdds, StepOverUnder,
    StepEuroHistory, StepAsianHistory, StepOverUnderHistory,
]

PHASES: list[list] = []
_phase_map: dict[int, list] = {}
for _s in STEPS:
    _phase_map.setdefault(_s.PHASE, []).append(_s)
for _p in sorted(_phase_map):
    PHASES.append(_phase_map[_p])


# ── 辅助函数 ─────────────────────────────────────────────────────────────────────

def _get_match_year(mid: int) -> int:
    """从 DB 获取赛事年份，作为 ctx 缺失时的回退。"""
    from src.db import get_conn
    row = get_conn().execute(
        "SELECT match_time FROM matches WHERE schedule_id = ?", (mid,)
    ).fetchone()
    if row and row[0] and len(row[0]) >= 4:
        try:
            return int(row[0][:4])
        except ValueError:
            pass
    return datetime.now().year


def _load_record_ids_from_db(mid: int) -> dict[int, int]:
    """从 DB 加载 record_ids，当欧赔步骤被跳过(新鲜度)时使用。"""
    from src.db import get_conn
    result = {}
    conn = get_conn()
    for table, cid in [("odds_wh", 115), ("odds_coral", 82), ("odds_365", 281)]:
        row = conn.execute(
            f"SELECT record_id FROM {table} WHERE schedule_id = ? AND record_id IS NOT NULL",
            (mid,),
        ).fetchone()
        if row:
            result[cid] = row[0]
    return result
