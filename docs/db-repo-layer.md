# DB Repository 层 API 参考

Repository 层位于 `src/db/repo/`，每个模块对应一张或一组数据库表，封装 SQL 读写操作。

---

## matches.py — 赛事表

### `upsert_matches(conn, records) -> int`

批量插入或替换赛事行（来自 match_list 抓取结果）。

- **策略**：`INSERT OR REPLACE`
- **参数**：`records` — 每个 dict 含 `scheduleID`, `match_time`, `status`, `league_abbr`, `home_team_id`, `away_team_id` 等字段
- **返回值**：写入行数

### `upsert_match_basics(conn, schedule_id, match_time, home_team_id, away_team_id, league_name_cn=None) -> None`

插入或更新赛事基础信息。

- **策略**：`INSERT ... ON CONFLICT DO UPDATE`，对已有行只更新非空字段，同时刷新 `fetched_at`

### `upsert_match_score(conn, schedule_id, home_score, away_score, status) -> None`

更新赛事比分与状态。若数据库中已是完赛状态（status=-1），则不再覆盖。

### `ensure_match_stub(conn, schedule_id, match_time, home_team_id, away_team_id) -> None`

仅在赛事不存在时插入最小骨架记录。

- **策略**：`INSERT OR IGNORE`

---

## teams.py — 球队表

### `upsert_teams(conn, records) -> int`

批量插入球队行（来自 match_list 的 home/away 字段）。

- **策略**：`INSERT OR IGNORE`（队名写入一次不覆盖）
- **返回值**：插入的唯一球队行数

### `ensure_team(conn, team_id, name_cn) -> None`

仅在球队不存在时插入最小骨架记录。

- **策略**：`INSERT OR IGNORE`

### `refresh_team_name(conn, team_id, name_cn) -> None`

插入或刷新球队中文名。已存在时也会更新 `team_name_cn`（`name_cn` 为空时不覆盖）。

- **策略**：`INSERT ... ON CONFLICT DO UPDATE`

---

## standings.py — 联赛排名

### `upsert_standings(conn, record) -> int`

插入或替换排名行。每场赛事产生 16 行：2 sides × 2 periods × 4 scopes。

- **策略**：`INSERT OR REPLACE` on `UNIQUE(schedule_id, side, period, scope)`
- **参数**：`record` — `match_detail._parse_detail()` 的扁平字典，含 `home_ft_total_W` 等键
- **返回值**：写入行数

---

## recent_matches.py — 近期比赛

### `upsert_recent_matches(conn, record) -> int`

插入或替换近期比赛行。每场赛事每侧最多 8 条。

- **策略**：`INSERT OR REPLACE` on `UNIQUE(schedule_id, side, match_id)`
- **参数**：`record` — 含 `schedule_id`, `home_recent`, `away_recent`
- **返回值**：写入行数

---

## h2h_matches.py — 交手记录

### `upsert_h2h_matches(conn, schedule_id, records) -> int`

插入或替换交手记录行。

- **策略**：`INSERT OR REPLACE` on `UNIQUE(schedule_id, match_id)`
- **参数**：`records` — `_parse_match_array(html, 'v_data')` 的输出列表
- **返回值**：写入行数

---

## odds.py — 欧赔快照（威廉 / 立博 / 365）

### `upsert_wh(conn, schedule_id, r) -> bool`

插入或替换威廉希尔欧赔快照。

### `upsert_coral(conn, schedule_id, r) -> bool`

插入或替换立博欧赔快照。

### `upsert_365(conn, schedule_id, r) -> bool`

插入或替换 Bet365 欧赔快照。

- **策略**：均为 `INSERT OR REPLACE` on `schedule_id` (PRIMARY KEY)
- **参数**：`r` — 含 `open_win`, `cur_win`, `kelly_win`, `record_id` 等字段的 dict
- **返回值**：`True`

---

## odds_history.py — 欧赔变盘历史（威廉 / 立博 / 365）

### `upsert_wh_history(conn, schedule_id, records, match_year) -> int`

插入威廉希尔欧赔变盘历史行。

### `upsert_coral_history(conn, schedule_id, records, match_year) -> int`

插入立博欧赔变盘历史行。

### `upsert_365_history(conn, schedule_id, records, match_year) -> int`

插入 Bet365 欧赔变盘历史行。

- **策略**：均为 `INSERT OR IGNORE` on `UNIQUE(schedule_id, change_time)`（历史不可变）
- **参数**：
  - `records` — 含 `win`, `draw`, `lose`, `change_time`, `is_opening`, `win_dir` 等字段
  - `match_year` — 用于补全 "MM-DD HH:MM" 时间戳为完整 ISO 格式
- **返回值**：写入行数

---

## asian_odds.py — Bet365 亚盘快照

### `upsert_365(conn, schedule_id, r) -> bool`

插入或替换 Bet365 亚盘快照。

