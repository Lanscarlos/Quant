# launcher.py

import webview

def launch_client():
    webview.create_window(
        title="ERP ",
        url="http://10.16.0.103/k3cloud/",
        width=1400,
        height=900,
        resizable=True,
        frameless=False,  # 保留标题栏
        easy_drag=False
    )
    webview.start()

def launch_server():
    a = 1