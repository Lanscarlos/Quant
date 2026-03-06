# 数据抓取方案与 SQLite 表结构设计

## 一、数据来源分析

### 1. match_list（比赛列表）
来源页面：`bf.titan007.com/football/Over_YYYYMMDD.htm` 等

数据以 JavaScript 数组 `A` 的形式嵌入页面，每条记录代表一场比赛。核心字段：

| 数组索引 | 含义 |
|---|---|
| `A[i][0]` | 比赛 ID（scheduleID） |
| `A[i][1]` | 联赛颜色标识 |
| `A[i][2/3]` | 联赛名称（简/繁体） |
| `A[i][11]` | 比赛时间戳 |
| `A[i][13]` | 比赛状态（0=未开赛, 1=上半场, 3=下半场, -1=完场） |
| `A[i][14/15]` | 主队/客队全场得分 |
| `A[i][16/17]` | 主队/客队半场得分 |
| `A[i][18/19]` | 主队/客队红牌数 |
| `A[i][20/21]` | 主队/客队黄牌数 |
| `A[i][22/23]` | 主队/客队联赛排名 |
| `A[i][37/38]` | 主队/客队 ID |
| `A[i][40]` | 国家 ID |

**抓取内容：** 指定日期的所有比赛基础信息、实时状态、比分。

---

### 2. match_detail（比赛详情分析页）
来源页面：`zq.titan007.com/analysis/{scheduleID}cn.htm`

包含以下 JavaScript 变量：

| 变量 | 含义 |
|---|---|
| `scheduleID` | 比赛 ID |
| `h2h_home / h2h_away` | 主/客队 ID |
| `hometeam / guestteam` | 主/客队名称 |
| `strTime` | 比赛时间 |
| `v_data` | 两队交锋历史记录数组 |
| `h_data` | 主队近期比赛记录数组 |
| `a_data` | 客队近期比赛记录数组 |
| `h2_data` | 主队主场近期记录 |
| `a2_data` | 客队客场近期记录 |
| `Vs_hOdds` | 相关历史比赛的亚让盘数据 |
| `Vs_eOdds` | 相关历史比赛的欧赔数据 |
| `totalScoreStr` | 联赛总积分榜 |
| `homeScoreStr` | 联赛主场积分榜 |
| `guestScoreStr` | 联赛客场积分榜 |

历史记录数组（`h_data` / `a_data` / `v_data` 等）每条记录格式：
`[日期, 联赛ID, 联赛名, 颜色, 主队ID, 主队名(含排名), 客队ID, 客队名(含排名), 主场全场得分, 客场全场得分, 半场比分, ..., scheduleID, 角球主, 角球客, 联赛URL, 胜负标识, ...]`

页面 `porlet_5` 区块还含有联赛积分排名 HTML 表格（全场/主场/客场/近6场），字段包括：赛/胜/平/负/得/失/净/积分/排名/胜率。

**抓取内容：** 两队历史交锋、各队近期战绩、亚欧赔参考数据、联赛积分榜。

---

### 3. match_odd_list（欧赔列表）
来源页面：`1x2.titan007.com/oddslist/{scheduleID}_2.htm`

展示该场比赛所有博彩公司的欧赔数据，表头列：

| 列 | 含义 |
|---|---|
| 公司名 | 博彩公司 |
| 初/即 | 初盘 or 即时盘 |
| 主胜 / 和 / 客胜 | 欧赔三项赔率 |
| 主胜率 / 和率 / 客胜率 | 由即时赔率换算的概率 |
| 返还率 | 公司水位（越高对投注者越有利） |
| 凯利指数（主/和/客） | 凯利值，>1 红色加粗表示风险高 |
| 变化时间 | 最近一次赔率变动时间 |
| 历史指数 | 链接至该公司历史走势 |

底部汇总行：初盘/即时的最高值、最低值、平均值。

