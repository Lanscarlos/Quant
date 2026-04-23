# UI 页面说明

## 页面总览

| 页面 | 路由 key | 模块 | 返回 API |
|------|----------|------|----------|
| 赛事列表 | `match_list` | `src/ui/page/match_list/` | `set_refresh_interval(seconds)` |
| 抓取数据 | `fetch` | `src/ui/page/fetch/` | `trigger(mid, force=False)` |
| 结论展示 | `conclusion` | `src/ui/page/conclusion/` | `trigger(mid, source='live')` |
| 历史数据 | `history` | `src/ui/page/history/` | 无 |
| 设置 | `settings` | `src/ui/page/settings/` | 无 |

---

## 赛事列表页 (`src/ui/page/match_list/`)

### 功能

- 显示用户在 Chrome 浏览器中筛选的赛事列表
- 自动刷新（可配置间隔，默认 20 分钟）
- 右下角倒计时浮标
- 点击行跳转到抓取数据页

### 模块结构

| 文件 | 职责 |
|------|------|
| `index.py` | 页面主逻辑：布局、事件绑定、自动刷新定时器 |
| `columns.py` | 表格列定义（12 列） |
| `queries.py` | DB 查询辅助函数（`query_filtered`） |
| `refresh.py` | 网络抓取辅助（`hydrate_ids`） |

### 状态管理

```python
cached_rows:  list = [[]]       # 表格数据缓存
filter_ids:   list = [[...]]    # Chrome 白名单 ID 列表
is_loading:   list = [False]    # 首次加载 spinner
is_fetching:  list = [False]    # 重入保护锁
progress_state: dict             # 进度状态 {done, total}
interval_seconds: list = [1200]  # 自动刷新间隔
next_refresh_at: list            # 下次刷新的绝对时间点
```

### 刷新流程

1. **手动刷新**（点击"刷新列表"按钮）：
   - 重读 Chrome 白名单
   - 差量对比（`_diff_ids`）：新增 ID 全量抓，老 ID 走 freshness 判断
   - `hydrate_ids` 顺序抓取，进度回调驱动增量渲染

2. **自动刷新**（定时器触发）：
   - 静默执行，不显示 loading 遮罩
   - 同样走差量 + freshness 逻辑

3. **首次加载**（页面挂载时）：
   - 若有需要刷新的 ID，自动触发一次抓取

### 表格列

| 列名 | 字段 | 说明 |
|------|------|------|
| 序号 | `idx` | 行号 |
| 时间 | `match_time` | 开球时间 |
| 主队 | `home_team` | 含 `[排名]` 前缀 |
| 客队 | `away_team` | 含 `[排名]` 前缀 |
| 联赛类型 | `league` | 联赛中文名 |
| 初始赔率 | `open_odds` | 威廉希尔 胜/平/负 |
| 赛前半小时赔率 | `h30_odds` | 威廉希尔变盘历史中赛前 30 分钟的赔率 |
| 最终赔率 | `cur_odds` | 威廉希尔即时 胜/平/负 |
| 最终亚盘 | `asian` | Bet365 主水/盘口/客水 |
| 分析结论 | `analysis` | 预留（当前为空） |
| 赛果输入 | `score` | 比分或 `-` |
| 详细信息 | `id` | 点击图标跳转 |

### 返回 API

```python
def set_refresh_interval(seconds: int) -> None:
    """供设置页调用，动态更新定时器间隔并重置倒计时。"""
```

---

## 抓取数据页 (`src/ui/page/fetch/`)

### 功能

- 输入赛事 URL 或 ID，分阶段并行抓取数据
- 实时显示每个步骤的状态和子任务进度
- 支持中断和强制抓取
- 完成后自动跳转结论页

### 模块结构

| 文件 | 职责 |
|------|------|
| `index.py` | 页面主逻辑：布局、步骤行渲染、事件处理 |
| `steps.py` | 8 个步骤类定义 + 阶段分组 |
| `progress.py` | `ProgressTracker` + `SubTask` 进度追踪 |
| `_sub_odds.py` | 子比赛赔率批量抓取 |

### 步骤状态

| 状态 | 图标 | 颜色 | 说明 |
|------|------|------|------|
| `pending` | `radio_button_unchecked` | 灰色 | 等待中 |
| `running` | `hourglass_top` | 蓝色 | 抓取中 |
| `done` | `check_circle` | 绿色 | 完成 |
| `skipped` | `check_circle` | 浅灰 | 已跳过（数据新鲜） |
| `error` | `cancel` | 红色 | 出错 |
| `stopped` | `do_not_disturb_on` | 橙色 | 已中断 |

### URL 解析

```python
def _parse_mid(raw: str) -> str | None:
    # 支持两种格式：
    # 1. URL: https://zq.titan007.com/analysis/2907948sb.htm → "2907948"
    # 2. 纯数字: "2907948" → "2907948"
```

### 返回 API

```python
def trigger(mid: int | str, force: bool = False) -> None:
    """从外部跳入时调用：填入 URL 并自动开始抓取。"""
```

---

