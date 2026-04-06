"""步骤2：抓取两队交手数据."""
from nicegui import run

from src.service.archived.match_detail import fetch_match_h2h

KEY   = 'h2h'
ICON  = 'people'
LABEL = '两队交手数据'


async def fetch(mid: str) -> None:
    await run.io_bound(fetch_match_h2h, mid)
