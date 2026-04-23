# Service 层 API 参考

Service 层位于 `src/service/`，每个模块封装一个数据源的"抓取 + 解析 + 持久化"流水线。

---

## match_detail.py — 赛事详情页

数据源：`https://zq.titan007.com/analysis/{mid}sb.htm`（UTF-8）

### `fetch_match_all(match_id, tracker=None) -> dict`

一次 HTTP 请求抓取并持久化：排名 + 近期 + 交手 + 联赛积分榜。

- **参数**：
  - `match_id`: 赛事 ID（str 或 int）
  - `tracker`: 可选 `ProgressTracker`，用于上报子步骤进度
- **返回值**：`{'match_time': str, 'match_year': int}`
- **写入表**：`matches`, `teams`, `match_standings`, `match_recent`, `match_h2h`, `league_table_snapshot`
- **子步骤**：下载 HTML → 解析基本信息 → 确保基础记录 → 保存排名 → 保存积分榜 → 保存近期比赛 → 解析交手 → 保存交手

### `fetch_match_basics(match_id) -> dict | None`

轻量抓取赛事基础信息（不写 standings/recent/h2h）。

- **返回值**：`{'schedule_id', 'match_time', 'league_name_cn', 'home_team', 'away_team'}` 或 `None`
- **写入表**：`matches`, `teams`

### `fetch_match_time(match_id) -> str | None`

仅抓取比赛开球时间，如 `"2026-03-07 20:45"`。

---

## euro_odds.py — 欧赔快照

数据源：`https://1x2d.titan007.com/{mid}.js`（UTF-8）

### `fetch_euro_odds(schedule_id) -> dict`

抓取并持久化威廉/立博/365 欧赔快照。

- **返回值**：`{'wh': bool, 'coral': bool, 'b365': bool}`
- **写入表**：`odds_wh`, `odds_coral`, `odds_365`

### `fetch_euro_odds_with_record_ids(schedule_id, tracker=None) -> dict[int, int]`

抓取并持久化欧赔快照，同时返回 `{company_id: record_id}`。

- **返回值**：`{115: record_id_wh, 82: record_id_coral, 281: record_id_365}`
- **用途**：返回值用于后续拉取变赔历史

---

## euro_odds_history.py — 欧赔变盘历史

数据源：`https://1x2.titan007.com/OddsHistory.aspx?id={rid}&sid={mid}&cid={cid}&l=0`（UTF-8）

### 常量

```python
COMPANY_WH    = 115   # 威廉希尔
COMPANY_CORAL = 82    # 立博
COMPANY_365   = 281   # Bet365
```

### `fetch_euro_odds_history(rid, mid, cid, match_year, tracker=None) -> int`

抓取并持久化某公司的欧赔变盘历史。

- **参数**：
  - `rid`: record_id，用于构建 URL
  - `mid`: 赛事 schedule_id
  - `cid`: 公司 ID（115/82/281）
  - `match_year`: 赛事年份，用于补全 "MM-DD HH:MM" 时间戳
  - `tracker`: 可选 ProgressTracker
- **返回值**：写入行数
- **写入表**：`odds_wh_history` / `odds_coral_history` / `odds_365_history`（根据 cid）
- **解析细节**：通过 font 颜色判断涨跌方向（green=up, red=down）

---

## asian_odds.py — 亚盘快照

数据源：`https://vip.titan007.com/AsianOdds_n.aspx?id={mid}`（GB2312）

### `fetch_asian_odds(schedule_id, tracker=None) -> bool`

抓取并持久化 Bet365 亚盘快照。

- **返回值**：`True` 写入成功，`False` 未找到 Bet365 数据
- **写入表**：`asian_odds_365`
- **常量**：`COMPANY_365 = 8`

---

## asian_odds_history.py — 亚盘变盘历史

数据源：`https://vip.titan007.com/changeDetail/handicap.aspx?id={mid}&companyID=8&l=0`（GB2312）

