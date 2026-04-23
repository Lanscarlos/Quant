# Quant 项目技术文档

## 项目简介

Quant 是一款基于 [NiceGUI](https://nicegui.io/) 的桌面足球赔率分析应用。它从 titan007.com 抓取赛事数据和赔率信息，存储到本地 SQLite 数据库，并在桌面窗口中提供分析 UI。

## 技术栈

| 组件 | 技术 |
|------|------|
| UI 框架 | NiceGUI（native 模式，基于 pywebview） |
| 数据库 | SQLite（WAL 模式，双库架构） |
| HTTP 抓取 | requests |
| HTML 解析 | BeautifulSoup4 |
| 异步模型 | asyncio + `run.io_bound()` 线程池 |
| 打包工具 | PyInstaller（onedir 模式） |

## 文档目录

| 文档 | 说明 |
|------|------|
| [architecture.md](architecture.md) | 项目架构总览：目录结构、入口点、路由机制、页面跳转流程 |
| [database.md](database.md) | 数据库 Schema 详解：quant.db 17 张表 + history.db 2 张表 |
| [data-pipeline.md](data-pipeline.md) | 数据抓取流水线：8 步骤 4 阶段、新鲜度策略、浏览器白名单 |
| [service-layer.md](service-layer.md) | Service 层 API 参考：12 个模块的公开函数签名与说明 |
| [db-repo-layer.md](db-repo-layer.md) | DB Repository 层 API 参考：14 个 repo 模块的公开函数 |
| [ui-pages.md](ui-pages.md) | UI 页面说明：5 个页面的功能、回调、状态管理 |
| [algorithm-api.md](algorithm-api.md) | 算法数据加载器 API：`load_match()` 返回值字段说明 |
| [build-and-config.md](build-and-config.md) | 构建打包与配置管理 |

## 快速启动

```bash
# 运行应用
python main.py

# 打包（创建临时 .build_venv → pip install → PyInstaller → 清理）
python build.py
```

应用启动后会在 `localhost:19193` 打开一个 1260×840 的桌面窗口。
