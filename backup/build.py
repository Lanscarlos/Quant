# build.py - 打包脚本
import PyInstaller.__main__
import shutil
from pathlib import Path


def build():
    # 清理旧的打包文件
    if Path("dist").exists():
        shutil.rmtree("dist")
    if Path("build").exists():
        shutil.rmtree("build")

    PyInstaller.__main__.run([
        'launcher.py',  # 入口文件
        '--name=Pythia',  # 程序名称
        '--onefile',  # 打包成单个文件
        '--windowed',  # 无控制台窗口（Windows）
        '--icon=assets/icon.ico',  # 图标（需要准备一个）
        '--add-data=hello.py;.',  # 包含 hello.py
        # '--add-data=pages;pages',  # 包含 pages 目录
        # '--add-data=core;core',  # 包含 core 目录
        # '--add-data=config;config',  # 包含 config 目录
        '--add-data=assets;assets',  # 包含资源文件
        '--hidden-import=streamlit',  # 确保包含 Streamlit
        '--hidden-import=pandas',
        '--hidden-import=plotly',
        '--hidden-import=httpx',
        '--collect-all=streamlit',  # 包含 Streamlit 所有资源
        '--clean',  # 清理临时文件
    ])

    print("✅ 打包完成！可执行文件在 dist/Pythia.exe")


if __name__ == "__main__":
    build()