### `fetch_asian_odds_history(mid, match_year, tracker=None) -> int`

抓取并持久化 Bet365 亚盘变盘历史。

- **参数**：
  - `mid`: 赛事 schedule_id
  - `match_year`: 赛事年份
  - `tracker`: 可选 ProgressTracker
- **返回值**：写入行数
- **写入表**：`asian_odds_365_history`

---

## over_under.py — 大小球快照

数据源：`https://vip.titan007.com/OverDown_n.aspx?id={mid}&l=0`（GB2312）

### `fetch_over_under(schedule_id, tracker=None) -> bool`

抓取并持久化 Bet365 大小球快照。Bet365 可能有多行（主盘 + 副盘），取第一行（主盘）。

- **返回值**：`True` 写入成功，`False` 未找到 Bet365 数据
- **写入表**：`over_under_365`

---

## over_under_history.py — 大小球变盘历史

数据源：`https://vip.titan007.com/changeDetail/overunder.aspx?id={mid}&companyID=8&l=0`（GB2312）

### `fetch_over_under_history(mid, match_year, tracker=None) -> int`

抓取并持久化 Bet365 大小球变盘历史。

- **返回值**：写入行数
- **写入表**：`over_under_365_history`

---

## live_score.py — 实时比分

数据源：`https://live.titan007.com/jsData/{prefix}/{sid}.js`（GBK/UTF-8）

### `fetch_live_score(match_id, match_time=None) -> dict | None`

抓取并解析赛事实时比分与状态。

- **参数**：
  - `match_id`: 赛事 ID
  - `match_time`: 可选开球时间字符串，用于推断完赛状态
- **返回值**：`{'home_score': int, 'away_score': int, 'status': int}` 或 `None`
- **状态映射**：

| JS 阶段 | status |
|---------|--------|
| `未开场` / `早餐` | 0（未开赛） |
| 数字字符串（分钟） | 1（进行中），若超过开球 110 分钟则 -1 |
| `中场` | 3 |
| `终场` | -1（完赛） |

---

## browser_filter.py — 浏览器白名单

### `get_filtered_match_ids() -> list[str]`

返回用户在 titan007 中筛选出来要看的比赛 ID 列表（白名单）。

- **返回值**：比赛 ID 字符串列表，如 `['2958472', '2958473']`。读取失败或未设置筛选时返回空列表。
- **实现**：扫描 Chrome/Edge 的 LevelDB 本地存储，解析 Snappy 压缩的 SSTable 和 WAL 日志

---

## freshness.py — 新鲜度决策助手

所有函数只做一件事：回答"要不要发 HTTP 请求"。

### `match_ids_needing_refresh(filter_ids) -> list[int]`

返回 filter_ids 中需要重新抓取的 ID 子集。

### `should_fetch_detail(schedule_id, *, status=None) -> bool`

是否需要抓取赛事详情。

### `should_fetch_odds(schedule_id, *, status=None) -> bool`

是否需要抓取欧赔快照。

### `should_fetch_asian_odds(schedule_id, *, status=None) -> bool`

是否需要抓取亚盘快照。

### `should_fetch_over_under(schedule_id, *, status=None) -> bool`

是否需要抓取大小球快照。

### `should_fetch_history(schedule_id) -> bool`

是否需要抓取欧赔变盘历史。

### `should_fetch_asian_history(schedule_id) -> bool`

是否需要抓取亚盘变盘历史。

### `should_fetch_over_under_history(schedule_id) -> bool`

是否需要抓取大小球变盘历史。

详细阈值策略见 [data-pipeline.md](data-pipeline.md#新鲜度策略-srcservicefreshnesspy)。

---

## config.py — 配置管理

配置文件：`data/config.json`

### `get_refresh_interval() -> int`

返回赛事列表自动刷新间隔（秒）。默认 1200（20 分钟）。

### `set_refresh_interval(seconds: int) -> None`

持久化保存赛事列表自动刷新间隔（秒）。
