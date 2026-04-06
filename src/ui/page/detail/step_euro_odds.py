"""步骤3：抓取欧赔数据."""
from nicegui import run

from src.service.archived.match_odds_list import fetch_match_odds_list

KEY   = 'euro_odds'
ICON  = 'analytics'
LABEL = '欧赔数据'


async def fetch(mid: str) -> None:
    await run.io_bound(fetch_match_odds_list, mid)
