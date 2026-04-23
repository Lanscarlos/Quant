# 数据库 Schema 详解

## 概述

项目使用两个 SQLite 数据库，均以 WAL 模式运行，开启外键约束，`row_factory=sqlite3.Row`。

| 数据库 | 文件 | 用途 | 管理模块 |
|--------|------|------|----------|
| 实时库 | `data/quant.db` | 所有抓取的赛事、赔率数据 | `src/db/connection.py` + `schema.py` |
| 历史库 | `data/history.db` | 用户保存的分析快照 | `src/db/history_connection.py` + `history_schema.py` |

### 路径解析

```python
if getattr(sys, 'frozen', False):
    base = Path(sys.executable).parent   # 打包环境
else:
    base = Path(__file__).parent.parent.parent  # 开发环境（项目根目录）
db_path = base / "data" / "quant.db"
```

### 连接管理

两个数据库各自维护一个全局单例连接（`_conn`），首次调用 `get_conn()` / `get_history_conn()` 时创建：

```python
conn = sqlite3.connect(str(path), check_same_thread=False, timeout=5)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA journal_mode=WAL")
conn.execute("PRAGMA foreign_keys=ON")
```

---

## quant.db 表结构（17 张表）

### 1. leagues — 联赛字典

```sql
CREATE TABLE IF NOT EXISTS leagues (
    league_abbr    TEXT    PRIMARY KEY,
    league_name_cn TEXT,
    league_color   TEXT,
    country_id     INTEGER
);
```

### 2. teams — 球队字典

```sql
CREATE TABLE IF NOT EXISTS teams (
    team_id      INTEGER PRIMARY KEY,
    team_name_cn TEXT,
    team_name_en TEXT
);
```

### 3. matches — 赛事列表

```sql
CREATE TABLE IF NOT EXISTS matches (
    schedule_id       INTEGER PRIMARY KEY,
    match_time        TEXT    NOT NULL,
    status            INTEGER NOT NULL DEFAULT 0,   -- 0=未开赛, 1=上半场, 3=下半场, -1=完场
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
    league_name_cn    TEXT,                          -- 迁移新增
    league_table_fetched INTEGER NOT NULL DEFAULT 0, -- 迁移新增：积分榜是否已抓取
    fetched_at        TEXT NOT NULL DEFAULT (datetime('now', '+8 hours'))
);
```

索引：`match_time`, `status`, `league_abbr`, `home_team_id`, `away_team_id`

### 4. match_standings — 联赛排名详情

每场赛事产生 16 行：2 sides × 2 periods × 4 scopes。

```sql
CREATE TABLE IF NOT EXISTS match_standings (
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
    goal_diff     INTEGER,
    points        INTEGER,
    rank          INTEGER,
    win_rate      REAL,
    fetched_at    TEXT NOT NULL DEFAULT (datetime('now', '+8 hours')),
    UNIQUE(schedule_id, side, period, scope)
);
```

### 5. match_recent — 近 8 场比赛历史

每场赛事每侧最多 8 条记录。

```sql
CREATE TABLE IF NOT EXISTS match_recent (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id  INTEGER NOT NULL REFERENCES matches(schedule_id) ON DELETE CASCADE,
    side         TEXT    NOT NULL CHECK(side IN ('home', 'away')),
    match_id     INTEGER NOT NULL,
    date         TEXT,
    match_time   TEXT,       -- 迁移新增：用于计算赛前半小时赔率
    league       TEXT,
    home_id      INTEGER,
    home_name    TEXT,
    home_rank    INTEGER,    -- 迁移新增
    away_id      INTEGER,
    away_name    TEXT,
    away_rank    INTEGER,    -- 迁移新增
    home_ft      INTEGER,
    away_ft      INTEGER,
    ht_score     TEXT,
    handicap     TEXT,
    result       INTEGER,    -- 1=胜, 0=平, -1=负
    hc_result    INTEGER,    -- -2=无数据, -1=输, 0=走, 1=赢
    fetched_at   TEXT NOT NULL DEFAULT (datetime('now', '+8 hours')),
    UNIQUE(schedule_id, side, match_id)
);
```

### 6. match_h2h — 两队交手记录

每场赛事最多 20 条交手记录。

```sql
CREATE TABLE IF NOT EXISTS match_h2h (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id INTEGER NOT NULL REFERENCES matches(schedule_id) ON DELETE CASCADE,
    match_id    INTEGER NOT NULL,
    date        TEXT,
    league      TEXT,
    home_id     INTEGER,
    home_name   TEXT,
    home_rank   INTEGER,    -- 迁移新增
    away_id     INTEGER,
    away_name   TEXT,
    away_rank   INTEGER,    -- 迁移新增
    home_ft     INTEGER,
    away_ft     INTEGER,
    ht_score    TEXT,
    handicap    TEXT,
    hc_result   INTEGER,
    fetched_at  TEXT NOT NULL DEFAULT (datetime('now', '+8 hours')),
    UNIQUE(schedule_id, match_id)
);
```

