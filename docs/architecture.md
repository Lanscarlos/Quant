# 项目架构总览

## 目录结构

```
Quant/
├── main.py                          # 应用入口
├── build.py                         # PyInstaller 打包脚本
├── assets/
│   └── icon.ico                     # 应用图标
├── data/
│   ├── quant.db                     # 实时数据库（抓取的赛事/赔率数据）
│   ├── history.db                   # 历史数据库（用户保存的分析快照）
│   └── config.json                  # 应用配置（刷新间隔等）
├── src/
│   ├── ui/                          # UI 层
│   │   ├── index.py                 # 主页面布局、路由注册、页面间跳转编排
│   │   ├── router.py                # 自定义路由器（基于 tab_panels）
│   │   ├── frame/
│   │   │   └── navigation_bar.py    # 左侧导航栏（56px 宽）
│   │   └── page/
│   │       ├── match_list/          # 赛事列表页
│   │       ├── fetch/               # 抓取数据页
│   │       ├── conclusion/          # 结论展示页
│   │       ├── history/             # 历史数据页
│   │       ├── settings/            # 设置页
│   │       └── dashboard.py         # 占位页（未使用）
│   ├── service/                     # 服务层（抓取 + 解析 + 持久化）
│   │   ├── match_detail.py          # 赛事详情页抓取
│   │   ├── euro_odds.py             # 欧赔快照抓取
│   │   ├── euro_odds_history.py     # 欧赔变盘历史抓取
│   │   ├── asian_odds.py            # 亚盘快照抓取
│   │   ├── asian_odds_history.py    # 亚盘变盘历史抓取
│   │   ├── over_under.py            # 大小球快照抓取
│   │   ├── over_under_history.py    # 大小球变盘历史抓取
│   │   ├── live_score.py            # 实时比分抓取
│   │   ├── browser_filter.py        # Chrome LevelDB 白名单读取
│   │   ├── freshness.py             # 新鲜度决策助手
│   │   └── config.py                # 配置文件读写
│   ├── db/                          # 数据库层
│   │   ├── connection.py            # quant.db 连接管理
│   │   ├── history_connection.py    # history.db 连接管理
│   │   ├── schema.py                # quant.db DDL + 迁移
│   │   ├── history_schema.py        # history.db DDL + 迁移
│   │   └── repo/                    # Repository 模块（每张表一个文件）
│   │       ├── matches.py
│   │       ├── teams.py
│   │       ├── standings.py
│   │       ├── recent_matches.py
│   │       ├── h2h_matches.py
│   │       ├── odds.py
│   │       ├── odds_history.py
│   │       ├── asian_odds.py
│   │       ├── asian_odds_history.py
│   │       ├── over_under.py
│   │       ├── over_under_history.py
│   │       ├── league_table.py
│   │       ├── companies.py
│   │       └── history.py           # history.db 的读写操作
│   └── algorithm/                   # 算法数据加载器
│       ├── __init__.py
│       └── loader.py                # load_match() / load_match_from_history()
└── scripts/                         # 辅助脚本（非核心流程）
    ├── discover_datasource.py
    ├── md2docx.py
    └── _md2pdf.py
```

## 入口点

```python
# main.py
from nicegui import ui
import src.ui.index as app
from src.db import init_db, init_history_db

init_db()           # 创建 quant.db 所有表 + 增量迁移
init_history_db()   # 创建 history.db 所有表 + 增量迁移

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        port=19193,
        title="Quant",
        favicon="assets/icon.ico",
        window_size=(1260, 840),
        native=True,
        reload=False,
    )
```

启动顺序：
1. `init_db()` → 打开 `data/quant.db`，执行 `schema.create_all()`（DDL + `_migrate()`）
2. `init_history_db()` → 打开 `data/history.db`，执行 `history_schema.create_all()`
3. `ui.run(native=True)` → NiceGUI 启动 HTTP 服务 + pywebview 桌面窗口

## 路由机制

### Router 类 (`src/ui/router.py`)

自定义路由器，基于 NiceGUI 的 `ui.tab_panels` 实现页面切换：

```python
class Router:
    _routes: dict[str, callable]    # key → render_fn 映射
    _panels: ui.tab_panels          # 底层容器
    _apis: dict[str, any]           # 页面 render() 的返回值
    _listeners: list[callable]      # 导航回调列表
    current: str                    # 当前活跃页面 key
```

核心方法：

| 方法 | 说明 |
|------|------|
| `add(key, render_fn)` | 注册页面，render_fn 在 mount 时执行一次 |
| `mount()` | 创建 tab_panels 容器，预渲染所有页面。若 render_fn 有返回值，存入 `_apis` |
| `navigate(key)` | 切换到指定页面，触发所有 `_listeners` |
| `get_api(key)` | 获取页面 render() 的返回值（如 `trigger(mid)` 回调） |
| `on_navigate(callback)` | 注册导航事件监听器 |

### 页面注册

在 `src/ui/index.py` 中注册 5 个页面：

```python
router.add('match_list',  lambda: match_list_index.render(on_match_click=...))
router.add('fetch',       lambda: fetch_index.render(on_complete=..., on_status_change=...))
router.add('conclusion',  lambda: conclusion_index.render(on_back=..., on_refetch=...))
router.add('history',     lambda: history_index.render(on_match_click=...))
router.add('settings',    lambda: settings_index.render(on_interval_change=...))
```

## 页面间跳转流程

页面间通过回调函数实现跳转，使用 holder 列表（`list[None]`）打破初始化顺序依赖：

```
赛事列表 rowClick
    → navigate('fetch')
    → fetch.trigger(mid)          # 自动开始抓取

fetch on_complete
    → navigate('conclusion')
    → conclusion.trigger(mid)     # 渲染结论数据

历史数据 rowClick
    → navigate('conclusion')
    → conclusion.trigger(mid, source='history')  # 从 history.db 读快照

结论页 返回按钮
    → on_back(source)
    → navigate('match_list') 或 navigate('history')

结论页 重新抓取
    → navigate('fetch')
    → fetch.trigger(mid, force=True)

设置页 保存间隔
    → on_interval_change(seconds)
    → match_list.set_refresh_interval(seconds)
```

### 全局抓取进度浮标

`index.py` 维护一个 `_fetch_global` 状态字典，通过 `@ui.refreshable` 的 `_fetch_badge()` 在右下角显示：
- 抓取进行中：蓝色胶囊 "抓取中 x/y"，点击跳转 fetch 页
- 抓取完成：绿色胶囊 "抓取完成 · 查看结论"，点击跳转结论页
- 用户在 fetch 页时不显示（避免重复）

## 导航栏

`src/ui/frame/navigation_bar.py` 渲染左侧 56px 宽的图标导航栏：

| 位置 | key | 图标 | 标签 |
|------|-----|------|------|
| 上方 | `match_list` | `sports_soccer` | 赛事列表 |
| 上方 | `fetch` | `download` | 抓取数据 |
| 上方 | `conclusion` | `emoji_events` | 结论 |
| 上方 | `history` | `history` | 历史数据 |
| 底部 | `settings` | `settings` | 设置 |

当前活跃页面按钮高亮为蓝色，其余为灰色。

## 异步模型

所有 HTTP 请求通过 `run.io_bound()` 在线程池中执行，不阻塞 NiceGUI 的事件循环。线程内的 UI 更新通过 `loop.call_soon_threadsafe()` 回到主循环。

```python
# 典型模式
async def _on_fetch():
    result = await run.io_bound(some_blocking_function, arg1, arg2)
    # 回到事件循环，安全更新 UI
    data_table.refresh()
```
