import requests

# url = "https://1x2.titan007.com/oddslist/2915135.htm"
url = "https://1x2.titan007.com/OddsHistory.aspx?id=148976408&sid=2915135&cid=115&l=0"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

response = requests.get(url, headers=headers)
response.encoding = "utf-8"  # 防止乱码

# 保存到文件
with open("../../.temp/oddsHistory.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("状态码:", response.status_code)