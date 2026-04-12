"""历史数据页 — 常量定义."""

TABLE_COLS = [
    {'name': 'idx',      'label': '序号',          'field': 'idx',       'align': 'center', 'style': 'width:48px'},
    {'name': 'time',     'label': '时间',           'field': 'match_time', 'align': 'center', 'style': 'width:130px'},
    {'name': 'home',     'label': '主队',           'field': 'home_team', 'align': 'left'},
    {'name': 'away',     'label': '客队',           'field': 'away_team', 'align': 'left'},
    {'name': 'league',   'label': '联赛类型',       'field': 'league',    'align': 'left'},
    {'name': 'open',     'label': '初始赔率',       'field': 'open_odds', 'align': 'center'},
    {'name': 'h30',      'label': '赛前半小时赔率', 'field': 'h30_odds',  'align': 'center'},
    {'name': 'cur',      'label': '最终赔率',       'field': 'cur_odds',  'align': 'center'},
    {'name': 'asian',    'label': '最终亚盘',       'field': 'asian',     'align': 'center'},
    {'name': 'analysis', 'label': '分析结论',       'field': 'analysis',  'align': 'left'},
    {'name': 'result',   'label': '赛果输入',       'field': 'score',     'align': 'center'},
    {'name': 'detail',   'label': '详细信息',       'field': 'id',        'align': 'center', 'style': 'width:72px'},
]

PANEL_LEAGUES = ['胜赔', '章甲', '英超', '德甲', '西甲', '法甲', '荷甲', '欧冠']

ODDS_OPTIONS = {
    'wh_open_win':   '威廉 初始 胜',
    'wh_open_draw':  '威廉 初始 平',
    'wh_open_lose':  '威廉 初始 负',
    'wh_cur_win':    '威廉 即时 胜',
    'wh_cur_draw':   '威廉 即时 平',
    'wh_cur_lose':   '威廉 即时 负',
    'coral_open_win':  '立博 初始 胜',
    'coral_open_draw': '立博 初始 平',
    'coral_open_lose': '立博 初始 负',
    'coral_cur_win':   '立博 即时 胜',
    'coral_cur_draw':  '立博 即时 平',
    'coral_cur_lose':  '立博 即时 负',
}
