# build.py

import PyInstaller.__main__

# 定义你的主脚本文件名
SOURCE_FILE = 'main.py'

# 定义生成的 exe 名字（可选，不写默认和脚本同名）
EXE_NAME = 'Quant'

# 定义图标路径（如果有的话，没有就留空或注释掉）
ICON_PATH = 'assets/icon.ico'

# 组装打包参数列表
params = [
    SOURCE_FILE,  # 你的主程序文件
    '-F',  # 打包成一个单独的 exe 文件
    '-w',  # 这里的 -w 意思是不要黑框 (Windowed)
    '--clean',  # 每次打包前清理缓存
    f'-n={EXE_NAME}',  # 命名你的 exe 文件

    # 如果你有图标，取消下面这行的注释
    f'-i={ICON_PATH}',
]

def build():
    print("开始打包，请稍候...\n")

    # 运行 PyInstaller
    PyInstaller.__main__.run(params)

    print(f"打包完成！请在 dist 文件夹中查看 {EXE_NAME}.exe")

if __name__ == "__main__":
    build()