**抓取内容：** 所有公司的初盘与即时欧赔三项赔率、返还率、凯利指数、变化时间。

---

### 4. match_odd_history（欧赔历史走势）
来源页面：`1x2.titan007.com/history/{scheduleID}_{companyID}_2.htm`（推测）

展示某场比赛某个公司的完整历史赔率变动记录，列：

| 列 | 含义 |
|---|---|
| 主胜 / 和局 / 客胜 | 三项赔率 |
| 主胜率 / 和率 / 客胜率 | 换算概率 |
| 返还率 | 水位 |
| 凯利指数（主/和/客） | 凯利值 |
| 变化时间 | 变动时间，最早一条标注"(初盘)" |

示例数据（威*英国，2917854场次）：
- 初盘 08:06：7.50 / 4.75 / 1.30，返还率 89.84%
- 17:19：9.50 / 5.00 / 1.20，返还率 87.83%
- 18:23：10.00 / 5.00 / 1.20，返还率 88.24%

**抓取内容：** 每次赔率变动的完整快照（含初盘）。

---

## 二、需要抓取的数据汇总

| 数据类型 | 来源页面 | 优先级 |
|---|---|---|
| 比赛基础信息（联赛/球队/时间/状态/比分） | match_list | 高 |
| 两队历史交锋记录 | match_detail | 高 |
| 主/客队近期战绩（含主客场分类） | match_detail | 高 |
| 联赛积分榜（总/主场/客场） | match_detail | 高 |
| 所有公司欧赔（初盘+即时） | match_odd_list | 高 |
| 公司欧赔历史走势 | match_odd_history | 中 |
| 历史比赛关联亚让盘参考 | match_detail (Vs_hOdds) | 中 |
| 历史比赛关联欧赔参考 | match_detail (Vs_eOdds) | 中 |

---

## 三、SQLite 表结构设计

### 3.1 leagues（联赛）

```sql
CREATE TABLE leagues (
    id          INTEGER PRIMARY KEY,   -- 联赛 ID，如 1741
    name        TEXT    NOT NULL,      -- 联赛名称，如 "布隆迪超"
    country     TEXT,                  -- 国家/地区
    color       TEXT,                  -- 联赛颜色标识（页面用于渲染）
    created_at  TEXT    DEFAULT (datetime('now'))
);
```

---

### 3.2 teams（球队）

```sql
CREATE TABLE teams (
    id          INTEGER PRIMARY KEY,   -- 球队 ID，如 74031
    name        TEXT    NOT NULL,      -- 球队名称，如 "绿色农足"
    league_id   INTEGER,               -- 主要所属联赛
    created_at  TEXT    DEFAULT (datetime('now')),
    FOREIGN KEY (league_id) REFERENCES leagues(id)
);
```

---

### 3.3 matches（比赛）

```sql
CREATE TABLE matches (
    id              INTEGER PRIMARY KEY,   -- scheduleID，如 2917854
    league_id       INTEGER NOT NULL,
    season          TEXT,                  -- 赛季，如 "2025-2026"
    round           INTEGER,               -- 轮次
    match_time      TEXT,                  -- 比赛时间，ISO8601 格式
    home_team_id    INTEGER NOT NULL,
    away_team_id    INTEGER NOT NULL,
    status          INTEGER DEFAULT 0,     -- 0=未开赛,1=上半场,3=下半场,-1=完场,-11/-12=中断等
    home_score      INTEGER,               -- 全场主队得分
    away_score      INTEGER,               -- 全场客队得分
    home_half_score INTEGER,               -- 半场主队得分
    away_half_score INTEGER,               -- 半场客队得分
    home_rank       INTEGER,               -- 主队当前联赛排名
    away_rank       INTEGER,               -- 客队当前联赛排名
    home_red_cards  INTEGER DEFAULT 0,
    away_red_cards  INTEGER DEFAULT 0,
    home_yellow_cards INTEGER DEFAULT 0,
    away_yellow_cards INTEGER DEFAULT 0,
    weather         TEXT,
    temperature     TEXT,
    scraped_at      TEXT    DEFAULT (datetime('now')),
    FOREIGN KEY (league_id)    REFERENCES leagues(id),
    FOREIGN KEY (home_team_id) REFERENCES teams(id),
    FOREIGN KEY (away_team_id) REFERENCES teams(id)
);
```

