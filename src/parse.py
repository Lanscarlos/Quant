import requests
from bs4 import BeautifulSoup
import pandas as pd

# ── 1. 获取页面 ───────────────────────────────────────────────────
# 实际使用时取消注释下面这段，注释掉"本地读取"部分：
url = "https://zq.titan007.com/analysis/2911120sb.htm"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
response = requests.get(url, headers=headers)
response.encoding = "utf-8"
html = response.text

# 本地读取（测试用）
# with open("view-source_https___zq_titan007_com_analysis_2911120sb.html", "r", encoding="utf-8") as f:
#     html = f.read()

soup = BeautifulSoup(html, "lxml")

# ── 2. 定位"联赛积分排名"区域 ────────────────────────────────────
porlet = soup.find("div", id="porlet_5")
all_tables = porlet.find_all("table")

# 结构说明：
# table[2] bgcolor=#CECECE  → 主队（华奇巴托）全场
# table[3] bgcolor=#B0D2E3  → 客队（卡拉波波）全场
# table[4] bgcolor=#CECECE  → 主队（华奇巴托）半场
# table[5] bgcolor=#B0D2E3  → 客队（卡拉波波）半场
target_tables = {
    "主队-全场": all_tables[2],
    "客队-全场": all_tables[3],
    "主队-半场": all_tables[4],
    "客队-半场": all_tables[5],
}

col_headers = ["类型", "赛", "胜", "平", "负", "得", "失", "净", "积分", "排名", "胜率"]
all_data = []

for label, table in target_tables.items():
    rows = table.find_all("tr")
    team_name = ""

    for row in rows:
        cells = row.find_all("td")

        # 队伍名称行（colspan=11）
        if len(cells) == 1 and cells[0].get("colspan") == "11":
            team_name = cells[0].get_text(strip=True)
            continue

        # 跳过表头行（第一列文字是"全场"或"半场"）
        if cells and cells[0].get_text(strip=True) in ["全场", "半场"]:
            continue

        # 数据行（11列）
        if len(cells) == 11:
            row_data = [c.get_text(strip=True) for c in cells]
            all_data.append([label, team_name] + row_data)

# ── 3. 整理 DataFrame ─────────────────────────────────────────────
df = pd.DataFrame(all_data, columns=["分类", "队伍"] + col_headers)
print(df.to_string(index=False))

# ── 4. 保存 ──────────────────────────────────────────────────────
df.to_csv("ranking.csv", index=False, encoding="utf-8-sig")
print("\n✅ 已保存到 ranking.csv")