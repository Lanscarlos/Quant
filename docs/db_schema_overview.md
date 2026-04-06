# 数据库表结构说明

数据库：`data/quant.db`（SQLite 本地数据库）

赔率数据仅保留三家公司：**威廉希尔**（欧赔）、**立博**（欧赔）、**365**（亚盘），每家公司独立一套表。

---

## 目录

1. [leagues — 联赛](#1-leagues--联赛)
2. [teams — 球队](#2-teams--球队)
3. [matches — 赛事](#3-matches--赛事)
4. [match_standings — 联赛排名详情](#4-match_standings--联赛排名详情)
5. [match_recent — 近6场历史](#5-match_recent--近6场历史)
6. [odds_wh — 威廉希尔欧赔快照](#6-odds_wh--威廉希尔欧赔快照)
7. [odds_wh_history — 威廉希尔欧赔历史](#7-odds_wh_history--威廉希尔欧赔历史)
8. [odds_coral — 立博欧赔快照](#8-odds_coral--立博欧赔快照)
9. [odds_coral_history — 立博欧赔历史](#9-odds_coral_history--立博欧赔历史)
10. [asian_odds_365 — 365亚盘快照](#10-asian_odds_365--365亚盘快照)
11. [asian_odds_365_history — 365亚盘历史](#11-asian_odds_365_history--365亚盘历史)

---

## 1. leagues — 联赛

| 字段 | 类型 | 说明 |
|---|---|---|
| `league_abbr` | 文本 | 联赛英文缩写，唯一标识 |
| `league_name_cn` | 文本 | 联赛中文名（简体） |
| `league_color` | 文本 | 显示色 |
| `country_id` | 整数 | 所属国家 ID |

---

## 2. teams — 球队

| 字段 | 类型 | 说明 |
|---|---|---|
| `team_id` | 整数 | 球队 ID |
| `team_name_cn` | 文本 | 中文名（简体） |
| `team_name_en` | 文本 | 英文名 |

---

## 3. matches — 赛事

| 字段 | 类型 | 说明 |
|---|---|---|
| `schedule_id` | 整数 | 赛事 ID |
| `match_time` | 文本 | 开赛时间（北京时间） |
| `status` | 整数 | 状态：0=未开始 1=进行中 3=半场 -1=完场 -11/-12/-14=异常取消 |
| `league_abbr` | 文本 | 所属联赛 |
| `home_team_id` | 整数 | 主队 ID |
| `home_rank` | 整数 | 主队排名 |
| `away_team_id` | 整数 | 客队 ID |
| `away_rank` | 整数 | 客队排名 |
| `home_score` | 整数 | 主队全场进球 |
| `away_score` | 整数 | 客队全场进球 |
| `home_half_score` | 整数 | 主队半场进球 |
| `away_half_score` | 整数 | 客队半场进球 |
| `home_red_cards` | 整数 | 主队红牌数 |
| `away_red_cards` | 整数 | 客队红牌数 |
| `home_yellow_cards` | 整数 | 主队黄牌数 |
| `away_yellow_cards` | 整数 | 客队黄牌数 |
| `fetched_at` | 文本 | 最近抓取时间 |

---

## 4. match_standings — 联赛排名详情

每场比赛最多 16 条记录（主队/客队 × 全场/半场 × 总榜/主场榜/客场榜/近6场榜）。

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | 整数 | 自增主键 |
| `schedule_id` | 整数 | 所属赛事 ID |
| `side` | 文本 | `home`=主队，`away`=客队 |
| `period` | 文本 | `ft`=全场，`ht`=半场 |
| `scope` | 文本 | `total`=总榜，`home`=主场，`away`=客场，`last6`=近6场 |
| `played` | 整数 | 出场场次 |
| `win` | 整数 | 胜场数 |
| `draw` | 整数 | 平场数 |
| `loss` | 整数 | 负场数 |
| `goals_for` | 整数 | 进球数 |
| `goals_against` | 整数 | 失球数 |
| `goal_diff` | 整数 | 净胜球 |
| `points` | 整数 | 积分 |
| `rank` | 整数 | 排名 |
| `win_rate` | 小数 | 胜率 |
| `fetched_at` | 文本 | 最近抓取时间 |

---

## 5. match_recent — 近6场历史

每场比赛的主队和客队各保存最近 6 场交战记录。

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | 整数 | 自增主键 |
| `schedule_id` | 整数 | 所属赛事 ID |
| `side` | 文本 | `home`=主队视角，`away`=客队视角 |
| `match_id` | 整数 | 历史赛事 ID |
| `date` | 文本 | 比赛日期 |
| `match_time` | 文本 | 比赛时间 |
| `league` | 文本 | 联赛名 |
| `home_id` | 整数 | 主队 ID |
| `home_name` | 文本 | 主队名 |
| `away_id` | 整数 | 客队 ID |
| `away_name` | 文本 | 客队名 |
| `home_ft` | 整数 | 主队全场进球 |
| `away_ft` | 整数 | 客队全场进球 |
| `ht_score` | 文本 | 半场比分（如 `1:0`） |
| `handicap` | 文本 | 让球盘口 |
| `result` | 整数 | 全场胜平负结果 |
| `hc_result` | 整数 | 让球结果 |
| `fetched_at` | 文本 | 最近抓取时间 |

---

## 6. odds_wh — 威廉希尔欧赔快照

每场比赛一条记录，保存威廉希尔当前最新赔率状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `schedule_id` | 整数 | 赛事 ID（主键） |
| `open_win` | 小数 | 开盘胜赔 |
| `open_draw` | 小数 | 开盘平赔 |
| `open_lose` | 小数 | 开盘负赔 |
| `open_win_prob` | 小数 | 开盘胜概率 |
| `open_draw_prob` | 小数 | 开盘平概率 |
| `open_lose_prob` | 小数 | 开盘负概率 |
| `open_payout_rate` | 小数 | 开盘返还率 |
| `cur_win` | 小数 | 即时胜赔 |
| `cur_draw` | 小数 | 即时平赔 |
| `cur_lose` | 小数 | 即时负赔 |
| `cur_win_prob` | 小数 | 即时胜概率 |
| `cur_draw_prob` | 小数 | 即时平概率 |
| `cur_lose_prob` | 小数 | 即时负概率 |
| `cur_payout_rate` | 小数 | 即时返还率 |
| `kelly_win` | 小数 | 凯利指数（胜） |
| `kelly_draw` | 小数 | 凯利指数（平） |
| `kelly_lose` | 小数 | 凯利指数（负） |
| `hist_kelly_win` | 小数 | 历史凯利（胜） |
| `hist_kelly_draw` | 小数 | 历史凯利（平） |
| `hist_kelly_lose` | 小数 | 历史凯利（负） |
| `change_time` | 文本 | 最近变动时间 |
| `fetched_at` | 文本 | 最近抓取时间 |

---

## 7. odds_wh_history — 威廉希尔欧赔历史

记录威廉希尔每次赔率变动。第一条为开盘赔率，其余为后续变动。

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | 整数 | 自增主键 |
| `schedule_id` | 整数 | 所属赛事 ID |
| `win` | 小数 | 胜赔 |
| `draw` | 小数 | 平赔 |
| `lose` | 小数 | 负赔 |
| `win_prob` | 小数 | 胜概率 |
| `draw_prob` | 小数 | 平概率 |
| `lose_prob` | 小数 | 负概率 |
| `payout_rate` | 小数 | 返还率 |
| `kelly_win` | 小数 | 凯利指数（胜） |
| `kelly_draw` | 小数 | 凯利指数（平） |
| `kelly_lose` | 小数 | 凯利指数（负） |
| `change_time` | 文本 | 变动时间（`YYYY-MM-DD HH:MM`） |
| `is_opening` | 整数 | 1=开盘赔率，0=后续变动 |
| `win_dir` | 文本 | 胜赔变动方向：`up` / `down` / `unchanged` |
| `draw_dir` | 文本 | 平赔变动方向：`up` / `down` / `unchanged` |
| `lose_dir` | 文本 | 负赔变动方向：`up` / `down` / `unchanged` |

---

## 8. odds_coral — 立博欧赔快照

结构与 `odds_wh` 完全相同，每场比赛一条记录。

| 字段 | 类型 | 说明 |
|---|---|---|
| `schedule_id` | 整数 | 赛事 ID（主键） |
| `open_win` | 小数 | 开盘胜赔 |
| `open_draw` | 小数 | 开盘平赔 |
| `open_lose` | 小数 | 开盘负赔 |
| `open_win_prob` | 小数 | 开盘胜概率 |
| `open_draw_prob` | 小数 | 开盘平概率 |
| `open_lose_prob` | 小数 | 开盘负概率 |
| `open_payout_rate` | 小数 | 开盘返还率 |
| `cur_win` | 小数 | 即时胜赔 |
| `cur_draw` | 小数 | 即时平赔 |
| `cur_lose` | 小数 | 即时负赔 |
| `cur_win_prob` | 小数 | 即时胜概率 |
| `cur_draw_prob` | 小数 | 即时平概率 |
| `cur_lose_prob` | 小数 | 即时负概率 |
| `cur_payout_rate` | 小数 | 即时返还率 |
| `kelly_win` | 小数 | 凯利指数（胜） |
| `kelly_draw` | 小数 | 凯利指数（平） |
| `kelly_lose` | 小数 | 凯利指数（负） |
| `hist_kelly_win` | 小数 | 历史凯利（胜） |
| `hist_kelly_draw` | 小数 | 历史凯利（平） |
| `hist_kelly_lose` | 小数 | 历史凯利（负） |
| `change_time` | 文本 | 最近变动时间 |
| `fetched_at` | 文本 | 最近抓取时间 |

---

## 9. odds_coral_history — 立博欧赔历史

结构与 `odds_wh_history` 完全相同。

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | 整数 | 自增主键 |
| `schedule_id` | 整数 | 所属赛事 ID |
| `win` | 小数 | 胜赔 |
| `draw` | 小数 | 平赔 |
| `lose` | 小数 | 负赔 |
| `win_prob` | 小数 | 胜概率 |
| `draw_prob` | 小数 | 平概率 |
| `lose_prob` | 小数 | 负概率 |
| `payout_rate` | 小数 | 返还率 |
| `kelly_win` | 小数 | 凯利指数（胜） |
| `kelly_draw` | 小数 | 凯利指数（平） |
| `kelly_lose` | 小数 | 凯利指数（负） |
| `change_time` | 文本 | 变动时间（`YYYY-MM-DD HH:MM`） |
| `is_opening` | 整数 | 1=开盘赔率，0=后续变动 |
| `win_dir` | 文本 | 胜赔变动方向：`up` / `down` / `unchanged` |
| `draw_dir` | 文本 | 平赔变动方向：`up` / `down` / `unchanged` |
| `lose_dir` | 文本 | 负赔变动方向：`up` / `down` / `unchanged` |

---

## 10. asian_odds_365 — 365亚盘快照

每场比赛一条记录，保存 Bet365 让球盘口及赔率的当前状态。

| 字段 | 类型 | 说明 |
|---|---|---|
| `schedule_id` | 整数 | 赛事 ID（主键） |
| `open_handicap` | 文本 | 开盘让球盘口（如 `-0.75`） |
| `open_home` | 小数 | 开盘主队赔率 |
| `open_away` | 小数 | 开盘客队赔率 |
| `cur_handicap` | 文本 | 即时让球盘口 |
| `cur_home` | 小数 | 即时主队赔率 |
| `cur_away` | 小数 | 即时客队赔率 |
| `fetched_at` | 文本 | 最近抓取时间 |

---

## 11. asian_odds_365_history — 365亚盘历史

记录 Bet365 每次亚盘变动，完整还原盘口走势。

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | 整数 | 自增主键 |
| `schedule_id` | 整数 | 所属赛事 ID |
| `change_time` | 文本 | 变动时间（`YYYY-MM-DD HH:MM`） |
| `score` | 文本 | 变动时场上比分（如 `0:0`） |
| `home_odds` | 小数 | 主队赔率 |
| `handicap` | 文本 | 让球盘口 |
| `away_odds` | 小数 | 客队赔率 |
| `is_opening` | 整数 | 1=开盘记录，0=后续变动 |
| `home_dir` | 文本 | 主队赔率变动方向：`up` / `down` / `unchanged` |
| `away_dir` | 文本 | 客队赔率变动方向：`up` / `down` / `unchanged` |
