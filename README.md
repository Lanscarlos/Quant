# Quant

足球赔率量化分析桌面应用。基于 [NiceGUI](https://nicegui.io/) native 模式运行，从 titan007.com 抓取赛事及赔率数据，存入本地 SQLite，以桌面窗口呈现分析界面。

## 快速开始

```bash
# 运行应用
python main.py

# 打包为可执行文件（onedir 模式）
python build.py
```

打包产物输出到 `dist/Quant/`。

---

## 目录结构

```
Quant/
├── main.py          # 入口：启动 NiceGUI native 窗口
├── build.py         # PyInstaller 打包脚本
├── assets/          # 应用图标等静态资源
├── data/            # 运行时数据目录（自动创建）
│   ├── quant.db     # 实时数据库（所有抓取数据）
│   ├── history.db   # 历史数据库（用户保存的分析快照）
│   └── config.json  # 应用配置（自动刷新间隔等）
├── design/          # UI 设计稿（PNG 原型图）
├── scripts/         # 开发辅助脚本（文档转换、数据源探查等）
├── build/           # PyInstaller 中间产物
├── dist/            # 打包输出（dist/Quant/）
└── src/             # 业务代码
    ├── ui/          # 界面层
    ├── service/     # 数据抓取与业务逻辑层
    ├── db/          # 数据库访问层
    ├── algorithm/   # 算法模块（新增，当前为空占位）
    └── scraper/     # 遗留抓取模块（当前流程已不使用）
```

---

## src/ 详细说明

### ui/ — 界面层

| 文件/目录 | 作用 |
|-----------|------|
| `index.py` | 应用常量（`PORT=19193`、`NAME`、`ICON`、`SIZE=(1260,840)`）；注册 NiceGUI 页面路由；完成各页面回调的串联（赛事列表 → 抓取 → 结论） |
| `router.py` | 自定义路由器。基于 `ui.tab_panels` 实现：`mount()` 时预渲染所有页面，`navigate()` 切换 tab 显示/隐藏，不重新渲染 |
| `frame/navigation_bar.py` | 左侧导航栏（56px 宽）；包含赛事列表、抓取数据、结论、设置四个入口；高亮当前页 |
| `page/match_list/` | **赛事列表页**。从 DB 读取经浏览器筛选的赛事，展示历史数据表格（赔率/赛果）；主客队名以 `[N]` 前缀显示排名；自动定时刷新（间隔可配置）；底部附威廉/立博两套"平赔平局值"分析面板 |
| `page/fetch/` | **抓取数据页** |
| `page/fetch/index.py` | 页面主体。用户输入赛事 URL 或 ID，分阶段展示进度（步骤圆圈 + 子任务列表）；支持中断；完成后自动跳转结论页；右下角浮标显示后台抓取状态 |
| `page/fetch/steps.py` | 6 个抓取步骤的定义，分 4 个阶段执行（同阶段并行）：赛事详情 → 子比赛赔率 → 欧赔+亚盘（并行）→ 欧赔历史+亚盘历史（并行）；每步包含新鲜度检查与依赖声明 |
| `page/fetch/progress.py` | `ProgressTracker` + `SubTask`：线程安全的子任务进度追踪，供 io_bound 线程调用，通过 `loop.call_soon_threadsafe` 触发 UI 刷新 |
| `page/fetch/_sub_odds.py` | 抓取近六场及交手记录中各子比赛的欧赔数据 |
| `page/conclusion/` | **结论页** |
| `page/conclusion/index.py` | 页面主体。展示赛事头部（队名/比分/联赛）、主客队近六场、交手记录、欧赔（威廉/立博）、亚盘（365）、联赛积分榜（可展开/收起，全场/半场 × 总/主/客）、分析过程与结论输入框；支持保存快照、重新抓取 |
| `page/conclusion/queries.py` | 结论页所有 DB 查询：基本赛事信息、近六场、交手、欧赔、亚盘、联赛积分榜；`load_all_from_quant()` 统一打包所有数据 |
| `page/conclusion/renderers.py` | 结论页各区块的 NiceGUI 渲染函数（近六场区块、交手区块、欧赔区块、亚盘区块） |
| `page/conclusion/formatters.py` | 数字/文本格式化工具函数（赔率显示、百分比、日期解析等） |
| `page/conclusion/columns.py` | ag-Grid 列定义（近六场、交手、欧赔、亚盘各自的列结构） |
| `page/history/` | **历史数据页**。列表展示已保存赛事分析快照；支持时间/联赛/球队/赔率四类筛选对话框；提供导出 JSON 和导入 JSON 功能；点击行跳转结论页（从 history.db 快照读取） |
| `page/settings/` | **设置页**。配置赛事列表自动刷新间隔（1–60 分钟，默认 20 分钟），持久化到 `data/config.json` |

---

### service/ — 数据抓取与业务逻辑层

| 文件 | 作用 |
|------|------|
| `match_list.py` | 从 `bf.titan007.com/VbsXml/bfdata.js` 抓取并解析当日赛事列表（GBK 编码 JS 文件，`^` 分隔字段）；写入 `leagues / teams / matches` 三张表 |
| `match_detail.py` | 从 `zq.titan007.com/analysis/{mid}sb.htm` 抓取赛事详情页（UTF-8 HTML）；解析联赛排名（BeautifulSoup `#porlet_5`）、近六场（`h_data/a_data` JS 数组）、交手记录（`v_data`）；写入 `match_standings / match_recent / match_h2h` |
| `euro_odds.py` | 抓取威廉希尔（公司 115）和立博（公司 82）的欧赔快照；写入 `odds_wh / odds_coral` |
| `euro_odds_history.py` | 抓取欧赔变盘历史；解析 HTML 字体颜色（绿=上涨/红=下跌）得出变动方向；写入 `odds_wh_history / odds_coral_history` |
| `asian_odds.py` | 抓取 Bet365 亚盘快照（GB2312 编码）；写入 `asian_odds_365` |
| `asian_odds_history.py` | 抓取 Bet365 亚盘变盘历史；写入 `asian_odds_365_history` |
| `live_score.py` | 抓取赛事实时比分与状态（`live.titan007.com`，GBK/UTF-8 自适应）；超过开球时间 110 分钟自动推断为完赛 |
| `browser_filter.py` | 读取 Chrome/Edge LevelDB `localStorage`，提取 `Bet007live_hiddenID` 键（用户在 titan007 上筛选的白名单赛事 ID，Base36 编码） |
| `freshness.py` | 新鲜度决策助手。`should_fetch_*()` 系列函数根据赛事状态（完场/进行中/未开赛）和上次抓取时间，决定是否需要重新发起 HTTP 请求 |
| `config.py` | 读写 `data/config.json`；管理 `refresh_interval`（默认 1200 秒） |

**新鲜度阈值一览：**

| 数据 | 完场 (-1) | 进行中 (1/3) | 未开赛 (0) |
|------|-----------|-------------|-----------|
| 赛事列表 | 永不重抓 | 2 分钟 | 10 分钟 |
| 赛事详情 | 抓一次即止 | 不重抓 | 6 小时 |
| 欧赔快照 | 抓一次即止 | 2 分钟 | 10 分钟 |
| 欧赔历史 | 抓一次即止 | 总是刷新 | 总是刷新 |
| 亚盘快照 | 抓一次即止 | 2 分钟 | 10 分钟 |
| 亚盘历史 | 抓一次即止 | 总是刷新 | 总是刷新 |

---

### db/ — 数据库访问层

| 文件/目录 | 作用 |
|-----------|------|
| `connection.py` | SQLite 单例连接（`data/quant.db`）；启用 WAL 模式和外键约束；`init_db()` 在应用启动时调用一次 |
| `schema.py` | 所有建表/建索引 DDL（幂等）；`create_all()` 在 `init_db()` 中调用；`_migrate()` 处理存量数据库的增量列变更 |
| `repo/` | 每张表一个模块，各自暴露 `upsert_*()` 函数 |
| `repo/leagues.py` | 联赛字典表写入 |
| `repo/teams.py` | 球队字典表写入 |
| `repo/matches.py` | 赛事主表写入 |
| `repo/standings.py` | 联赛排名详情写入 |
| `repo/recent_matches.py` | 近六场比赛记录写入 |
| `repo/h2h_matches.py` | 两队交手记录写入 |
| `repo/odds.py` | 欧赔快照（威廉希尔/立博）写入 |
| `repo/odds_history.py` | 欧赔变盘历史写入 |
| `repo/asian_odds.py` | Bet365 亚盘快照写入 |
| `repo/asian_odds_history.py` | Bet365 亚盘变盘历史写入 |
| `repo/companies.py` | 博彩公司字典写入 |
| `repo/league_table.py` | 赛前联赛积分榜（`league_table_snapshot`）读写；按 total/home/away 三维存储 |
| `repo/history.py` | history.db 读写：`save_match()`、`list_saved_matches(filters)`、`load_snapshot()`、`backfill_h30()`、导出/导入 JSON |

**quant.db 表结构（14 张表）：**

- **维度表**（`INSERT OR IGNORE`）：`leagues`、`teams`、`companies`
- **赛事事实表**：`matches`、`match_standings`（16 行/场：2 边 × 2 周期 × 4 范围）、`match_recent`、`match_h2h`、`league_table_snapshot`（赛前联赛积分榜，仅 isShowIntegral=1 的联赛有数据）
- **赔率事实表**：`odds_wh`、`odds_wh_history`、`odds_coral`、`odds_coral_history`、`asian_odds_365`、`asian_odds_365_history`

**history.db 表结构（2 张表）：**

模块：`src/db/history_connection.py` + `history_schema.py` + `repo/history.py`

- `saved_matches`：反范式化平铺行（供列表展示与过滤），含威廉希尔开盘/H30/当前赔率、Bet365 亚盘等；主键 `schedule_id`（UNIQUE，INSERT OR REPLACE）
- `saved_snapshots`：JSON 快照，以 `saved_match_id` 为主键（ON DELETE CASCADE 级联删除）；`snapshot_json` 存储 `load_all_from_quant()` 返回的完整数据包

---

### scraper/ — 遗留模块

早期版本的抓取脚本，当前数据流已由 `service/` 全面替代，此目录保留仅供参考。

---

## 数据流

```
用户在 titan007 筛选赛事
        ↓ (浏览器 localStorage)
service/browser_filter.py → 获取白名单 ID
        ↓
service/match_list.py     → 抓取赛事列表  → db/repo/matches 等
service/live_score.py     → 抓取实时比分  → db/repo/matches（更新比分/状态）
        ↓ (用户点击某场赛事)
service/match_detail.py   → 抓取赛事详情  → db/repo/standings / recent_matches / h2h_matches / league_table
service/euro_odds.py      → 抓取欧赔快照  → db/repo/odds
service/asian_odds.py     → 抓取亚盘快照  → db/repo/asian_odds
service/euro_odds_history → 抓取欧赔历史  → db/repo/odds_history
service/asian_odds_history→ 抓取亚盘历史  → db/repo/asian_odds_history
        ↓
ui/page/conclusion/       → 从 quant.db 读取并展示分析结论（含联赛积分榜）
        ↓ (用户保存)
db/repo/history.py        → 写入 history.db（saved_matches + saved_snapshots）
        ↓ (历史页点击)
ui/page/conclusion/       → 从 history.db 快照读取并展示
```

---

## 数据来源

| 接口 | URL | 编码 |
|------|-----|------|
| 赛事列表 | `https://bf.titan007.com/VbsXml/bfdata.js` | GBK |
| 赛事详情 | `https://zq.titan007.com/analysis/{mid}sb.htm` | UTF-8 |
| 欧赔快照 | `https://1x2d.titan007.com/{mid}.js` | UTF-8 |
| 欧赔历史 | `https://1x2.titan007.com/OddsHistory.aspx?...` | UTF-8 |
| 亚盘快照 | `https://vip.titan007.com/AsianOdds_n.aspx?id={mid}` | GB2312 |
| 亚盘历史 | `https://vip.titan007.com/changeDetail/handicap.aspx?...` | GB2312 |
