# 算法数据加载器 API

## 概述

`src/algorithm/` 提供两个入口函数，将数据库中的所有比赛数据整合成一个扁平字典，无需了解 SQL。

```python
from src.algorithm import load_match, load_match_from_history
```

---

## 公开 API

### `load_match(mid: int) -> dict | None`

从实时数据库（quant.db）加载指定比赛的完整数据。

- **参数**：`mid` — 赛事 ID（即 schedule_id）
- **返回值**：包含所有数据的字典；赛事不存在时返回 `None`

### `load_match_from_history(mid: int) -> dict | None`

从历史快照数据库（history.db）加载已保存比赛的完整数据。

- **参数**：`mid` — 赛事 ID，与 `load_match` 相同
- **返回值**：结构与 `load_match` 完全相同的字典；快照不存在时返回 `None`

---

## 返回值字段说明

### 基本赛事信息

| 字段 | 类型 | 说明 |
|------|------|------|
| `match_id` | `int` | 赛事 ID（schedule_id） |
| `match_time` | `str` | 开球时间，如 `"2026-03-07 20:45"` |
| `league` | `str` | 联赛中文名 |
| `home_team` | `str` | 主队中文名 |
| `away_team` | `str` | 客队中文名 |
| `home_rank` | `int \| None` | 主队联赛排名 |
| `away_rank` | `int \| None` | 客队联赛排名 |
| `home_score` | `int \| None` | 主队进球数（未开赛为 None） |
| `away_score` | `int \| None` | 客队进球数 |
| `home_half_score` | `int \| None` | 主队半场进球数 |
| `away_half_score` | `int \| None` | 客队半场进球数 |

### 联赛积分与近期胜平负

| 字段 | 类型 | 说明 |
|------|------|------|
| `home_pts` | `int \| None` | 主队联赛积分 |
| `away_pts` | `int \| None` | 客队联赛积分 |
| `home_wdl` | `tuple(int, int, int) \| None` | 主队近期 (胜, 平, 负) 场数 |
| `away_wdl` | `tuple(int, int, int) \| None` | 客队近期 (胜, 平, 负) 场数 |

### 近期比赛（各队最多 8 场）

| 字段 | 类型 | 说明 |
|------|------|------|
| `home_recent` | `list[dict]` | 主队近期比赛列表 |
| `away_recent` | `list[dict]` | 客队近期比赛列表 |

每条记录的字段：

| key | 类型 | 说明 |
|-----|------|------|
| `home_name` | `str` | 主场队名（含 `[排名]` 前缀） |
| `away_name` | `str` | 客场队名（含 `[排名]` 前缀） |
| `score` | `str` | 比分，如 `"2:1"` |
| `h30_odds` | `str` | 赛前半小时赔率，如 `"1.50/3.80/6.00"` |
| `cur_odds` | `str` | 最终赔率，如 `"1.45/4.00/6.50"` |

### 历史交手（最多 8 场）

| 字段 | 类型 | 说明 |
|------|------|------|
| `h2h` | `list[dict]` | 交手记录列表 |
| `h2h_summary` | `dict` | 站主队视角统计 `{win, draw, loss}` |

每条交手记录的字段：

| key | 类型 | 说明 |
|-----|------|------|
| `side` | `str` | `"主"` 或 `"客"`（主队在该场的身份） |
| `home_name` | `str` | 主场队名 |
| `away_name` | `str` | 客场队名 |
| `score` | `str` | 比分 |
| `cur_odds` | `str` | 最终赔率 |

### 欧赔（三家博彩公司）

```python
'odds': {
    'wh':    {...},   # 威廉希尔（可能为 None）
    'coral': {...},   # 立博（可能为 None）
    '365':   {...},   # Bet365 欧赔（可能为 None）
}
```

每家公司的结构：

```python
{
    'open': {
        'win':    '1.50',     # 初盘胜赔（字符串）
        'draw':   '3.80',
        'lose':   '6.00',
        'payout': '93.5%',    # 返还率
        'time':   '2026-03-01 12:00:00',
    },
    'history': [              # 变盘历史（最多 5 条，按时间正序）
        {
            'win': '1.48', 'draw': '3.90', 'lose': '6.20',
            'payout': '93.2%',
            'time': '2026-03-07 18:30',
            'win_dir': 'down',     # 'up' | 'down' | 'unchanged' | ''
            'draw_dir': 'up',
            'lose_dir': 'up',
        },
        ...
    ],
}
```

### 亚盘（Bet365）

```python
'asian_odds': {
    'open': {
        'hc':   '-0.5',      # 盘口
        'home': '0.95',       # 主队水位
        'away': '0.90',       # 客队水位
        'time': '...',
    },
    'history': [              # 变盘历史（最多 3 条，按时间正序）
        {
            'hc': '-0.75', 'home': '0.88', 'away': '0.97',
            'time': '...',
            'home_dir': 'down', 'away_dir': 'up',
        },
        ...
    ],
}
# 若无数据则为 None
```

### 大小球（Bet365）

```python
'over_under': {
    'open': {
        'goals': '2.5',      # 进球线
        'over':  '0.95',     # 大球赔率
        'under': '0.90',     # 小球赔率
        'time':  '...',
    },
    'history': [              # 变盘历史（最多 3 条，按时间正序）
        {
            'goals': '2.5', 'over': '0.88', 'under': '0.97',
            'time': '...',
            'over_dir': 'down', 'under_dir': 'up',
        },
        ...
    ],
}
# 若无数据则为 None
```

### 联赛积分榜

```python
'league_table': {
    'total': [...],   # 总榜
    'home':  [...],   # 主场榜
    'away':  [...],   # 客场榜
}
```

每行的字段：

| key | 类型 | 说明 |
|-----|------|------|
| `rank` | `int` | 排名 |
| `team_name` | `str` | 球队名 |
| `points` | `int \| None` | 积分 |
| `zone_flag` | `int` | 区域标记（0=蓝区, 1=绿区, 2=灰区, -1=无） |
| `is_focus` | `int` | 1=本场参赛队, 0=其他 |

---

## 使用示例

```python
from src.algorithm import load_match

data = load_match(2907948)
if data is None:
    print("赛事不存在或未抓取")
else:
    print(f"{data['home_team']} vs {data['away_team']}")
    print(f"联赛：{data['league']}")
    print(f"主队积分：{data['home_pts']}")
    print(f"主队近期战绩：{data['home_wdl']}")

    # 威廉希尔开盘赔率
    wh = data['odds']['wh']
    if wh:
        print(f"威廉开盘：{wh['open']['win']}/{wh['open']['draw']}/{wh['open']['lose']}")

    # 亚盘
    asian = data['asian_odds']
    if asian:
        print(f"亚盘开盘：{asian['open']['home']} / {asian['open']['hc']} / {asian['open']['away']}")

    # 大小球
    ou = data['over_under']
    if ou:
        print(f"大小球开盘：{ou['open']['over']} / {ou['open']['goals']} / {ou['open']['under']}")
```

注意：赔率数值为格式化字符串（如 `"1.50"`），需转为浮点数时用 `float(v)`。
