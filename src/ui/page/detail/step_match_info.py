"""步骤1：抓取赛事基本信息 & 联赛比分."""
from nicegui import run

from src.service.archived.match_detail import fetch_match_detail

KEY   = 'match_info'
ICON  = 'search'
LABEL = '赛事信息 & 联赛比分'


async def fetch(mid: str) -> None:
    await run.io_bound(fetch_match_detail, mid)
