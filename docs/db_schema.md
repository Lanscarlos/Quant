# 数据库表结构文档

数据库：`data/quant.db`（SQLite，WAL 模式，外键启用）

---

## 目录

1. [leagues — 联赛字典](#1-leagues--联赛字典)
2. [teams — 球队字典](#2-teams--球队字典)
3. [matches — 赛事列表](#3-matches--赛事列表)
4. [match_standings — 联赛排名详情](#4-match_standings--联赛排名详情)
5. [match_recent — 近6场历史](#5-match_recent--近6场历史)
6. [companies — 博彩公司字典](#6-companies--博彩公司字典)
7. [match_odds — 欧赔快照](#7-match_odds--欧赔快照)
8. [odds_history — 欧赔变动历史](#8-odds_history--欧赔变动历史)
9. [match_asian_odds — 亚盘快照](#9-match_asian_odds--亚盘快照)
10. [asian_odds_history — 亚盘变动历史](#10-asian_odds_history--亚盘变动历史)
11. [设计备注](#设计备注)

---

## 1. leagues — 联赛字典

写入策略：`INSERT OR IGNORE`（写一次，不覆盖）

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `league_abbr` | TEXT | PRIMARY KEY | 英文缩写，唯一标识 |
| `league_name_cn` | TEXT | | 联赛中文名（简体） |
| `league_color` | TEXT | | 显示色 |
| `country_id` | INTEGER | | 国家 ID |

---

## 2. teams — 球队字典

写入策略：`INSERT OR IGNORE`

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `team_id` | INTEGER | PRIMARY KEY | titan007 球队 ID |
| `team_name_cn` | TEXT | | 中文名（简体） |
| `team_name_en` | TEXT | | 英文名 |

---

## 3. matches — 赛事列表

写入策略：`INSERT OR REPLACE`（每次拉取均更新状态/比分）

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `schedule_id` | INTEGER | PRIMARY KEY | titan007 赛事 ID |
| `match_time` | TEXT | NOT NULL | 开赛时间（北京时间） |
| `status` | INTEGER | NOT NULL DEFAULT 0 | 0=未开始 1=进行中 3=半场 -1=完场 -11/-12/-14=异常 |
| `league_abbr` | TEXT | → leagues | 所属联赛 |
| `home_team_id` | INTEGER | NOT NULL → teams | 主队 ID |
| `home_rank` | INTEGER | | 主队排名 |
| `away_team_id` | INTEGER | NOT NULL → teams | 客队 ID |
| `away_rank` | INTEGER | | 客队排名 |
| `home_score` | INTEGER | | 主队全场进球 |
| `away_score` | INTEGER | | 客队全场进球 |
| `home_half_score` | INTEGER | | 主队半场进球 |
| `away_half_score` | INTEGER | | 客队半场进球 |
| `home_red_cards` | INTEGER | DEFAULT 0 | 主队红牌数 |
| `away_red_cards` | INTEGER | DEFAULT 0 | 客队红牌数 |
| `home_yellow_cards` | INTEGER | DEFAULT 0 | 主队黄牌数 |
| `away_yellow_cards` | INTEGER | DEFAULT 0 | 客队黄牌数 |
| `fetched_at` | TEXT | NOT NULL DEFAULT now+8h | 最近抓取时间 |

**索引：** `match_time` / `status` / `league_abbr` / `home_team_id` / `away_team_id`

---

## 4. match_standings — 联赛排名详情

数据来源：`https://zq.titan007.com/analysis/{mid}sb.htm`
写入策略：`INSERT OR REPLACE`，每场 16 行（2 side × 2 period × 4 scope）

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK AUTOINCREMENT | |
| `schedule_id` | INTEGER | NOT NULL → matches ON DELETE CASCADE | |
| `side` | TEXT | CHECK IN ('home','away') | 主/客队 |
| `period` | TEXT | CHECK IN ('ft','ht') | 全场/半场 |
| `scope` | TEXT | CHECK IN ('total','home','away','last6') | 统计范围 |
| `played` | INTEGER | | 出场场次 |
| `win` | INTEGER | | 胜 |
| `draw` | INTEGER | | 平 |
| `loss` | INTEGER | | 负 |
| `goals_for` | INTEGER | | 进球 |
| `goals_against` | INTEGER | | 失球 |
| `goal_diff` | INTEGER | | 净胜球 |
| `points` | INTEGER | | 积分 |
| `rank` | INTEGER | | 排名 |
| `win_rate` | REAL | | 胜率 |
| `fetched_at` | TEXT | NOT NULL DEFAULT now+8h | |

**唯一约束：** `(schedule_id, side, period, scope)`
**索引：** `schedule_id`

---

## 5. match_recent — 近6场历史

数据来源：同 match_standings（`{mid}sb.htm` 页面的 `h_data`/`a_data` JS 数组）
写入策略：`INSERT OR REPLACE`，每支球队最多 6 行

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK AUTOINCREMENT | |
| `schedule_id` | INTEGER | NOT NULL → matches ON DELETE CASCADE | 关联的当前赛事 |
| `side` | TEXT | CHECK IN ('home','away') | 主/客队视角 |
| `match_id` | INTEGER | NOT NULL | 历史赛事 ID |
| `date` | TEXT | | 比赛日期 |
| `match_time` | TEXT | | 比赛时间 |
| `league` | TEXT | | 联赛名 |
| `home_id` | INTEGER | | 历史主队 ID |
| `home_name` | TEXT | | 历史主队名 |
| `away_id` | INTEGER | | 历史客队 ID |
| `away_name` | TEXT | | 历史客队名 |
| `home_ft` | INTEGER | | 主队全场进球 |
| `away_ft` | INTEGER | | 客队全场进球 |
| `ht_score` | TEXT | | 半场比分（字符串，如 "1:0"） |
| `handicap` | TEXT | | 让球盘口 |
| `result` | INTEGER | | 全场胜平负结果 |
| `hc_result` | INTEGER | | 让球结果 |
| `fetched_at` | TEXT | NOT NULL DEFAULT now+8h | |

**唯一约束：** `(schedule_id, side, match_id)`
**索引：** `schedule_id`

---

## 6. companies — 博彩公司字典

写入策略：`INSERT OR IGNORE`

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `company_id` | INTEGER | PRIMARY KEY | titan007 公司 ID |
| `company_name` | TEXT | NOT NULL | 公司名称 |
| `label` | TEXT | | 自定义标签（如 "wh"、"coral"） |

**当前关注的公司 ID：**
- `115` — William Hill（威廉希尔，欧赔）
- `立博 ID` — Coral（立博，欧赔）
- `365 ID` — Bet365（亚盘）

---

## 7. match_odds — 欧赔快照

数据来源：`https://1x2d.titan007.com/{mid}.js`
写入策略：`INSERT OR REPLACE`，每次覆盖最新快照

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `record_id` | INTEGER | PRIMARY KEY | titan007 内部 record ID（供 odds_history FK 使用） |
| `schedule_id` | INTEGER | NOT NULL | 赛事 ID |
| `company_id` | INTEGER | NOT NULL → companies | 博彩公司 |
| `open_win` | REAL | | 初始胜赔 |
| `open_draw` | REAL | | 初始平赔 |
| `open_lose` | REAL | | 初始负赔 |
| `open_win_prob` | REAL | | 初始胜概率 |
| `open_draw_prob` | REAL | | 初始平概率 |
| `open_lose_prob` | REAL | | 初始负概率 |
| `open_payout_rate` | REAL | | 初始返还率 |
| `cur_win` | REAL | | 即时胜赔 |
| `cur_draw` | REAL | | 即时平赔 |
| `cur_lose` | REAL | | 即时负赔 |
| `cur_win_prob` | REAL | | 即时胜概率 |
| `cur_draw_prob` | REAL | | 即时平概率 |
| `cur_lose_prob` | REAL | | 即时负概率 |
| `cur_payout_rate` | REAL | | 即时返还率 |
| `kelly_win` | REAL | | 凯利指数（胜） |
| `kelly_draw` | REAL | | 凯利指数（平） |
| `kelly_lose` | REAL | | 凯利指数（负） |
| `hist_kelly_win` | REAL | | 历史凯利（胜） |
| `hist_kelly_draw` | REAL | | 历史凯利（平） |
| `hist_kelly_lose` | REAL | | 历史凯利（负） |
| `change_time` | TEXT | | 最近变动时间（ISO 格式） |
| `flag1` | INTEGER | | titan007 标志位 1 |
| `flag2` | INTEGER | | titan007 标志位 2 |
| `fetched_at` | TEXT | NOT NULL DEFAULT now+8h | |

**唯一约束：** `(schedule_id, company_id)`
**索引：** `schedule_id`

---

## 8. odds_history — 欧赔变动历史

数据来源：`https://1x2.titan007.com/OddsHistory.aspx?...`
写入策略：`INSERT OR IGNORE`（历史记录不可变）

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK AUTOINCREMENT | |
| `record_id` | INTEGER | NOT NULL → match_odds | 对应快照行 |
| `schedule_id` | INTEGER | NOT NULL | 冗余存储，加速按赛事查询 |
| `company_id` | INTEGER | NOT NULL | 冗余存储，加速按公司筛选 |
| `win` | REAL | | 胜赔 |
| `draw` | REAL | | 平赔 |
| `lose` | REAL | | 负赔 |
| `win_prob` | REAL | | 胜概率 |
| `draw_prob` | REAL | | 平概率 |
| `lose_prob` | REAL | | 负概率 |
| `payout_rate` | REAL | | 返还率 |
| `kelly_win` | REAL | | 凯利（胜） |
| `kelly_draw` | REAL | | 凯利（平） |
| `kelly_lose` | REAL | | 凯利（负） |
| `change_time` | TEXT | NOT NULL | 变动时间（`YYYY-MM-DD HH:MM`） |
| `is_opening` | INTEGER | NOT NULL DEFAULT 0 | 1=初始赔率行 |
| `win_dir` | TEXT | CHECK IN ('up','down','unchanged') | 胜赔变动方向 |
| `draw_dir` | TEXT | CHECK IN ('up','down','unchanged') | 平赔变动方向 |
| `lose_dir` | TEXT | CHECK IN ('up','down','unchanged') | 负赔变动方向 |

**唯一约束：** `(record_id, change_time)`
**索引：** `record_id` / `schedule_id` / `(schedule_id, company_id, is_opening, change_time DESC)`

---

## 9. match_asian_odds — 亚盘快照

数据来源：`https://vip.titan007.com/AsianOdds_n.aspx?id={mid}`（GB2312）
写入策略：`INSERT OR REPLACE`

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK AUTOINCREMENT | |
| `schedule_id` | INTEGER | NOT NULL → matches ON DELETE CASCADE | |
| `company_id` | INTEGER | NOT NULL → companies | |
| `open_handicap` | TEXT | | 初始让球盘口（如 "-0.75"） |
| `open_home` | REAL | | 初始主队赔率 |
| `open_away` | REAL | | 初始客队赔率 |
| `cur_handicap` | TEXT | | 即时让球盘口 |
| `cur_home` | REAL | | 即时主队赔率 |
| `cur_away` | REAL | | 即时客队赔率 |
| `fetched_at` | TEXT | NOT NULL DEFAULT now+8h | |

**唯一约束：** `(schedule_id, company_id)`
**索引：** `schedule_id`

---

## 10. asian_odds_history — 亚盘变动历史

数据来源：`https://vip.titan007.com/changeDetail/handicap.aspx?...`（GB2312）
写入策略：`INSERT OR IGNORE`（历史记录不可变）

| 列名 | 类型 | 约束 | 说明 |
|---|---|---|---|
| `id` | INTEGER | PK AUTOINCREMENT | |
| `schedule_id` | INTEGER | NOT NULL | |
| `company_id` | INTEGER | NOT NULL | |
| `change_time` | TEXT | NOT NULL | 变动时间（`YYYY-MM-DD HH:MM`） |
| `score` | TEXT | | 变动时比分（如 "0:0"） |
| `home_odds` | REAL | | 主队赔率 |
| `handicap` | TEXT | | 让球盘口 |
| `away_odds` | REAL | | 客队赔率 |
| `is_opening` | INTEGER | NOT NULL DEFAULT 0 | 1=初始行 |
| `home_dir` | TEXT | CHECK IN ('up','down','unchanged') | 主队赔率变动方向 |
| `away_dir` | TEXT | CHECK IN ('up','down','unchanged') | 客队赔率变动方向 |

**唯一约束：** `(schedule_id, company_id, change_time)`
**索引：** `schedule_id` / `(schedule_id, company_id)`

---

## 设计备注

### 刷新策略（`src/sync/coordinator.py`）

| 数据 | 已完场 | 进行中（status 1/3） | 未开始（status 0） |
|---|---|---|---|
| match_list | — | — | 超 10 分钟重新拉取 |
| match_detail（standings + recent） | 拉一次即止 | 跳过 | 超 6 小时重新拉取 |
| match_odds | 拉一次即止 | 超 2 分钟重新拉取 | 超 10 分钟重新拉取 |
| odds_history | 拉一次即止 | 每次都拉取 | 每次都拉取 |

### 待优化：专表方案

当前 `match_odds` / `odds_history` / `match_asian_odds` / `asian_odds_history` 存储所有博彩公司数据。
若仅需威廉希尔（欧赔）、立博（欧赔）、365（亚盘）三家，可改为每家一套专表：

- `schedule_id` 直接作为快照表主键（无需 `(schedule_id, company_id)` 联合约束）
- 历史表唯一键简化为 `(schedule_id, change_time)`
- `record_id`（titan007 内部 artifact）可从对外接口中去除
- 查询无需 `WHERE company_id = ?` 过滤，`companies` 字典表不再作为 FK 依赖

此方案对公司集固定的场景更优，扩展新公司时需要新表 + migration。