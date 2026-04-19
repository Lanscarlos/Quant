"""Table column definitions for the conclusion page."""

RECENT_COLS = [
    {'name': 'home',  'label': '主场',          'field': 'home_name', 'align': 'left'},
    {'name': 'away',  'label': '客场',          'field': 'away_name', 'align': 'left'},
    {'name': 'score', 'label': '比分',          'field': 'score',     'align': 'center'},
    {'name': 'h30',   'label': '赛前半小时赔率', 'field': 'h30_odds',  'align': 'center'},
    {'name': 'cur',   'label': '最终赔率',      'field': 'cur_odds',  'align': 'center'},
]

H2H_COLS = [
    {'name': 'side',  'label': '主/客',  'field': 'side',      'align': 'center'},
    {'name': 'home',  'label': '主场',   'field': 'home_name', 'align': 'left'},
    {'name': 'away',  'label': '客场',   'field': 'away_name', 'align': 'left'},
    {'name': 'score', 'label': '比分',   'field': 'score',     'align': 'center'},
    {'name': 'cur',   'label': '最终赔率', 'field': 'cur_odds', 'align': 'center'},
]

ODDS_COLS = [
    {'name': 'win',    'label': '胜',    'field': 'win',    'align': 'center'},
    {'name': 'draw',   'label': '和',    'field': 'draw',   'align': 'center'},
    {'name': 'lose',   'label': '负',    'field': 'lose',   'align': 'center'},
    {'name': 'payout', 'label': '返还率', 'field': 'payout', 'align': 'center'},
    {'name': 'time',   'label': '时间',  'field': 'time',   'align': 'center'},
]

ASIAN_COLS = [
    {'name': 'home', 'label': '主队',    'field': 'home', 'align': 'center'},
    {'name': 'hc',   'label': '盘口',    'field': 'hc',   'align': 'center'},
    {'name': 'away', 'label': '客队',    'field': 'away', 'align': 'center'},
    {'name': 'time', 'label': '时间',    'field': 'time', 'align': 'center'},
    {'name': 'data', 'label': '对应数据', 'field': 'data', 'align': 'center'},
]

OVER_UNDER_COLS = [
    {'name': 'over',  'label': '大',      'field': 'over',  'align': 'center'},
    {'name': 'goals', 'label': '盘口',    'field': 'goals', 'align': 'center'},
    {'name': 'under', 'label': '小',      'field': 'under', 'align': 'center'},
    {'name': 'time',  'label': '时间',    'field': 'time',  'align': 'center'},
    {'name': 'data',  'label': '对应数据', 'field': 'data',  'align': 'center'},
]
