# 算法可用字段参考手册

本文档列出 `load_match(mid)` 返回字典中所有可用字段，按分类说明含义、数据类型和示例值。

```python
from src.algorithm import load_match

data = load_match(12345)   # 传入赛事 ID
```

---

## 一、基本赛事信息

| 字段路径 | 中文含义 | 类型 | 示例值 |
|---------|---------|------|-------|
| `data['match_id']` | 赛事唯一 ID | `int` | `12345` |
| `data['match_time']` | 赛事时间（北京时间） | `str` | `"2025-01-15 20:45"` |
| `data['league']` | 联赛名称 | `str` | `"英超"` |
| `data['home_team']` | 主队名称 | `str` | `"曼城"` |
| `data['away_team']` | 客队名称 | `str` | `"阿森纳"` |
| `data['home_rank']` | 主队联赛排名（未获取时为 `None`） | `int \| None` | `3` |
| `data['away_rank']` | 客队联赛排名 | `int \| None` | `1` |
| `data['home_score']` | 主队全场进球数（未开赛为 `None`） | `int \| None` | `2` |
| `data['away_score']` | 客队全场进球数 | `int \| None` | `1` |
| `data['home_half_score']` | 主队半场进球数 | `int \| None` | `1` |
| `data['away_half_score']` | 客队半场进球数 | `int \| None` | `0` |

---

## 二、联赛积分与胜平负

| 字段路径 | 中文含义 | 类型 | 示例值 |
|---------|---------|------|-------|
| `data['home_pts']` | 主队当前联赛积分 | `int \| None` | `42` |
| `data['away_pts']` | 客队当前联赛积分 | `int \| None` | `50` |
| `data['home_wdl']` | 主队近期战绩 (胜, 平, 负)，基于 recent 数据统计 | `tuple \| None` | `(4, 2, 2)` |
| `data['away_wdl']` | 客队近期战绩 (胜, 平, 负) | `tuple \| None` | `(6, 1, 1)` |

```python
# 取用示例
if data['home_wdl']:
    win, draw, loss = data['home_wdl']
    print(f"主队近期 {win}胜 {draw}平 {loss}负")
```

---

## 三、近期比赛（各队最多 8 场）

```python
data['home_recent']   # 主队近 8 场，列表
data['away_recent']   # 客队近 8 场，列表
```

每条记录是一个字典，包含：

| 键名 | 中文含义 | 类型 | 示例值 |
|-----|---------|------|-------|
| `home_name` | 本场主队名（含排名前缀） | `str` | `"[3] 曼城"` |
| `away_name` | 本场客队名（含排名前缀） | `str` | `"[8] 利物浦"` |
| `score` | 全场比分 | `str` | `"2:1"` |
| `h30_odds` | 赛前 30 分钟威廉希尔赔率（胜/平/负） | `str` | `"1.80/3.40/4.50"` |
| `cur_odds` | 最终威廉希尔赔率（胜/平/负） | `str` | `"1.75/3.50/4.80"` |

```python
# 取用示例
for match in data['home_recent']:
    print(match['home_name'], match['score'], match['away_name'])
    # 将字符串赔率转为浮点数
    win_odds = float(match['cur_odds'].split('/')[0])
```

---

## 四、历史交手记录（最多 8 场）

```python
data['h2h']           # 交手记录列表
data['h2h_summary']   # 汇总统计
```

### `data['h2h']` — 每条记录

| 键名 | 中文含义 | 类型 | 示例值 |
|-----|---------|------|-------|
| `side` | 主队以什么身份出场 | `str` | `"主"` 或 `"客"` |
| `home_name` | 本场主队名（含排名） | `str` | `"[3] 曼城"` |
| `away_name` | 本场客队名（含排名） | `str` | `"[1] 阿森纳"` |
| `score` | 全场比分 | `str` | `"1:1"` |
| `cur_odds` | 最终威廉希尔赔率 | `str` | `"2.10/3.30/3.50"` |

