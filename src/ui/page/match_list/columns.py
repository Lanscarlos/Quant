"""赛事列表表格列定义。"""

TABLE_COLS = [
    {'name': 'idx',      'label': '序号',         'field': 'idx',      'align': 'center', 'style': 'width:48px'},
    {'name': 'time',     'label': '时间',         'field': 'match_time','align': 'center', 'style': 'width:130px'},
    {'name': 'home',     'label': '主队',         'field': 'home_team','align': 'left'},
    {'name': 'away',     'label': '客队',         'field': 'away_team','align': 'left'},
    {'name': 'league',   'label': '联赛类型',     'field': 'league',   'align': 'left'},
    {'name': 'open',     'label': '初始赔率',     'field': 'open_odds','align': 'center'},
    {'name': 'h30',      'label': '赛前半小时赔率','field': 'h30_odds', 'align': 'center'},
    {'name': 'cur',      'label': '最终赔率',     'field': 'cur_odds', 'align': 'center'},
    {'name': 'asian',    'label': '最终亚盘',     'field': 'asian',    'align': 'center'},
    {'name': 'analysis', 'label': '分析结论',     'field': 'analysis', 'align': 'left'},
    {'name': 'result',   'label': '赛果输入',     'field': 'score',    'align': 'center'},
    {'name': 'detail',   'label': '详细信息',     'field': 'id',       'align': 'center', 'style': 'width:72px'},
]
