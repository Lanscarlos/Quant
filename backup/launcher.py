# launcher.py
import subprocess
import sys
import os
import time
import threading
from pathlib import Path
import socket

try:
    import webview
except ImportError:
    print("正在安装依赖...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pywebview"])
    import webview


class PythiaLauncher:
    def __init__(self):
        self.port = 8501
        self.streamlit_process = None

    def find_free_port(self):
        """找到可用端口"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    def start_streamlit(self):
        """后台启动 Streamlit"""
        # 获取 hello.py 的绝对路径
        app_path = Path(__file__).parent / "hello.py"

        self.streamlit_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(app_path),
                f"--server.port={self.port}",
                "--server.headless=true",
                "--browser.gatherUsageStats=false",
                "--server.fileWatcherType=none"  # 禁用文件监控，减少资源占用
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )

        # 等待 Streamlit 启动
        print("正在启动 Pythia...")
        time.sleep(3)

    def create_window(self):
        """创建桌面窗口"""
        webview.create_window(
            title="⚽ Pythia - 足球数据分析系统",
            url=f"http://localhost:{self.port}",
            width=1400,
            height=900,
            resizable=True,
            frameless=False,  # 保留标题栏
            easy_drag=False
        )

    def cleanup(self):
        """清理进程"""
        if self.streamlit_process:
            self.streamlit_process.terminate()
            self.streamlit_process.wait()
            print("Pythia 已关闭")

    def run(self):
        """运行应用"""
        try:
            self.start_streamlit()
            self.create_window()
            webview.start()
        finally:
            self.cleanup()


if __name__ == "__main__":
    launcher = PythiaLauncher()
    launcher.run()