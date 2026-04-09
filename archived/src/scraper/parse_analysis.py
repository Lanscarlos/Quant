import re
from bs4 import BeautifulSoup


def _int(cell) -> int:
    try:
        return int(cell.get_text(strip=True))
    except (ValueError, AttributeError):
        return 0


def _extract_team_stats(table) -> dict:
    """从 porlet_5 内单支球队的 TABLE 中提取排名、积分、近6场胜平负。"""
    stats = {"rank": 0, "points": 0, "wins": 0, "draws": 0, "losses": 0}
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) != 11:
            continue
        first = cells[0].get_text(strip=True)
        if first in ("全场", "半场"):   # 跳过表头行
            continue
        if first == "总":
            stats["points"] = _int(cells[8])
            stats["rank"] = _int(cells[9])
        elif first == "近6":
            stats["wins"] = _int(cells[2])
            stats["draws"] = _int(cells[3])
            stats["losses"] = _int(cells[4])
    return stats


def parse_match_data(html: str) -> dict:
    """解析 titan007 analysis 页面，返回 match_view 所需数据结构。"""
    soup = BeautifulSoup(html, "lxml")

    # ── 联赛名 ──────────────────────────────────────────────────────
    league_tag = soup.find("a", class_="LName")
    league = league_tag.get_text(strip=True) if league_tag else ""

    # ── 比赛时间 ─────────────────────────────────────────────────────
    time_m = re.search(r"var strTime = '([^']+)'", html)
    match_time = time_m.group(1) if time_m else ""

    # ── 队名 ─────────────────────────────────────────────────────────
    home_m = re.search(r'var hometeam = "([^"]+)"', html)
    away_m = re.search(r'var guestteam = "([^"]+)"', html)
    home_team = home_m.group(1) if home_m else ""
    away_team = away_m.group(1) if away_m else ""

    # ── 积分排名（porlet_5 → table[2]=主队全场, table[3]=客队全场）──
    porlet = soup.find("div", id="porlet_5")
    all_tables = porlet.find_all("table")
    home_stats = _extract_team_stats(all_tables[2])
    away_stats = _extract_team_stats(all_tables[3])

    return {
        "type": league,
        "time": match_time,
        "home_team": home_team,
        "away_team": away_team,
        "home_rank": home_stats["rank"],
        "home_points": home_stats["points"],
        "home_wins": home_stats["wins"],
        "home_draws": home_stats["draws"],
        "home_losses": home_stats["losses"],
        "away_rank": away_stats["rank"],
        "away_points": away_stats["points"],
        "away_wins": away_stats["wins"],
        "away_draws": away_stats["draws"],
        "away_losses": away_stats["losses"],
        # 暂无真实数据，保留占位（欧赔由 JS 动态加载，静态 HTML 无法获取）
        "full_odds": [
            {'主场': '-', '客场': '-', '比分': '-', '赔率(赛前半小时)': '-', '赔率(最终)': '-'},
        ],
        "half_odds": [
            {'主场': '-', '客场': '-', '比分': '-', '赔率(赛前半小时)': '-', '赔率(最终)': '-'},
        ],
        "wlh_odds": [
            {'胜': '-', '负': '-', '平': '-', '返还率': '-', '时间': '-'},
        ],
        "lb_odds": [
            {'胜': '-', '负': '-', '平': '-', '返还率': '-', '时间': '-'},
        ],
    }
