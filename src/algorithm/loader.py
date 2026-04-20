"""
算法数据加载器

提供 load_match(mid) 和 load_match_from_history(mid) 两个入口函数，
将数据库中的所有比赛数据整合成一个扁平字典，无需了解 SQL。

用法示例：
    from src.algorithm import load_match

    data = load_match(12345)
    if data is None:
        print("赛事不存在或未抓取")
    else:
        print(data['home_team'], 'vs', data['away_team'])
        print("主队积分：", data['home_pts'])
        print("威廉希尔开盘：", data['odds']['wh']['open'])

注意：赔率数值为格式化字符串（如 "1.50"），需转为浮点数时用 float(v)。
"""

from src.ui.page.conclusion.queries import load_all_from_quant
from src.db.repo.history import load_snapshot


def load_match(mid: int) -> dict | None:
    """从实时数据库加载指定比赛的完整数据。

    Args:
        mid: 赛事 ID（即 schedule_id）

    Returns:
        包含所有数据的字典，详见 FIELDS.md；赛事不存在时返回 None。
    """
    raw = load_all_from_quant(mid)
    if raw.get('match') is None:
        return None
    return _flatten(raw)


def load_match_from_history(mid: int) -> dict | None:
    """从历史快照数据库加载已保存比赛的完整数据。

    Args:
        mid: 赛事 ID（即 schedule_id），与 load_match 相同。

    Returns:
        结构与 load_match 完全相同的字典；快照不存在时返回 None。
    """
    raw = load_snapshot(mid)
    if raw is None or raw.get('match') is None:
        return None
    return _flatten(raw)


def _flatten(raw: dict) -> dict:
    """将 load_all_from_quant / load_snapshot 的嵌套结构展开为扁平字典。"""
    m       = raw['match']
    extras  = raw.get('extras') or {}
    recent  = raw.get('recent') or {}
    h2h_raw = raw.get('h2h') or {}
    odds    = raw.get('odds') or {}

    return {
        # ── 基本赛事信息 ──────────────────────────────────────────────────
        'match_id':         m['schedule_id'],
        'match_time':       m.get('match_time') or '',
        'league':           m.get('league') or '',
        'home_team':        m.get('home_team') or '',
        'away_team':        m.get('away_team') or '',
        'home_rank':        m.get('home_rank'),
        'away_rank':        m.get('away_rank'),
        'home_score':       m.get('home_score'),
        'away_score':       m.get('away_score'),
        'home_half_score':  m.get('home_half_score'),
        'away_half_score':  m.get('away_half_score'),

        # ── 联赛积分与近期胜平负 ──────────────────────────────────────────
        'home_pts':  extras.get('home_pts'),
        'away_pts':  extras.get('away_pts'),
        # home_wdl / away_wdl 是 (胜场数, 平场数, 负场数) 元组，可能为 None
        'home_wdl':  extras.get('home_wdl'),
        'away_wdl':  extras.get('away_wdl'),

        # ── 近期比赛（各队最多 8 场）─────────────────────────────────────
        # 每条记录含 home_name / away_name / score / h30_odds / cur_odds
        'home_recent': recent.get('home') or [],
        'away_recent': recent.get('away') or [],

        # ── 历史交手（最多 8 场）─────────────────────────────────────────
        # 每条记录含 side / home_name / away_name / score / cur_odds
        'h2h': h2h_raw.get('rows') or [],
        # 站主队视角统计
        'h2h_summary': {
            'win':  h2h_raw.get('win', 0),
            'draw': h2h_raw.get('draw', 0),
            'loss': h2h_raw.get('loss', 0),
        },

        # ── 欧赔（三家博彩公司）──────────────────────────────────────────
        # open   含 win / draw / lose / payout / time（均为字符串）
        # history 列表，每条同 open + win_dir / draw_dir / lose_dir
        'odds': {
            'wh':    odds.get('William Hill'),   # 威廉希尔
            'coral': odds.get('Ladbrokes'),      # 立博
            '365':   odds.get('Bet365'),         # Bet365 欧赔
        },

        # ── 亚盘（Bet365）────────────────────────────────────────────────
        # open   含 hc / home / away / time；history 列表同 open + home_dir / away_dir
        # 若无数据则为 None
        'asian_odds': raw.get('asian_odds'),

        # ── 大小球（Bet365）──────────────────────────────────────────────
        # open   含 goals / over / under / time；history 列表同 open + over_dir / under_dir
        # 若无数据则为 None
        'over_under': raw.get('over_under'),

        # ── 联赛积分榜──────────────────────────────────────────────────
        # 含 total / home / away 三个列表
        # 每行含 rank / team_name / points / zone_flag / is_focus
        'league_table': raw.get('league_table') or {'total': [], 'home': [], 'away': []},
    }