### 7. odds_wh — 威廉希尔欧赔快照

```sql
CREATE TABLE IF NOT EXISTS odds_wh (
    schedule_id       INTEGER PRIMARY KEY,
    record_id         INTEGER,          -- 用于变赔历史 URL
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
    fetched_at        TEXT NOT NULL DEFAULT (datetime('now', '+8 hours')),
    no_data           INTEGER NOT NULL DEFAULT 0  -- 迁移新增：标记无数据的子比赛
);
```

### 8. odds_wh_history — 威廉希尔欧赔变盘历史

```sql
CREATE TABLE IF NOT EXISTS odds_wh_history (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id  INTEGER NOT NULL,
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
    is_opening   INTEGER NOT NULL DEFAULT 0,  -- 1=初盘
    win_dir      TEXT CHECK(win_dir  IN ('up', 'down', 'unchanged')),
    draw_dir     TEXT CHECK(draw_dir IN ('up', 'down', 'unchanged')),
    lose_dir     TEXT CHECK(lose_dir IN ('up', 'down', 'unchanged')),
    UNIQUE(schedule_id, change_time)
);
```

索引：`(schedule_id)`, `(schedule_id, is_opening, change_time DESC)`

### 9. odds_coral — 立博欧赔快照

结构与 `odds_wh` 相同（无 `no_data` 列）。

### 10. odds_coral_history — 立博欧赔变盘历史

结构与 `odds_wh_history` 相同。

### 11. odds_365 — Bet365 欧赔快照

结构与 `odds_coral` 相同。

### 12. odds_365_history — Bet365 欧赔变盘历史

结构与 `odds_wh_history` 相同。

### 13. asian_odds_365 — Bet365 亚盘快照

```sql
CREATE TABLE IF NOT EXISTS asian_odds_365 (
    schedule_id   INTEGER PRIMARY KEY REFERENCES matches(schedule_id) ON DELETE CASCADE,
    open_handicap TEXT,
    open_home     REAL,
    open_away     REAL,
    cur_handicap  TEXT,
    cur_home      REAL,
    cur_away      REAL,
    fetched_at    TEXT NOT NULL DEFAULT (datetime('now', '+8 hours'))
);
```

### 14. asian_odds_365_history — Bet365 亚盘变盘历史

```sql
CREATE TABLE IF NOT EXISTS asian_odds_365_history (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id  INTEGER NOT NULL,
    change_time  TEXT    NOT NULL,
    score        TEXT,
    home_odds    REAL,
    handicap     TEXT,
    away_odds    REAL,
    is_opening   INTEGER NOT NULL DEFAULT 0,
    home_dir     TEXT CHECK(home_dir IN ('up', 'down', 'unchanged')),
    away_dir     TEXT CHECK(away_dir IN ('up', 'down', 'unchanged')),
    UNIQUE(schedule_id, change_time)
);
```

### 15. over_under_365 — Bet365 大小球快照

```sql
CREATE TABLE IF NOT EXISTS over_under_365 (
    schedule_id   INTEGER PRIMARY KEY REFERENCES matches(schedule_id) ON DELETE CASCADE,
    open_goals    TEXT,
    open_over     REAL,
    open_under    REAL,
    cur_goals     TEXT,
    cur_over      REAL,
    cur_under     REAL,
    fetched_at    TEXT NOT NULL DEFAULT (datetime('now', '+8 hours'))
);
```

### 16. over_under_365_history — Bet365 大小球变盘历史

```sql
CREATE TABLE IF NOT EXISTS over_under_365_history (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id  INTEGER NOT NULL,
    change_time  TEXT    NOT NULL,
    score        TEXT,
    over_odds    REAL,
    goals_line   TEXT,
    under_odds   REAL,
    is_opening   INTEGER NOT NULL DEFAULT 0,
    over_dir     TEXT CHECK(over_dir  IN ('up', 'down', 'unchanged')),
    under_dir    TEXT CHECK(under_dir IN ('up', 'down', 'unchanged')),
    UNIQUE(schedule_id, change_time)
);
```

### 17. league_table_snapshot — 赛前联赛积分榜快照

