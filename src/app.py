from nicegui import ui
from src import hello

PORT = 19193
NAME = "Quant"
ICON = "assets/icon.ico"
SIZE = (1080, 720)

# 你的页面代码
@ui.page('/')
def index():# 文件名: app.py

    def on_click():
        # 获取输入框的名字
        name = name_input.value

        # 2. 调用 hello.py 里的函数处理逻辑
        result = hello.get_welcome_message(name)

        # 3. 更新界面上的标签文字
        result_label.text = result

        # 顺便弹个窗（可选）
        ui.notify(f"处理完成：{result}")

    # --- 界面布局 ---
    ui.markdown('## NiceGUI 模块化示例')

    # 一个输入框
    name_input = ui.input(label='请输入你的名字', placeholder='例如：张三')

    # 一个按钮，点击时触发 on_click 函数
    ui.button('点击打招呼', on_click=on_click)

    # 一个用来显示结果的标签
    result_label = ui.label('这里将显示结果...').classes('text-lg text-blue-500')