from nicegui import ui

def render():
    ui.label('📋 TODO 待办事项').classes('text-2xl font-bold')
    ui.separator()
    ui.checkbox(value=False, text="增加历史数据页面")
    ui.checkbox(value=False, text="赛事详情页增加顶部功能按钮区域")
    ui.checkbox(value=False, text="赛事详情页增加亚盘数据渲染逻辑")
    ui.checkbox(value=False, text="优化抓取数据效率")