### `data['h2h_summary']` — 站主队视角统计

| 键名 | 中文含义 | 类型 | 示例值 |
|-----|---------|------|-------|
| `win` | 主队赢场数 | `int` | `3` |
| `draw` | 平局数 | `int` | `2` |
| `loss` | 主队输场数 | `int` | `3` |

---

## 五、欧赔数据（三家博彩公司）

```python
data['odds']['wh']      # 威廉希尔（William Hill）
data['odds']['coral']   # 立博（Ladbrokes）
data['odds']['365']     # Bet365 欧赔
```

若某家公司数据未抓取，对应值为 `None`，使用前请先判断。

每家公司的数据结构相同：

```python
company = data['odds']['wh']
company['open']      # 开盘数据
company['history']   # 变盘历史列表（赛前最多 5 条，按时间从早到晚排列）
```

### `open` — 开盘数据

| 键名 | 中文含义 | 类型 | 示例值 |
|-----|---------|------|-------|
| `win` | 主队胜赔率 | `str` | `"2.00"` |
| `draw` | 平局赔率 | `str` | `"3.40"` |
| `lose` | 客队胜赔率 | `str` | `"3.80"` |
| `payout` | 返还率（越高越公平） | `str` | `"97.5%"` |
| `time` | 开盘时间 | `str` | `"2025-01-10 08:30"` |

### `history` — 变盘历史，每条记录

| 键名 | 中文含义 | 类型 | 示例值 |
|-----|---------|------|-------|
| `win` | 主队胜赔率 | `str` | `"1.95"` |
| `draw` | 平局赔率 | `str` | `"3.50"` |
| `lose` | 客队胜赔率 | `str` | `"3.90"` |
| `payout` | 返还率 | `str` | `"97.8%"` |
| `time` | 变盘时间 | `str` | `"2025-01-14 18:00"` |
| `win_dir` | 主队赔率变化方向 | `str` | `"down"` / `"up"` / `"unchanged"` |
| `draw_dir` | 平局赔率变化方向 | `str` | `"up"` |
| `lose_dir` | 客队赔率变化方向 | `str` | `"up"` |

```python
# 取用示例
wh = data['odds']['wh']
if wh:
    open_win = float(wh['open']['win'])      # 开盘主胜赔率（浮点数）
    
    # 最新变盘赔率（history 最后一条）
    if wh['history']:
        last = wh['history'][-1]
        cur_win = float(last['win'])
        trend = last['win_dir']              # "down" 表示主队赔率下降（更被看好）
```

---

## 六、亚盘数据（Bet365）

```python
data['asian_odds']   # 若无数据则为 None
```

```python
asian = data['asian_odds']
if asian:
    asian['open']      # 开盘数据
    asian['history']   # 变盘历史（最多 3 条，按时间从早到晚排列）
```

### `open` — 开盘数据

| 键名 | 中文含义 | 类型 | 示例值 | 说明 |
|-----|---------|------|-------|-----|
| `hc` | 让球盘口 | `str` | `"-0.5"` / `"+1.0"` | 负数表示主队让球 |
| `home` | 主队赔率 | `str` | `"0.94"` | 通常在 0.80～1.10 之间 |
| `away` | 客队赔率 | `str` | `"0.96"` | 同上 |
| `time` | 开盘时间 | `str` | `"2025-01-10 08:30"` | |

### `history` — 变盘历史，每条记录

| 键名 | 中文含义 | 类型 | 示例值 |
|-----|---------|------|-------|
| `hc` | 变化后盘口 | `str` | `"-0.75"` |
| `home` | 变化后主队赔率 | `str` | `"0.91"` |
| `away` | 变化后客队赔率 | `str` | `"0.99"` |
| `time` | 变盘时间 | `str` | `"2025-01-14 20:00"` |
| `home_dir` | 主队赔率变化方向 | `str` | `"down"` / `"up"` / `"unchanged"` |
| `away_dir` | 客队赔率变化方向 | `str` | `"up"` |

