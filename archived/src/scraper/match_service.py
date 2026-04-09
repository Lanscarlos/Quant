import re
import requests
from src.scraper.parse_analysis import parse_match_data
from src.scraper.odds import fetch_odds
from src.scraper.odds_history import fetch_odds_history

_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def extract_match_id(url: str) -> str:
    """从 URL 中提取比赛 ID，如 .../2911120sb.htm → '2911120'"""
    m = re.search(r'/(\d+)sb\.htm', url)
    return m.group(1) if m else ''


def _get_bookie_history(game_df, match_id: str, company_keyword: str) -> list[dict]:
    _empty = [{'胜': '-', '平': '-', '负': '-', '返还率': '-', '时间': '-'}]
    if game_df.empty:
        return _empty
    match_rows = game_df[game_df['公司名'].str.contains(company_keyword, na=False)]
    if match_rows.empty:
        return _empty
    info = match_rows.iloc[0]
    return fetch_odds_history(info['记录ID'], match_id, info['公司ID'])


def fetch_match(url: str) -> dict:
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.encoding = "utf-8"
    d = parse_match_data(resp.text)

    match_id = extract_match_id(url)
    if match_id:
        game_df, _ = fetch_odds(match_id)
        d['wlh_odds'] = _get_bookie_history(game_df, match_id, 'William Hill')
        d['lb_odds']  = _get_bookie_history(game_df, match_id, '立博')

    return d