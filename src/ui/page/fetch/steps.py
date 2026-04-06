"""抓取步骤定义 — 每个步骤包含 KEY / LABEL / ICON / fetch()."""
from nicegui import run

from src.service.archived.match_detail import fetch_match_h2h, fetch_match_recent, fetch_match_standings
from src.service.archived.match_asian_handicap_list import fetch_match_asian_handicap_list
from src.service.archived.match_odds_list import fetch_match_odds_list


# ── 步骤 1: 赛事信息 & 联赛排名 ──────────────────────────────────────────────

class StepMatchInfo:
    KEY   = 'match_info'
    ICON  = 'search'
    LABEL = '赛事信息 & 联赛排名'

    @staticmethod
    async def fetch(mid: str) -> None:
        await run.io_bound(fetch_match_standings, mid)


# ── 步骤 2: 近六场比赛数据 ───────────────────────────────────────────────────

class StepRecent:
    KEY   = 'recent'
    ICON  = 'history'
    LABEL = '近六场比赛数据'

    @staticmethod
    async def fetch(mid: str) -> None:
        await run.io_bound(fetch_match_recent, mid)


# ── 步骤 3: 两队交手数据 ─────────────────────────────────────────────────────

class StepH2H:
    KEY   = 'h2h'
    ICON  = 'people'
    LABEL = '两队交手数据'

    @staticmethod
    async def fetch(mid: str) -> None:
        await run.io_bound(fetch_match_h2h, mid)


# ── 步骤 4: 欧赔数据 ─────────────────────────────────────────────────────────

class StepEuroOdds:
    KEY   = 'euro_odds'
    ICON  = 'analytics'
    LABEL = '欧赔数据'

    @staticmethod
    async def fetch(mid: str) -> None:
        await run.io_bound(fetch_match_odds_list, mid)


# ── 步骤 5: 365 亚盘数据 ─────────────────────────────────────────────────────

class StepAsianOdds:
    KEY   = 'asian_odds'
    ICON  = 'filter_list'
    LABEL = '365 亚盘数据'

    @staticmethod
    async def fetch(mid: str) -> None:
        await run.io_bound(fetch_match_asian_handicap_list, mid)


# 有序步骤列表
STEPS = [StepMatchInfo, StepRecent, StepH2H, StepEuroOdds, StepAsianOdds]
