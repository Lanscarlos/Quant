"""步骤2：抓取近六场比赛数据."""
from nicegui import run

from src.service.archived.match_detail import fetch_match_recent

KEY   = 'recent'
ICON  = 'history'
LABEL = '近六场比赛数据'


async def fetch(mid: str) -> None:
    await run.io_bound(fetch_match_recent, mid)
