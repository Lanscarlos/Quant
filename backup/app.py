import streamlit as st
import pandas as pd

# 一行代码就能创建完整的数据看板
st.set_page_config(page_title="⚽ Pythia - 足球数据分析", layout="wide")

st.title("⚽ Pythia 足球数据分析平台")

# 侧边栏 - 筛选条件
with st.sidebar:
    st.header("🔍 筛选条件")
    league = st.selectbox("联赛", ["英超", "西甲", "德甲", "意甲", "法甲"])
    date_range = st.date_input("日期范围", [])
    min_odds = st.slider("最低赔率", 1.0, 10.0, 1.5)

# 主面板 - 多列布局
col1, col2, col3, col4 = st.columns(4)
col1.metric("今日比赛", "12场", "+3")
col2.metric("推荐场次", "5场", "+2")
col3.metric("胜率", "68.5%", "+2.1%")
col4.metric("本月盈利", "+1,250", "+180")

# 数据表格
st.subheader("📋 今日赛事分析")
data = pd.DataFrame({
    "比赛": ["曼城 vs 利物浦", "巴萨 vs 皇马", "拜仁 vs 多特"],
    "联赛": ["英超", "西甲", "德甲"],
    "主胜赔率": [2.10, 1.85, 1.65],
    "平局赔率": [3.40, 3.60, 3.90],
    "客胜赔率": [3.20, 4.00, 5.20],
    "推荐": ["✅ 主胜", "⚠️ 观望", "✅ 主胜"],
    "置信度": [0.82, 0.51, 0.76]
})
st.dataframe(data, use_container_width=True)

# 图表
st.subheader("📈 赔率走势")
st.line_chart({"主胜": [2.1, 2.05, 2.0, 1.95], "客胜": [3.2, 3.3, 3.35, 3.4]})