---

### 3.4 match_history（历史战绩记录）

存储从 match_detail 页解析出的 `h_data`、`a_data`、`v_data`、`h2_data`、`a2_data`。

```sql
CREATE TABLE match_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ref_match_id    INTEGER NOT NULL,  -- 所属分析页的比赛 ID（当前场次）
    data_type       TEXT    NOT NULL,  -- 'h'=主队近期,'a'=客队近期,'v'=两队交锋,
                                       -- 'h2'=主队主场,'a2'=客队客场
    hist_match_id   INTEGER,           -- 历史比赛的 scheduleID
    hist_date       TEXT,              -- 历史比赛日期，如 "26-03-01"
    league_id       INTEGER,
    home_team_id    INTEGER,
    away_team_id    INTEGER,
    home_score      INTEGER,           -- 全场主队得分
    away_score      INTEGER,           -- 全场客队得分
    half_score      TEXT,              -- 上半场比分字符串，如 "1-0"
    home_rank       INTEGER,           -- 比赛时主队排名
    away_rank       INTEGER,           -- 比赛时客队排名
    home_corners    INTEGER,           -- 主队角球数
    away_corners    INTEGER,           -- 客队角球数
    result          INTEGER,           -- 1=主胜, 0=平, -1=主负（相对主队）
    scraped_at      TEXT    DEFAULT (datetime('now')),
    FOREIGN KEY (ref_match_id) REFERENCES matches(id)
);
```

---

### 3.5 league_standings（联赛积分榜）

```sql
CREATE TABLE league_standings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ref_match_id    INTEGER NOT NULL,  -- 关联的分析页比赛 ID
    team_id         INTEGER NOT NULL,
    team_name       TEXT,
    rank            INTEGER,           -- 排名
    stand_type      TEXT NOT NULL,     -- 'total'=总,'home'=主场,'away'=客场
    played          INTEGER,           -- 已赛场次
    wins            INTEGER,
    draws           INTEGER,
    losses          INTEGER,
    goals_for       INTEGER,           -- 得球
    goals_against   INTEGER,           -- 失球
    goal_diff       INTEGER,           -- 净胜球
    points          INTEGER,           -- 积分
    win_rate        REAL,              -- 胜率，如 0.043
    is_relegation   INTEGER DEFAULT 0, -- 是否降级区
    scraped_at      TEXT    DEFAULT (datetime('now')),
    FOREIGN KEY (ref_match_id) REFERENCES matches(id),
    FOREIGN KEY (team_id)      REFERENCES teams(id)
);
```

---

### 3.6 companies（博彩公司）

```sql
CREATE TABLE companies (
    id          INTEGER PRIMARY KEY,   -- 公司 ID，如 82(Bet365), 115, 281
    name        TEXT    NOT NULL,      -- 公司名称
    name_en     TEXT,                  -- 英文名
    type        TEXT,                  -- 'mainstream'=主流,'exchange'=交易所,'other'=其他
    created_at  TEXT    DEFAULT (datetime('now'))
);
```

---

### 3.7 odds_european（欧赔列表快照）

对应 match_odd_list 页，每次抓取保存所有公司的即时与初盘。