## 结论展示页 (`src/ui/page/conclusion/`)

### 功能

- 展示赛事分析数据：头部信息、近八场、交手记录、欧赔、亚盘、大小球、联赛积分榜
- 支持两种数据源：`live`（从 quant.db 读）和 `history`（从 history.db 快照读）
- 结果保存到历史数据库
- 页内刷新赔率（不跳转 fetch 页）
- 可收起/展开右侧积分榜

### 模块结构

| 文件 | 职责 |
|------|------|
| `index.py` | 页面主逻辑：数据加载、布局编排、赔率刷新 |
| `queries.py` | DB 查询函数（`query_match`, `query_odds`, `query_asian_odds` 等） |
| `renderers.py` | UI 渲染组件（`render_recent_section`, `render_odds_section` 等） |
| `columns.py` | 表格列定义（近期、交手、欧赔、亚盘、大小球） |
| `formatters.py` | 格式化辅助函数（`fmt_float`, `fmt_percent`, `parse_year`） |

### 数据加载

```python
if source == 'history':
    data = load_snapshot(mid)       # 从 history.db
else:
    data = load_all_from_quant(mid) # 从 quant.db
```

两者返回相同结构：`{match, extras, recent, h2h, odds, asian_odds, over_under, league_table}`

### 页面布局

```
操作按钮栏（数据分析初始 / 结果保存 / 重新抓取 / 刷新赔率 / 返回 / 收起积分榜）
─────────────────────────────────────────────────────────────────
│ 左侧主区                                    │ 右侧积分榜    │
│ ┌─ 赛事头部（联赛 / 主队 VS 客队 / 比分）─┐ │ ┌─ 总/主/客 ─┐│
│ ├─ 主队近八场 │ 客队近八场                 ─┤ │ │ 排名列表   ││
│ ├─ 近八场交手 │ 365亚盘 │ 365大小球        ─┤ │ └───────────┘│
│ ├─ 威廉希尔   │ 立博    │ 365欧赔          ─┤ │              │
│ └─ 分析过程   │ 结论                       ─┘ │              │
─────────────────────────────────────────────────────────────────
```

### 赔率刷新机制

点击"刷新赔率"按钮后，在结论页内直接抓取欧赔+亚盘四个步骤：
1. Phase 3 并行：`StepEuroOdds.fetch` + `StepAsianOdds.fetch`
2. Phase 4 并行：`StepEuroHistory.fetch` + `StepAsianHistory.fetch`
3. 右下角悬浮指示器显示进度（loading → done → idle）

### 返回 API

```python
def trigger(mid: int | str, source: str = 'live') -> None:
    """设置 mid 并刷新结论。source='live' 从 quant.db 读，'history' 从 history.db 读。"""
```

---

## 历史数据页 (`src/ui/page/history/`)

### 功能

- 展示用户保存的赛事分析记录列表
- 四种筛选对话框：时间、联赛、球队、赔率
- 快捷按钮：近十场分析数据
- 数据导入/导出（JSON 完整迁移 + CSV 查看用）
- 底部两个平赔面板（威廉体系 / 立博体系）

### 模块结构

| 文件 | 职责 |
|------|------|
| `index.py` | 页面主逻辑：布局、筛选状态管理、事件绑定 |
| `constants.py` | 表格列定义 + 面板联赛列表 + 赔率选项映射 |
| `dialogs.py` | 筛选对话框构建器（时间/联赛/球队/赔率/导出/导入） |
| `odds_panel.py` | 平赔面板组件 |

### 筛选对话框

| 对话框 | 构建函数 | 说明 |
|--------|----------|------|
| 按时间检索 | `build_time_dialog` | 开始/结束日期，带日历选择器 |
| 按联赛检索 | `build_league_dialog` | 多选按钮，数据来自 `list_distinct_leagues()` |
| 按球队检索 | `build_team_dialog` | 多选按钮 + 搜索框 + 主/客/全部角色切换 |
| 按赔率检索 | `build_odds_dialog` | 赔率类型下拉 + 最小/最大值 |
| 导出数据 | `build_export_dialog` | 范围（筛选/全部）+ 格式（CSV/JSON）+ 保存路径 |
| 导入数据 | `build_import_dialog` | 文件选择 + 预览 + 覆盖选项 |

### 初始化

页面加载时自动执行：
1. `backfill_h30()` — 补全旧记录的赛前半小时赔率
2. `backfill_recent_h2h()` — 补全旧快照的近期/交手数据
3. `_reload()` — 加载列表数据

---

## 设置页 (`src/ui/page/settings/`)

### 功能

- 配置赛事列表自动刷新间隔（1-60 分钟，默认 5 分钟）
- 保存后通过 `on_interval_change` 回调实时更新赛事列表页的定时器

### 布局

```
┌─ 设置 ──────────────────────────────┐
│ ┌─ 赛事列表 ──────────────────────┐ │
│ │ 自动刷新间隔                     │ │
│ │ [  5  ] 分钟  [保存]  已保存     │ │
│ │ 范围 1 ~ 60 分钟，默认 5 分钟    │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```