- **策略**：`INSERT OR REPLACE` on `schedule_id` (PRIMARY KEY)
- **FK 守卫**：若 `matches` 表中无对应记录，返回 `False`
- **参数**：`r` — 含 `open_handicap`, `open_home`, `open_away`, `cur_handicap`, `cur_home`, `cur_away`

---

## asian_odds_history.py — Bet365 亚盘变盘历史

### `upsert_365_history(conn, schedule_id, records, match_year) -> int`

插入 Bet365 亚盘变盘历史行。

- **策略**：`INSERT OR IGNORE` on `UNIQUE(schedule_id, change_time)`
- **时间补全**：`_complete_time("3-19 07:18", 2026)` → `"2026-03-19 07:18"`

---

## over_under.py — Bet365 大小球快照

### `upsert_over_under_365(conn, schedule_id, r) -> bool`

插入或替换 Bet365 大小球快照。

- **策略**：`INSERT OR REPLACE` on `schedule_id` (PRIMARY KEY)
- **FK 守卫**：若 `matches` 表中无对应记录，返回 `False`

---

## over_under_history.py — Bet365 大小球变盘历史

### `upsert_over_under_365_history(conn, schedule_id, records, match_year) -> int`

插入 Bet365 大小球变盘历史行。

- **策略**：`INSERT OR IGNORE` on `UNIQUE(schedule_id, change_time)`
- **返回值**：写入行数

---

## league_table.py — 联赛积分榜快照

### `upsert_league_table(conn, record) -> int`

将解析好的积分榜数据写入 `league_table_snapshot` 表。

- **策略**：`INSERT OR REPLACE` on `UNIQUE(schedule_id, scope, rank)`
- **参数**：`record` — 含 `schedule_id`, `home_team_id`, `away_team_id`, `league_table_total/home/away`
- **返回值**：写入行数（总/主/客场三榜合计）

### `load_league_table(conn, schedule_id, scope='total') -> list[dict]`

读取指定赛事的积分榜快照，按 rank 升序排列。

- **返回值**：`[{'rank', 'team_id', 'team_name', 'points', 'zone_flag', 'is_focus'}, ...]`

---

## companies.py — 博彩公司字典

### `upsert_companies(conn, records) -> int`

插入博彩公司行。

- **策略**：`INSERT OR IGNORE`
- **参数**：`records` — 含 `company_id`, `company_name`, `label`
- **返回值**：插入的唯一公司行数

---

## history.py — 历史数据（history.db）

### `save_match(mid) -> int`

从 quant.db 读取赛事所有数据，写入 history.db。

- **策略**：`INSERT OR REPLACE` on `schedule_id`（重复保存会覆盖）
- **返回值**：`saved_matches.id`
- **写入表**：`saved_matches`（反范式化平铺行）+ `saved_snapshots`（JSON 快照）

### `load_snapshot(schedule_id) -> dict | None`

从 history.db 加载已保存的赛事快照。

- **返回值**：与 `load_all_from_quant()` 相同结构的 dict：`{match, extras, recent, h2h, odds, asian_odds, over_under, league_table}`

### `list_saved_matches(filters=None) -> list[dict]`

查询已保存赛事列表，支持筛选。

- **筛选键**：

| key | 说明 |
|-----|------|
| `time_from` | `match_time >= value` |
| `time_to` | `match_time <= value + ' 23:59:59'` |
| `league` | `list[str]`，精确 IN 匹配 |
| `team` | `list[str]`，精确 IN 匹配（受 `team_role` 控制） |
| `team_role` | `'home'` / `'away'` / `'both'`（默认 `'both'`） |
| `odds_type` | 列名（必须在白名单 `_ODDS_COLS` 中） |
| `odds_min` / `odds_max` | 赔率范围 |
| `limit` | `LIMIT n` |

### `list_distinct_leagues() -> list[str]`

返回已保存赛事中的去重联赛名列表。

### `list_distinct_teams() -> list[str]`

返回已保存赛事中的去重球队名列表（主客合并）。

### `backfill_h30() -> int`

补全旧记录中缺失的 `wh_h30_*`（赛前半小时威廉赔率）列。

### `backfill_recent_h2h() -> int`

补全旧快照中近期/交手不足 8 条的记录。

### `export_to_json(filters) -> str`

将筛选后的数据序列化为 JSON 字符串（含完整快照，用于数据迁移）。

### `export_to_csv(filters) -> str`

将筛选后的数据序列化为 CSV 字符串（UTF-8-BOM，供 Excel/WPS 直接打开）。

### `import_from_json(content, overwrite=False) -> dict`

将 JSON 字符串导入到 history.db。

- **参数**：
  - `content`: JSON 文件内容
  - `overwrite`: `True` 覆盖已存在记录，`False` 跳过
- **返回值**：`{'imported': int, 'skipped': int, 'existed': int, 'errors': list[str]}`
