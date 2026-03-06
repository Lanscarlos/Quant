"""
build.py - 创建干净虚拟环境并打包
用法: python build.py
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import src.ui.index as app

# ===== 配置区 =====
ENTRY_FILE   = "main.py"
APP_NAME     = app.NAME
APP_ICON     = app.ICON        # 例如 "assets/icon.ico"，留空不设置
ONE_FILE     = False     # False = 目录模式（启动更快）
DEV_MODE = False
REQUIREMENTS = [         # 项目所需依赖
    "pywebview",
    "pyinstaller",
    "nicegui",
    # "requests",
    # "sqlalchemy",
]
# ==================

VENV_DIR = ".build_venv"
PY = Path(VENV_DIR) / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")

def run(cmd, **kwargs):
    print(f"▶ {' '.join(map(str, cmd))}")
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        sys.exit(result.returncode)

# 1. 创建干净虚拟环境
if Path(VENV_DIR).exists():
    shutil.rmtree(VENV_DIR)
run([sys.executable, "-m", "venv", VENV_DIR])

# 2. 安装依赖（只装项目需要的）
run([PY, "-m", "pip", "install"] + REQUIREMENTS)

# 3. 获取 nicegui 包路径
nicegui_path = subprocess.run(
    [PY, "-c", "import nicegui; print(nicegui.__file__)"],
    capture_output=True, text=True
).stdout.strip()
nicegui_dir = str(Path(nicegui_path).parent)

# 4. 打包 — 直接通过虚拟环境 Python 调用 PyInstaller
shutil.rmtree(f"dist/{APP_NAME}", ignore_errors=True)
cmd = [PY, "-m", "PyInstaller",
       "--onefile" if ONE_FILE else "--onedir",
       "--name", APP_NAME,
       "--icon", APP_ICON,
       "--console" if DEV_MODE else "--windowed",
       "--add-data",f"{nicegui_dir}{os.pathsep}nicegui",
       ENTRY_FILE]
run(cmd)

# 4. 清理
shutil.rmtree(VENV_DIR)
shutil.rmtree("build", ignore_errors=True)
for f in Path(".").glob("*.spec"):
    f.unlink()

print(f"\n✅ 打包完成 -> dist/{APP_NAME}")