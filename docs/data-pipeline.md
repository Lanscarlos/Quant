# 数据抓取流水线

## 概述

Quant 的数据抓取分为两个场景：

1. **赛事列表页**：批量顺序抓取（`hydrate_ids`），覆盖基础信息、欧赔、亚盘、变赔历史
2. **抓取数据页**：单场赛事分阶段并行抓取（8 步骤 4 阶段），带进度追踪和依赖管理

---

## 抓取数据页：8 步骤 4 阶段

### 步骤定义 (`src/ui/page/fetch/steps.py`)

| 阶段 | 步骤类 | KEY | 标签 | 依赖 | 特殊标记 |
|------|--------|-----|------|------|----------|
| 1 | `StepMatchDetail` | `match_detail` | 赛事详情 (排名 + 近期 + 交手) | 无 | |
| 2 | `StepSubOdds` | `sub_odds` | 子比赛赔率 (近六场 + 交手) | `match_detail` | `BACKGROUND=True` |
| 3 | `StepEuroOdds` | `euro_odds` | 欧赔数据 (威廉 / 立博 / 365) | 无 | |
| 3 | `StepAsianOdds` | `asian_odds` | 365 亚盘数据 | 无 | |
| 3 | `StepOverUnder` | `over_under` | 365 大小球数据 | 无 | |
| 4 | `StepEuroHistory` | `euro_history` | 欧赔变盘历史 (威廉 / 立博 / 365) | `euro_odds` | |
| 4 | `StepAsianHistory` | `asian_history` | 365 亚盘变盘历史 | 无 | |
| 4 | `StepOverUnderHistory` | `over_under_history` | 365 大小球变盘历史 | 无 | |

### 执行逻辑

```
阶段 1: StepMatchDetail（单独执行）
    ↓
阶段 2: StepSubOdds（BACKGROUND=True，create_task 后立即继续，不阻塞后续阶段）
    ↓
阶段 3: StepEuroOdds ‖ StepAsianOdds ‖ StepOverUnder（asyncio.gather 并行）
    ↓
阶段 4: StepEuroHistory ‖ StepAsianHistory ‖ StepOverUnderHistory（asyncio.gather 并行）
    ↓
等待所有后台任务完成 → on_complete(mid)
```

### 每个步骤的接口

```python
class StepXxx:
    KEY: str                    # 唯一标识
    LABEL: str                  # UI 显示名称
    ICON: str                   # Material icon 名称
    PHASE: int                  # 执行阶段号
    DEPENDS_ON: list[str]       # 依赖的步骤 KEY 列表
    BACKGROUND: bool = False    # 是否后台执行

    @staticmethod
    def should_skip(mid: int, force: bool = False) -> tuple[bool, str]:
        """新鲜度检查。返回 (是否跳过, 跳过原因)。"""

    @staticmethod
    async def fetch(mid: str, ctx: dict, tracker=None) -> None:
        """异步抓取。ctx 为步骤间共享上下文字典。"""
```

### 步骤间数据传递 (ctx)

`ctx` 是一个在所有步骤间共享的字典：

| key | 写入者 | 读取者 | 说明 |
|-----|--------|--------|------|
| `record_ids` | `StepEuroOdds` | `StepEuroHistory` | `{company_id: record_id}` 映射 |
| `match_time` | `StepMatchDetail` | — | 赛事开球时间字符串 |
| `match_year` | `StepMatchDetail` | `StepEuroHistory`, `StepAsianHistory`, `StepOverUnderHistory` | 赛事年份（int） |

当依赖步骤被跳过（新鲜度检查）时，后续步骤通过辅助函数从 DB 回退加载：
- `_load_record_ids_from_db(mid)` → 从 `odds_wh` / `odds_coral` / `odds_365` 表查 `record_id`
- `_get_match_year(mid)` → 从 `matches.match_time` 提取年份

### 中断机制

用户点击"中断"按钮后，`state['abort'] = True`：
- 当前正在执行的步骤会继续完成
- 后续未开始的步骤标记为 `stopped`
- 不触发 `on_complete` 回调

### 强制抓取

勾选"强制抓取"复选框后，所有步骤的 `should_skip()` 直接返回 `(False, '')`，忽略新鲜度检查。

---

## 进度追踪 (`src/ui/page/fetch/progress.py`)

### SubTask

单条子任务，持有状态和标签：

```python
class SubTask:
    key: str
    label: str
    status: str    # 'pending' | 'running' | 'done' | 'error'
    msg: str

    def start() -> SubTask       # 设为 running
    def done(msg='')             # 设为 done
    def error(msg)               # 设为 error
    def update(msg)              # 更新消息（保持 running）
```

支持上下文管理器用法：

```python
with tracker.task('html', '下载 HTML'):
    html = _fetch(mid)
# 正常退出 → done()，异常 → error()
```

### ProgressTracker

