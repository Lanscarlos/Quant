"""
build.py - 创建干净虚拟环境并打包
用法: python build.py
"""

import sys
import shutil
import subprocess
from pathlib import Path

# ===== 配置区 =====
ENTRY_FILE   = "main.py"
APP_NAME     = "MyApp"
APP_ICON     = ""        # 例如 "assets/icon.ico"，留空不设置
ONE_FILE     = False     # False = 目录模式（启动更快）
REQUIREMENTS = [         # 项目所需依赖
    "nicegui",
    # "nicegui-pack",
    # "requests",
    # "sqlalchemy",
]
# ==================

VENV_DIR = ".build_venv"
PY   = Path(VENV_DIR) / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
PACK = Path(VENV_DIR) / ("Scripts/nicegui-pack.exe" if sys.platform == "win32" else "bin/nicegui-pack")

def run(cmd):
    print(f"▶ {' '.join(map(str, cmd))}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)

# 1. 创建干净虚拟环境
if Path(VENV_DIR).exists():
    shutil.rmtree(VENV_DIR)
run([sys.executable, "-m", "venv", VENV_DIR])

# 2. 安装依赖（只装项目需要的）
run([PY, "-m", "pip", "install"] + REQUIREMENTS)

# 3. 打包
cmd = [PACK, "--onefile" if ONE_FILE else "--onedir", "--name", APP_NAME]
if APP_ICON:
    cmd += ["--icon", APP_ICON]
cmd.append(ENTRY_FILE)
run(cmd)

# 4. 清理
shutil.rmtree(VENV_DIR)
shutil.rmtree("build", ignore_errors=True)
for f in Path(".").glob("*.spec"):
    f.unlink()

print(f"\n✅ 打包完成 -> dist/{APP_NAME}")