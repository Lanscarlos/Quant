# 构建打包与配置管理

## 运行应用

```bash
python main.py
```

应用启动后：
- HTTP 服务监听 `localhost:19193`
- pywebview 打开 1260×840 的桌面窗口
- 标题为 "Quant"，图标为 `assets/icon.ico`

## 打包

```bash
python build.py
```

### 打包流程

1. **创建干净虚拟环境**：删除旧的 `.build_venv`，创建新的 venv
2. **安装依赖**：`pip install pywebview pyinstaller nicegui`
3. **获取 nicegui 包路径**：通过 `import nicegui; print(nicegui.__file__)` 定位
4. **PyInstaller 打包**：
   ```
   PyInstaller --onedir --name Quant --icon assets/icon.ico --windowed
               --add-data {nicegui_dir};nicegui main.py
   ```
5. **清理**：删除 `.build_venv`、`build/`、`*.spec`

### 打包配置

| 常量 | 值 | 说明 |
|------|-----|------|
| `ONE_FILE` | `False` | 目录模式（启动更快） |
| `DEV_MODE` | `False` | `--windowed`（无控制台）；设为 `True` 则 `--console` |
| `ENTRY_FILE` | `main.py` | 入口文件 |
| `APP_NAME` | `Quant` | 输出名称 |
| `APP_ICON` | `assets/icon.ico` | 应用图标 |

### 输出

```
dist/Quant/          # onedir 模式输出目录
dist/Quant/Quant.exe # 可执行文件
```

---

## 配置管理 (`src/service/config.py`)

### 配置文件

路径：`data/config.json`

```json
{
  "refresh_interval": 1200
}
```

### 路径解析

```python
if getattr(sys, 'frozen', False):
    base = Path(sys.executable).parent   # 打包环境：exe 所在目录
else:
    base = Path(__file__).parent.parent.parent  # 开发环境：项目根目录
config_path = base / "data" / "config.json"
```

### 配置项

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `refresh_interval` | `int` | `1200` | 赛事列表自动刷新间隔（秒），即 20 分钟 |

### API

```python
def get_refresh_interval() -> int:
    """返回赛事列表自动刷新间隔（秒）。"""

def set_refresh_interval(seconds: int) -> None:
    """持久化保存赛事列表自动刷新间隔（秒）。"""
```

### 设置页交互

设置页 UI 以分钟为单位展示（1-60 分钟），保存时转换为秒：

```python
minutes = max(1, min(60, int(raw or 5)))
seconds = minutes * 60
set_refresh_interval(seconds)
```

保存后通过 `on_interval_change(seconds)` 回调实时更新赛事列表页的定时器间隔。

---

## 数据目录结构

```
data/
├── quant.db       # 实时数据库（自动创建）
├── history.db     # 历史数据库（自动创建）
└── config.json    # 应用配置（首次保存时创建）
```

所有数据文件在首次使用时自动创建，`data/` 目录不存在时也会自动创建（`mkdir(parents=True, exist_ok=True)`）。