```python
class ProgressTracker:
    def __init__(self, task_list: list, on_update: callable):
        """task_list 由 UI 层提供，on_update 封装 loop.call_soon_threadsafe。"""

    def task(self, key: str, label: str) -> SubTask:
        """注册新子任务，追加到列表并触发 UI 刷新。"""
```

---

## 新鲜度策略 (`src/service/freshness.py`)

### 赛事列表 (`match_ids_needing_refresh`)

| 赛事状态 | 阈值 |
|----------|------|
| 完场 (-1) | 永不重抓 |
| 上半场 (1) / 下半场 (3) | 2 分钟 |
| 未开赛 (0) | 10 分钟 |
| DB 中不存在 | 需抓 |

### 赛事详情 (`should_fetch_detail`)

| 赛事状态 | 条件 |
|----------|------|
| 完场 (-1) | standings 不存在 → 需抓；存在但 `league_table_fetched=0` → 需抓；否则跳过 |
| 其他 | `fetched_at` 超过 6 小时 → 需抓 |
| 任何 | 近期赛事每侧恰好 6 条（旧版本上限）→ 需补抓到 8 条 |

### 欧赔 / 亚盘 / 大小球快照 (`should_fetch_odds` / `should_fetch_asian_odds` / `should_fetch_over_under`)

| 赛事状态 | 阈值 |
|----------|------|
| 完场 (-1) | 有数据就不再抓 |
| 上半场 (1) / 下半场 (3) | 2 分钟 |
| 未开赛 (0) | 10 分钟 |
| 其他 | 30 分钟 |

### 变盘历史 (`should_fetch_history` / `should_fetch_asian_history` / `should_fetch_over_under_history`)

| 赛事状态 | 条件 |
|----------|------|
| 完场 (-1) | 有数据就不再抓 |
| 其他 | 始终需抓（用户主动点击时总是刷新） |

---

## 赛事列表页的批量抓取 (`src/ui/page/match_list/refresh.py`)

### `hydrate_ids(ids, on_progress)`

顺序遍历赛事 ID 列表，每次 HTTP 请求间随机间隔 2-5 秒：

```
对每个 mid:
  1. 基础信息 + 实时比分（若 freshness 判定需抓）
     → fetch_match_basics(mid) + fetch_live_score(mid, match_time)
  2. 主赛事欧赔快照（若 freshness 判定需抓）
     → fetch_euro_odds_with_record_ids(mid)
  3. 威廉希尔欧赔变盘历史（若 freshness 判定需抓）
     → fetch_euro_odds_history(wh_record_id, mid, COMPANY_WH, year)
  4. Bet365 亚盘快照（若 freshness 判定需抓）
     → fetch_asian_odds(mid)
```

四类数据全部新鲜时跳过该赛事，不发请求。

### 差量刷新

赛事列表页刷新时，对比新旧白名单：
- `added`：新增 ID（缓存中没有），需全量抓取
- `kept`：已在缓存中的 ID，交给 `hydrate_ids` 内部 freshness 判断

---

## 子比赛赔率批量抓取 (`src/ui/page/fetch/_sub_odds.py`)

### `fetch_sub_odds(mid, tracker)`

为近六场和交手子比赛批量抓取欧赔快照 + 变赔历史：

1. 从 `match_recent` 和 `match_h2h` 查出所有子比赛 ID
2. 合并去重
3. 使用 `ThreadPoolExecutor(max_workers=4)` 并行处理每个子比赛：
   - 欧赔快照（`fetch_euro_odds`）
   - 欧赔变赔历史（`fetch_euro_odds_history`）
   - 近六场的 `match_time` 补全（赛前半小时赔率计算依赖）
4. 通过 `ProgressTracker` 实时更新进度 `(done/total)`

---

## 浏览器白名单读取 (`src/service/browser_filter.py`)

### 工作原理

titan007 将用户筛选的赛事 ID 存入 Chrome/Edge 的 `localStorage`，key 为 `Bet007live_hiddenID`，值为 Base36 编码的 ID 列表（`_` 分隔）。

### 读取流程

```
1. 检测 Chrome / Edge 的 User Data 路径
2. 定位 Default 或 Profile N 目录
3. 扫描 Local Storage/leveldb/ 下的 .ldb 和 .log 文件（按 mtime 倒序）
4. 对 .ldb（SSTable）：解析 footer → index block → data block，Snappy 解压
5. 对 .log（WAL）：按 32KB 物理块解析 record
6. 在明文 block 中搜索 _hiddenID 锚点，向前 30 字节确认 Bet007 前缀
7. 提取 "value":"..." 内容，Base36 解码为十进制 ID
8. 过滤掉 ID < 100000 的无效值
```

### 公开 API

```python
def get_filtered_match_ids() -> list[str]:
    """返回用户在 titan007 中筛选出来要看的比赛 ID 列表。"""
```
