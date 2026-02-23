# 文件名: hello.py

def get_welcome_message(name):
    if not name:
        return "名字不能为空哦！"

    # 返回一段格式化好的文字
    return f"你好，{name}！这是来自 hello.py 的问候。"