```sql
CREATE TABLE IF NOT EXISTS league_table_snapshot (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id  INTEGER NOT NULL REFERENCES matches(schedule_id) ON DELETE CASCADE,
    scope        TEXT    NOT NULL CHECK(scope IN ('total', 'home', 'away')),
    rank         INTEGER NOT NULL,
    team_id      INTEGER NOT NULL,
    team_name    TEXT    NOT NULL,
    points       INTEGER,
    zone_flag    INTEGER NOT NULL DEFAULT -1,  -- 0=蓝区, 1=绿区, 2=灰区
    is_focus     INTEGER NOT NULL DEFAULT 0,   -- 1=本场参赛队
    fetched_at   TEXT    NOT NULL DEFAULT (datetime('now', '+8 hours')),
    UNIQUE(schedule_id, scope, rank)
);
```

---

## history.db 表结构（2 张表）

### 1. saved_matches — 列表展示 + 检索（反范式化）

```sql
CREATE TABLE IF NOT EXISTS saved_matches (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    schedule_id         INTEGER NOT NULL UNIQUE,
    saved_at            TEXT    NOT NULL DEFAULT (datetime('now', '+8 hours')),
    match_time          TEXT,
    home_team           TEXT,
    away_team           TEXT,
    league              TEXT,
    home_rank           INTEGER,
    away_rank           INTEGER,
    home_score          INTEGER,
    away_score          INTEGER,
    home_half_score     INTEGER,
    away_half_score     INTEGER,

    -- 威廉希尔赔率
    wh_open_win         REAL,
    wh_open_draw        REAL,
    wh_open_lose        REAL,
    wh_h30_win          REAL,    -- 迁移新增：赛前半小时赔率
    wh_h30_draw         REAL,
    wh_h30_lose         REAL,
    wh_cur_win          REAL,
    wh_cur_draw         REAL,
    wh_cur_lose         REAL,

    -- 立博赔率
    coral_open_win      REAL,
    coral_open_draw     REAL,
    coral_open_lose     REAL,
    coral_cur_win       REAL,
    coral_cur_draw      REAL,
    coral_cur_lose      REAL,

    -- Bet365 亚盘
    asian_open_handicap TEXT,
    asian_open_home     REAL,
    asian_open_away     REAL,
    asian_cur_handicap  TEXT,
    asian_cur_home      REAL,
    asian_cur_away      REAL,

    -- Bet365 大小球（迁移新增）
    ou_open_goals       TEXT,
    ou_open_over        REAL,
    ou_open_under       REAL,
    ou_cur_goals        TEXT,
    ou_cur_over         REAL,
    ou_cur_under        REAL,

    -- 积分 & 胜平负
    home_pts            INTEGER,
    away_pts            INTEGER,
    home_wdl_win        INTEGER,
    home_wdl_draw       INTEGER,
    home_wdl_loss       INTEGER,
    away_wdl_win        INTEGER,
    away_wdl_draw       INTEGER,
    away_wdl_loss       INTEGER,

    -- 用户输入
    analysis_note       TEXT,
    tags                TEXT
);
```

索引：`match_time`, `league`

### 2. saved_snapshots — 详情展示用 JSON 快照

```sql
CREATE TABLE IF NOT EXISTS saved_snapshots (
    saved_match_id    INTEGER PRIMARY KEY REFERENCES saved_matches(id) ON DELETE CASCADE,
    match_json        TEXT,
    extras_json       TEXT,
    recent_json       TEXT,
    h2h_json          TEXT,
    odds_json         TEXT,
    asian_odds_json   TEXT,
    league_table_json TEXT,    -- 迁移新增
    over_under_json   TEXT     -- 迁移新增
);
```

---

## 增量迁移机制

### quant.db 迁移 (`schema._migrate()`)

在 `create_all()` 执行完 DDL 后调用，使用 `_add_column_if_missing()` 安全添加新列：

```python
_add_column_if_missing(conn, "match_recent", "match_time", "TEXT")
_add_column_if_missing(conn, "odds_wh", "no_data", "INTEGER NOT NULL DEFAULT 0")
_add_column_if_missing(conn, "match_recent", "home_rank", "INTEGER")
_add_column_if_missing(conn, "match_recent", "away_rank", "INTEGER")
_add_column_if_missing(conn, "match_h2h", "home_rank", "INTEGER")
_add_column_if_missing(conn, "match_h2h", "away_rank", "INTEGER")
_add_column_if_missing(conn, "matches", "league_name_cn", "TEXT")
_add_column_if_missing(conn, "matches", "league_table_fetched", "INTEGER NOT NULL DEFAULT 0")
```

### history.db 迁移

在 `create_all()` 内通过 `PRAGMA table_info` 检查并 `ALTER TABLE ADD COLUMN`：
- `saved_matches`: `wh_h30_win/draw/lose`, `ou_open_goals/over/under`, `ou_cur_goals/over/under`
- `saved_snapshots`: `league_table_json`, `over_under_json`
