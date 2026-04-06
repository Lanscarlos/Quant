# Database Schema

数据库：SQLite
数据来源：[bf.titan007.com](https://bf.titan007.com) / [zq.titan007.com](https://zq.titan007.com) / [1x2.titan007.com](https://1x2.titan007.com)

---

## 范式说明

| 问题 | 位置 | 范式 | 处理方式 |
|------|------|------|----------|
| `home/away_team_cn/en` 传递依赖于 `team_id` | `matches` | 违反 3NF | 拆出 `teams` 表 |
| `league_name_cn/color/country_id` 传递依赖于 `league_abbr` | `matches` | 违反 3NF | 拆出 `leagues` 表 |
| `status_label` 完全由 `status` 静态推导 | `matches` | 派生列 | 删除，应用层映射 |
| `goal_diff = goals_for - goals_against` | `match_standings` | 派生列 | 保留，源数据直接提供，避免计算 |
| `odds_history.schedule_id / company_id` 可由 `record_id` 推导 | `odds_history` | 有意反范式 | 保留，避免高频查询时 JOIN `match_odds` |

---

## 表关系概览

```
leagues (1) ──── (N) matches
teams (1) ──────── (N) matches  [home_team_id / away_team_id]
matches (1) ────── (N) match_standings
matches (1) ────── (N) match_odds
companies (1) ──── (N) match_odds
match_odds (1) ─── (N) odds_history
```

---

## 1. `leagues` — 联赛字典

**数据来源**：从 `match_list.py` 结果中抽取去重

> 从 `matches` 表拆分。`league_abbr` 在源数据中是联赛的唯一标识，`league_name_cn`、`league_color`、`country_id` 均函数依赖于它，不应重复存入每条赛事记录。

```sql
CREATE TABLE leagues (
    league_abbr    TEXT    PRIMARY KEY,
    league_name_cn TEXT,
    league_color   TEXT,
    country_id     INTEGER
);
```

| 字段 | 类型 | 可空 | 说明 |
|------|------|------|------|
| `league_abbr` | TEXT | NOT NULL | 联赛英文缩写（主键），如 `JPN D1`、`AUS SASL` |
| `league_name_cn` | TEXT | 可空 | 联赛名称（简体中文），如「日职联」 |
| `league_color` | TEXT | 可空 | 页面色标，十六进制颜色值，如 `#009900` |
| `country_id` | INTEGER | 可空 | 国家 ID |

---

## 2. `teams` — 球队字典

**数据来源**：从 `match_list.py` 结果中抽取去重

> 从 `matches` 表拆分。`team_name_cn`、`team_name_en` 函数依赖于 `team_id`，存入 `matches` 时每场比赛都重复一份队名，违反 3NF。

```sql
CREATE TABLE teams (
    team_id      INTEGER PRIMARY KEY,
    team_name_cn TEXT,
    team_name_en TEXT
);
```

| 字段 | 类型 | 可空 | 说明 |
|------|------|------|------|
| `team_id` | INTEGER | NOT NULL | 球队唯一 ID（主键），来自 titan007 |
| `team_name_cn` | TEXT | 可空 | 球队名称（简体中文），如「FC东京」 |
| `team_name_en` | TEXT | 可空 | 球队名称（英文），如 `FC Tokyo` |

---

## 3. `matches` — 赛事列表

**数据来源**：`match_list.py` → `https://bf.titan007.com/VbsXml/bfdata.js`

> `status_label` 已删除——它是 `status` 的静态映射（`-1`→完场 等），派生数据不应入库，应在应用层或查询层转换。联赛信息和队名均改为外键引用。

```sql
CREATE TABLE matches (
    schedule_id       INTEGER PRIMARY KEY,
    match_time        TEXT    NOT NULL,
    status            INTEGER NOT NULL DEFAULT 0,  -- 0=未开赛 1=上半场 3=下半场 -1=完场 -11=中断 -12=腰斩 -14=推迟
    league_abbr       TEXT    REFERENCES leagues(league_abbr),
    home_team_id      INTEGER NOT NULL REFERENCES teams(team_id),
    home_rank         INTEGER,
    away_team_id      INTEGER NOT NULL REFERENCES teams(team_id),
    away_rank         INTEGER,
    home_score        INTEGER,
    away_score        INTEGER,
    home_half_score   INTEGER,
    away_half_score   INTEGER,
    home_red_cards    INTEGER DEFAULT 0,
    away_red_cards    INTEGER DEFAULT 0,
    home_yellow_cards INTEGER DEFAULT 0,
    away_yellow_cards INTEGER DEFAULT 0,
    fetched_at        TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_matches_time        ON matches(match_time);
CREATE INDEX idx_matches_status      ON matches(status);
CREATE INDEX idx_matches_league      ON matches(league_abbr);
CREATE INDEX idx_matches_home_team   ON matches(home_team_id);
CREATE INDEX idx_matches_away_team   ON matches(away_team_id);
```

| 字段 | 类型 | 可空 | 说明 |
|------|------|------|------|
| `schedule_id` | INTEGER | NOT NULL | 比赛唯一 ID（主键），对应源数据 `scheduleID` |
| `match_time` | TEXT | NOT NULL | 比赛开始时间，格式 `YYYY-MM-DD HH:MM` |
| `status` | INTEGER | NOT NULL | 比赛状态码：`0`=未开赛，`1`=上半场，`3`=下半场，`-1`=完场，`-11`=中断，`-12`=腰斩，`-14`=推迟 |
| `league_abbr` | TEXT | 可空 | 外键 → `leagues.league_abbr` |
| `home_team_id` | INTEGER | NOT NULL | 外键 → `teams.team_id`（主队） |
| `home_rank` | INTEGER | 可空 | 主队赛前联赛排名（随赛事快照存储，不属于球队固定属性） |
| `away_team_id` | INTEGER | NOT NULL | 外键 → `teams.team_id`（客队） |
| `away_rank` | INTEGER | 可空 | 客队赛前联赛排名 |
| `home_score` | INTEGER | 可空 | 主队全场得分（赛前为空） |
| `away_score` | INTEGER | 可空 | 客队全场得分 |
| `home_half_score` | INTEGER | 可空 | 主队半场得分 |
| `away_half_score` | INTEGER | 可空 | 客队半场得分 |
| `home_red_cards` | INTEGER | 可空 | 主队红牌数 |
| `away_red_cards` | INTEGER | 可空 | 客队红牌数 |
| `home_yellow_cards` | INTEGER | 可空 | 主队黄牌数 |
| `away_yellow_cards` | INTEGER | 可空 | 客队黄牌数 |
| `fetched_at` | TEXT | NOT NULL | 数据抓取时间，默认 `datetime('now')` |

---

## 4. `match_standings` — 联赛排名详情

**数据来源**：`match_detail.py` → `https://zq.titan007.com/analysis/{match_id}sb.htm`

每场比赛产生 **16 行**，维度组合为：

- `side`：`home`（主队）/ `away`（客队）
- `period`：`ft`（全场）/ `ht`（半场）
- `scope`：`total`（总）/ `home`（主场）/ `away`（客场）/ `last6`（近 6 场）

> `goal_diff` 虽可由 `goals_for - goals_against` 计算得出，但源数据直接提供且常用于排序，保留为冗余字段。

```sql
CREATE TABLE match_standings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id   INTEGER NOT NULL REFERENCES matches(schedule_id) ON DELETE CASCADE,
    side          TEXT    NOT NULL CHECK(side   IN ('home', 'away')),
    period        TEXT    NOT NULL CHECK(period IN ('ft', 'ht')),
    scope         TEXT    NOT NULL CHECK(scope  IN ('total', 'home', 'away', 'last6')),
    played        INTEGER,
    win           INTEGER,
    draw          INTEGER,
    loss          INTEGER,
    goals_for     INTEGER,
    goals_against INTEGER,
    goal_diff     INTEGER,   -- 冗余：= goals_for - goals_against，源数据直接提供
    points        INTEGER,
    rank          INTEGER,
    win_rate      REAL,
    fetched_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(schedule_id, side, period, scope)
);

CREATE INDEX idx_standings_match ON match_standings(schedule_id);
```

| 字段 | 类型 | 可空 | 说明 |
|------|------|------|------|
| `id` | INTEGER | NOT NULL | 自增主键 |
| `schedule_id` | INTEGER | NOT NULL | 外键 → `matches.schedule_id` |
| `side` | TEXT | NOT NULL | 队伍角色：`home`=主队，`away`=客队 |
| `period` | TEXT | NOT NULL | 统计时段：`ft`=全场，`ht`=半场 |
| `scope` | TEXT | NOT NULL | 统计范围：`total`=总场次，`home`=主场场次，`away`=客场场次，`last6`=近 6 场 |
| `played` | INTEGER | 可空 | 已赛场次 |
| `win` | INTEGER | 可空 | 胜场数 |
| `draw` | INTEGER | 可空 | 平场数 |
| `loss` | INTEGER | 可空 | 负场数 |
| `goals_for` | INTEGER | 可空 | 进球数 |
| `goals_against` | INTEGER | 可空 | 失球数 |
| `goal_diff` | INTEGER | 可空 | 净胜球（冗余，= `goals_for - goals_against`） |
| `points` | INTEGER | 可空 | 积分 |
| `rank` | INTEGER | 可空 | 当前联赛排名 |
| `win_rate` | REAL | 可空 | 胜率，原始值 `"20.0%"` 标准化后存为小数 `0.20` |
| `fetched_at` | TEXT | NOT NULL | 数据抓取时间 |

> **查询示例**：获取主队全场总排名
> ```sql
> SELECT rank, win_rate FROM match_standings
> WHERE schedule_id = 2921107 AND side = 'home' AND period = 'ft' AND scope = 'total';
> ```

---

## 5. `companies` — 博彩公司字典

**数据来源**：从 `match_odds_list.py` 解析结果中抽取去重

```sql
CREATE TABLE companies (
    company_id   INTEGER PRIMARY KEY,
    company_name TEXT    NOT NULL,
    label        TEXT
);
```

| 字段 | 类型 | 可空 | 说明 |
|------|------|------|------|
| `company_id` | INTEGER | NOT NULL | 博彩公司唯一 ID（主键），来自 titan007 |
| `company_name` | TEXT | NOT NULL | 公司名称，如 `Bet 365`、`William Hill` |
| `label` | TEXT | 可空 | 分类标签，含国家标注，如 `36*(英国)`、`澳*` |

---

## 6. `match_odds` — 欧赔快照

**数据来源**：`match_odds_list.py` → `https://1x2d.titan007.com/{match_id}.js`

每场比赛中每家博彩公司一条记录，存储初盘与即时盘的完整赔率快照。

```sql
CREATE TABLE match_odds (
    record_id         INTEGER PRIMARY KEY,
    schedule_id       INTEGER NOT NULL REFERENCES matches(schedule_id) ON DELETE CASCADE,
    company_id        INTEGER NOT NULL REFERENCES companies(company_id),
    open_win          REAL,
    open_draw         REAL,
    open_lose         REAL,
    open_win_prob     REAL,
    open_draw_prob    REAL,
    open_lose_prob    REAL,
    open_payout_rate  REAL,
    cur_win           REAL,
    cur_draw          REAL,
    cur_lose          REAL,
    cur_win_prob      REAL,
    cur_draw_prob     REAL,
    cur_lose_prob     REAL,
    cur_payout_rate   REAL,
    kelly_win         REAL,
    kelly_draw        REAL,
    kelly_lose        REAL,
    hist_kelly_win    REAL,
    hist_kelly_draw   REAL,
    hist_kelly_lose   REAL,
    change_time       TEXT,
    flag1             INTEGER,
    flag2             INTEGER,
    fetched_at        TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE(schedule_id, company_id)
);

CREATE INDEX idx_odds_match ON match_odds(schedule_id);
```

| 字段 | 类型 | 可空 | 说明 |
|------|------|------|------|
| `record_id` | INTEGER | NOT NULL | titan007 赔率记录 ID（主键），是查询 `odds_history` 的必要参数 |
| `schedule_id` | INTEGER | NOT NULL | 外键 → `matches.schedule_id` |
| `company_id` | INTEGER | NOT NULL | 外键 → `companies.company_id` |
| `open_win` | REAL | 可空 | 初盘主胜赔率 |
| `open_draw` | REAL | 可空 | 初盘平局赔率 |
| `open_lose` | REAL | 可空 | 初盘客胜赔率 |
| `open_win_prob` | REAL | 可空 | 初盘主胜隐含概率（%），如 `33.89` |
| `open_draw_prob` | REAL | 可空 | 初盘平局隐含概率（%） |
| `open_lose_prob` | REAL | 可空 | 初盘客胜隐含概率（%） |
| `open_payout_rate` | REAL | 可空 | 初盘返还率（%），如 `91.5` |
| `cur_win` | REAL | 可空 | 即时主胜赔率 |
| `cur_draw` | REAL | 可空 | 即时平局赔率 |
| `cur_lose` | REAL | 可空 | 即时客胜赔率 |
| `cur_win_prob` | REAL | 可空 | 即时主胜隐含概率（%） |
| `cur_draw_prob` | REAL | 可空 | 即时平局隐含概率（%） |
| `cur_lose_prob` | REAL | 可空 | 即时客胜隐含概率（%） |
| `cur_payout_rate` | REAL | 可空 | 即时返还率（%） |
| `kelly_win` | REAL | 可空 | 当前凯利指数（主胜） |
| `kelly_draw` | REAL | 可空 | 当前凯利指数（平局） |
| `kelly_lose` | REAL | 可空 | 当前凯利指数（客胜） |
| `hist_kelly_win` | REAL | 可空 | 历史凯利指数（主胜） |
| `hist_kelly_draw` | REAL | 可空 | 历史凯利指数（平局） |
| `hist_kelly_lose` | REAL | 可空 | 历史凯利指数（客胜） |
| `change_time` | TEXT | 可空 | 最近一次赔率变动时间，标准化为 `YYYY-MM-DD HH:MM:SS` |
| `flag1` | INTEGER | 可空 | 标志位 1，含义待考证（通常为 `1`） |
| `flag2` | INTEGER | 可空 | 标志位 2，含义待考证（通常为 `0`） |
| `fetched_at` | TEXT | NOT NULL | 数据抓取时间 |

---

## 7. `odds_history` — 赔率历史变动

**数据来源**：`match_odds_history.py` → `https://1x2.titan007.com/OddsHistory.aspx?id={record_id}&sid={match_id}&cid={company_id}`

记录某场比赛中某家公司每一次赔率变动的完整快照，按时间倒序排列（最新变动在前）。

> `schedule_id` 和 `company_id` 可通过 `record_id → match_odds` JOIN 得到，此处**有意冗余存储**，避免高频查询时产生 JOIN，是性能优先的合理反范式。

```sql
CREATE TABLE odds_history (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id    INTEGER NOT NULL REFERENCES match_odds(record_id) ON DELETE CASCADE,
    schedule_id  INTEGER NOT NULL,   -- 有意冗余，避免 JOIN match_odds
    company_id   INTEGER NOT NULL,   -- 有意冗余，方便按公司过滤
    win          REAL,
    draw         REAL,
    lose         REAL,
    win_prob     REAL,
    draw_prob    REAL,
    lose_prob    REAL,
    payout_rate  REAL,
    kelly_win    REAL,
    kelly_draw   REAL,
    kelly_lose   REAL,
    change_time  TEXT    NOT NULL,
    is_opening   INTEGER NOT NULL DEFAULT 0,
    win_dir      TEXT CHECK(win_dir  IN ('up', 'down', 'unchanged')),
    draw_dir     TEXT CHECK(draw_dir IN ('up', 'down', 'unchanged')),
    lose_dir     TEXT CHECK(lose_dir IN ('up', 'down', 'unchanged')),
    UNIQUE(record_id, change_time)
);

CREATE INDEX idx_odds_history_rid   ON odds_history(record_id);
CREATE INDEX idx_odds_history_match ON odds_history(schedule_id);
```

| 字段 | 类型 | 可空 | 说明 |
|------|------|------|------|
| `id` | INTEGER | NOT NULL | 自增主键 |
| `record_id` | INTEGER | NOT NULL | 外键 → `match_odds.record_id` |
| `schedule_id` | INTEGER | NOT NULL | 冗余字段，方便按场次直接查询 |
| `company_id` | INTEGER | NOT NULL | 冗余字段，方便按公司过滤 |
| `win` | REAL | 可空 | 本次变动后的主胜赔率 |
| `draw` | REAL | 可空 | 本次变动后的平局赔率 |
| `lose` | REAL | 可空 | 本次变动后的客胜赔率 |
| `win_prob` | REAL | 可空 | 主胜隐含概率（%） |
| `draw_prob` | REAL | 可空 | 平局隐含概率（%） |
| `lose_prob` | REAL | 可空 | 客胜隐含概率（%） |
| `payout_rate` | REAL | 可空 | 返还率（%） |
| `kelly_win` | REAL | 可空 | 凯利指数（主胜） |
| `kelly_draw` | REAL | 可空 | 凯利指数（平局） |
| `kelly_lose` | REAL | 可空 | 凯利指数（客胜） |
| `change_time` | TEXT | NOT NULL | 赔率变动时间，原始 `"03-07 07:18"` 写入时补全年份为 `YYYY-MM-DD HH:MM` |
| `is_opening` | INTEGER | NOT NULL | 是否为初盘：`1`=是，`0`=否 |
| `win_dir` | TEXT | 可空 | 主胜赔率变动方向：`up` / `down` / `unchanged` |
| `draw_dir` | TEXT | 可空 | 平局赔率变动方向 |
| `lose_dir` | TEXT | 可空 | 客胜赔率变动方向 |

> **查询示例**：获取某公司初盘与最新赔率对比
> ```sql
> SELECT
>     MAX(CASE WHEN is_opening = 1 THEN win  END) AS open_win,
>     MAX(CASE WHEN is_opening = 1 THEN draw END) AS open_draw,
>     MAX(CASE WHEN is_opening = 1 THEN lose END) AS open_lose,
>     MIN(change_time)                             AS opened_at,
>     MAX(change_time)                             AS last_changed_at
> FROM odds_history
> WHERE record_id = 151025873;
> ```

---

## 数据写入注意事项

| 事项 | 说明 |
|------|------|
| `status_label` | 不入库，在应用层用字典映射：`{0:"未开赛", 1:"上半场", 3:"下半场", -1:"完场", -11:"中断", -12:"腰斩", -14:"推迟"}` |
| `win_rate` 归一化 | 原始值 `"20.0%"` → 去掉 `%` 除以 100 → 存 `0.20` |
| `match_odds.change_time` 格式 | 原始 `"2026,03-1,06,23,30,00"` 需解析为 `"2026-03-06 23:30:00"` |
| `odds_history.change_time` 格式 | 原始 `"03-07 07:18"` 缺少年份，写入时需结合 `matches.match_time` 补全年份 |
| 写入顺序 | `leagues` → `teams` → `matches` → `match_standings` / `companies` → `match_odds` → `odds_history` |
| `leagues` / `teams` / `companies` 写入策略 | `INSERT OR IGNORE`，字典表只写一次 |
| `matches` / `match_standings` / `match_odds` 更新策略 | `INSERT OR REPLACE`，以各自 UNIQUE 约束保持幂等 |