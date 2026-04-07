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
    should_fetch_history,
    should_fetch_asian_history,
)


# ── 阶段 1: 赛事详情 (排名 + 近期 + 交手) ──────────────────────────────────────

class StepMatchDetail:
    KEY   = 'match_detail'
    ICON  = 'sports_soccer'
    LABEL = '赛事详情 (排名 + 近期 + 交手)'
    PHASE = 1
    DEPENDS_ON: list[str] = []

    @staticmethod
    def should_skip(mid: int) -> tuple[bool, str]:
        if not should_fetch_detail(mid):
            return True, '数据仍然新鲜，已跳过'
        return False, ''

    @staticmethod
    async def fetch(mid: str, ctx: dict, on_progress=None) -> None:
        from src.service.match_detail import fetch_match_all
        result = await run.io_bound(fetch_match_all, mid, on_progress)
        ctx.update(result)


# ── 阶段 2: 欧赔数据 ────────────────────────────────────────────────────────────

class StepSubOdds:
    KEY   = 'sub_odds'
    ICON  = 'query_stats'
    LABEL = '子比赛赔率 (近六场 + 交手)'
    PHASE = 2
    DEPENDS_ON: list[str] = ['match_detail']

    @staticmethod
    def should_skip(mid: int) -> tuple[bool, str]:
        return False, ''

    @staticmethod
    async def fetch(mid: str, ctx: dict, on_progress=None) -> None:
        from ._sub_odds import fetch_sub_odds
        await run.io_bound(fetch_sub_odds, int(mid), on_progress)


class StepEuroOdds:
    KEY   = 'euro_odds'
    ICON  = 'analytics'
    LABEL = '欧赔数据 (威廉 / 立博)'
    PHASE = 3
    DEPENDS_ON: list[str] = []

    @staticmethod
    def should_skip(mid: int) -> tuple[bool, str]:
        if not should_fetch_odds(mid):
            return True, '数据仍然新鲜，已跳过'
        return False, ''

    @staticmethod
    async def fetch(mid: str, ctx: dict, on_progress=None) -> None:
        from src.service.euro_odds import fetch_euro_odds_with_record_ids
        record_ids = await run.io_bound(fetch_euro_odds_with_record_ids, mid)
        ctx['record_ids'] = record_ids


# ── 阶段 3: 365 亚盘数据 ────────────────────────────────────────────────────────

class StepAsianOdds:
    KEY   = 'asian_odds'
    ICON  = 'filter_list'
    LABEL = '365 亚盘数据'
    PHASE = 3
    DEPENDS_ON: list[str] = []

    @staticmethod
    def should_skip(mid: int) -> tuple[bool, str]:
        if not should_fetch_asian_odds(mid):
            return True, '数据仍然新鲜，已跳过'
        return False, ''

    @staticmethod
    async def fetch(mid: str, ctx: dict, on_progress=None) -> None:
        from src.service.asian_odds import fetch_asian_odds
        await run.io_bound(fetch_asian_odds, mid)


# ── 阶段 4: 欧赔变盘历史 ────────────────────────────────────────────────────────

class StepEuroHistory:
    KEY   = 'euro_history'
    ICON  = 'timeline'
    LABEL = '欧赔变盘历史'
    PHASE = 4
    DEPENDS_ON: list[str] = ['euro_odds']

    @staticmethod
    def should_skip(mid: int) -> tuple[bool, str]:
        if not should_fetch_history(mid):
            return True, '数据仍然新鲜，已跳过'
        return False, ''

    @staticmethod
    async def fetch(mid: str, ctx: dict, on_progress=None) -> None:
        from src.service.euro_odds_history import (
            fetch_euro_odds_history, COMPANY_WH, COMPANY_CORAL,
        )

        record_ids = ctx.get('record_ids') or _load_record_ids_from_db(int(mid))
        match_year = ctx.get('match_year') or _get_match_year(int(mid))

        tasks = []
        for cid in (COMPANY_WH, COMPANY_CORAL):
            rid = record_ids.get(cid)
            if rid:
                tasks.append(run.io_bound(fetch_euro_odds_history, rid, mid, cid, match_year))

        if tasks:
            await asyncio.gather(*tasks)
        else:
            raise ValueError('未找到威廉/立博的 record_id')


# ── 阶段 4: 365 亚盘变盘历史 ────────────────────────────────────────────────────

class StepAsianHistory:
    KEY   = 'asian_history'
    ICON  = 'swap_vert'
    LABEL = '365 亚盘变盘历史'
    PHASE = 4
    DEPENDS_ON: list[str] = []

    @staticmethod
    def should_skip(mid: int) -> tuple[bool, str]:
        if not should_fetch_asian_history(mid):
            return True, '数据仍然新鲜，已跳过'
        return False, ''

    @staticmethod
    async def fetch(mid: str, ctx: dict, on_progress=None) -> None:
        from src.service.asian_odds_history import fetch_asian_odds_history
        match_year = ctx.get('match_year') or _get_match_year(int(mid))
        await run.io_bound(fetch_asian_odds_history, mid, match_year)


# ── 有序步骤列表 & 分阶段分组 ────────────────────────────────────────────────────

STEPS = [StepMatchDetail, StepSubOdds, StepEuroOdds, StepAsianOdds, StepEuroHistory, StepAsianHistory]

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
    for table, cid in [("odds_wh", 115), ("odds_coral", 82)]:
        row = conn.execute(
            f"SELECT record_id FROM {table} WHERE schedule_id = ? AND record_id IS NOT NULL",
            (mid,),
        ).fetchone()
        if row:
            result[cid] = row[0]
    return result