```sql
CREATE TABLE odds_european (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id        INTEGER NOT NULL,
    company_id      INTEGER NOT NULL,
    odds_type       TEXT    NOT NULL,  -- 'init'=初盘, 'real'=即时
    home_win        REAL,              -- 主胜赔率
    draw            REAL,              -- 平局赔率
    away_win        REAL,              -- 客胜赔率
    home_win_rate   REAL,              -- 主胜概率
    draw_rate       REAL,              -- 平局概率
    away_win_rate   REAL,              -- 客胜概率
    return_rate     REAL,              -- 返还率
    kelly_home      REAL,              -- 凯利主胜
    kelly_draw      REAL,              -- 凯利平
    kelly_away      REAL,              -- 凯利客胜
    change_time     TEXT,              -- 赔率变化时间
    scraped_at      TEXT    DEFAULT (datetime('now')),
    FOREIGN KEY (match_id)   REFERENCES matches(id),
    FOREIGN KEY (company_id) REFERENCES companies(id)
);

CREATE INDEX idx_odds_eu_match ON odds_european(match_id, odds_type);
```

---

### 3.8 odds_european_history（欧赔历史走势）

对应 match_odd_history 页，记录某公司对某场比赛赔率的每次变动。

```sql
CREATE TABLE odds_european_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id        INTEGER NOT NULL,
    company_id      INTEGER NOT NULL,
    home_win        REAL,
    draw            REAL,
    away_win        REAL,
    home_win_rate   REAL,
    draw_rate       REAL,
    away_win_rate   REAL,
    return_rate     REAL,
    kelly_home      REAL,
    kelly_draw      REAL,
    kelly_away      REAL,
    change_time     TEXT    NOT NULL,  -- 赔率变动时间（唯一标识一条记录）
    is_opening      INTEGER DEFAULT 0, -- 1=初盘（最早一条）
    scraped_at      TEXT    DEFAULT (datetime('now')),
    FOREIGN KEY (match_id)   REFERENCES matches(id),
    FOREIGN KEY (company_id) REFERENCES companies(id),
    UNIQUE (match_id, company_id, change_time)
);

CREATE INDEX idx_odds_eu_hist_match ON odds_european_history(match_id, company_id);
```

---

### 3.9 odds_asian（亚让盘历史参考）

来自 match_detail 页的 `Vs_hOdds`，记录相关历史比赛的亚让数据供参考分析。

```sql
CREATE TABLE odds_asian (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id        INTEGER NOT NULL,  -- 该条数据对应的历史比赛 scheduleID
    ref_match_id    INTEGER NOT NULL,  -- 关联的当前分析页比赛 ID
    company_id      INTEGER NOT NULL,
    -- 初盘
    init_home       REAL,              -- 初盘主队水位
    init_handicap   REAL,              -- 初盘让球（负=主让，正=客让）
    init_away       REAL,              -- 初盘客队水位
    init_total      REAL,              -- 初盘大小球线
    -- 即时盘
    real_home       REAL,
    real_handicap   REAL,
    real_away       REAL,
    real_total      REAL,
    scraped_at      TEXT    DEFAULT (datetime('now')),
    FOREIGN KEY (match_id)     REFERENCES matches(id),
    FOREIGN KEY (ref_match_id) REFERENCES matches(id),
    FOREIGN KEY (company_id)   REFERENCES companies(id)
);
```

---

## 四、表关系概览

```
leagues ──< matches >── teams
               │
               ├──< match_history
               ├──< league_standings >── teams
               ├──< odds_european >── companies
               ├──< odds_european_history >── companies
               └──< odds_asian >── companies
```

---

## 五、抓取流程建议

```
1. 抓取 match_list
   └─ 写入 leagues / teams / matches 表

2. 对每场目标比赛，抓取 match_detail
   └─ 写入 match_history / league_standings / odds_asian（Vs_hOdds）

3. 对每场目标比赛，抓取 match_odd_list
   └─ 写入 companies / odds_european

4. 对关键公司，抓取 match_odd_history
   └─ 写入 odds_european_history
```

> 注意：titan007 的比赛列表数据实际以 JS 文件形式动态加载（不在 HTML 中），抓取时需抓取对应的 `.js` 数据文件并解析其中的数组，而非直接解析 HTML 表格。