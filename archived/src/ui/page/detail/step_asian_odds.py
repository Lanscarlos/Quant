"""步骤4：抓取 365 亚盘数据."""
from nicegui import run

from src.service.archived.match_asian_handicap_list import fetch_match_asian_handicap_list

KEY   = 'asian_odds'
ICON  = 'filter_list'
LABEL = '365 亚盘数据'


async def fetch(mid: str) -> None:
    await run.io_bound(fetch_match_asian_handicap_list, mid)
