# build.py
# 构建 EXE 可执行程序

import os, subprocess
import shutil
from pathlib import Path
import nicegui, webview

print("开始打包，请稍候...\n")

# 运行 PyInstaller

if os.path.exists('build'):
    shutil.rmtree('build')
    print("已清理 build 临时文件夹")

if os.path.exists(f'{EXE_NAME}.spec'):
    os.remove(f'{EXE_NAME}.spec')
    print("已清理 spec 配置文件")

print(f"打包完成！请在 dist 文件夹中查看 {EXE_NAME}.exe")

cmd = [
'PyInstaller', 'app.py',
'--name', 'MyApp',
'--onefile', '--windowed', '--clean',
'--add-data', f'{Path(nicegui.__file__).parent}{os.pathsep}nicegui',
'--add-data', f'{Path(webview.__file__).parent}{os.pathsep}webview'
]
subprocess.call(cmd)