```python
# 取用示例
asian = data['asian_odds']
if asian:
    open_hc = asian['open']['hc']               # 开盘盘口，如 "-0.5"
    open_home = float(asian['open']['home'])     # 开盘主队赔率

    # 最新盘口（history 最后一条，若有）
    if asian['history']:
        latest = asian['history'][-1]
        cur_hc = latest['hc']
```

---

## 七、大小球数据（Bet365）

```python
data['over_under']   # 若无数据则为 None
```

```python
ou = data['over_under']
if ou:
    ou['open']      # 开盘数据
    ou['history']   # 变盘历史（最多 3 条，按时间从早到晚排列）
```

### `open` — 开盘数据

| 键名 | 中文含义 | 类型 | 示例值 | 说明 |
|-----|---------|------|-------|-----|
| `goals` | 进球数盘口 | `str` | `"2.5"` | 通常为 2.5 / 3.0 / 3.5 |
| `over` | 大球赔率（进球数超过盘口） | `str` | `"1.85"` | |
| `under` | 小球赔率（进球数不超过盘口） | `str` | `"1.95"` | |
| `time` | 开盘时间 | `str` | `"2025-01-10 08:30"` | |

### `history` — 变盘历史，每条记录

| 键名 | 中文含义 | 类型 | 示例值 |
|-----|---------|------|-------|
| `goals` | 变化后盘口 | `str` | `"3.0"` |
| `over` | 变化后大球赔率 | `str` | `"2.00"` |
| `under` | 变化后小球赔率 | `str` | `"1.80"` |
| `time` | 变盘时间 | `str` | `"2025-01-14 20:00"` |
| `over_dir` | 大球赔率变化方向 | `str` | `"up"` / `"down"` / `"unchanged"` |
| `under_dir` | 小球赔率变化方向 | `str` | `"down"` |

---

## 八、联赛积分榜

```python
data['league_table']['total']   # 总积分榜
data['league_table']['home']    # 主场积分榜
data['league_table']['away']    # 客场积分榜
```

每个列表按排名升序排列，每条记录：

| 键名 | 中文含义 | 类型 | 示例值 | 说明 |
|-----|---------|------|-------|-----|
| `rank` | 排名 | `int` | `1` | |
| `team_name` | 球队名称 | `str` | `"阿森纳"` | |
| `points` | 积分 | `int` | `50` | |
| `zone_flag` | 区域标志 | `int` | `-1` / `0` / `1` / `2` | `0`=欧冠区 `1`=欧联区 `2`=保级区 `-1`=无标记 |
| `is_focus` | 是否为本场参赛队 | `int` | `1` / `0` | `1`=是（共2条），`0`=其他队 |

```python
# 取用示例：找出本场两队在总榜的位置
total = data['league_table']['total']
for row in total:
    if row['is_focus']:
        print(f"第{row['rank']}名 {row['team_name']} 积分{row['points']}")
```

---

## 附录：赔率变化方向说明

| 值 | 含义 |
|----|-----|
| `"up"` | 赔率上升（对该结果更不看好） |
| `"down"` | 赔率下降（对该结果更看好，资金流入） |
| `"unchanged"` | 赔率未变 |
| `""` | 无数据 |

## 附录：常用数据转换

```python
# 字符串赔率 → 浮点数
win_odds = float(data['odds']['wh']['open']['win'])   # "1.80" → 1.8

# 返还率字符串 → 浮点数
payout = float(data['odds']['wh']['open']['payout'].rstrip('%')) / 100  # "97.5%" → 0.975

# 从 h30_odds / cur_odds 字符串拆分各项赔率
odds_str = "1.80/3.40/4.50"
win, draw, lose = [float(x) for x in odds_str.split('/')]

# 安全取值（避免 None 报错）
home_score = data['home_score'] or 0
```
