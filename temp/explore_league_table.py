"""
探索脚本：分析 titan007 赛事详情页的联赛积分榜 HTML 结构。

用法：
    python temp/explore_league_table.py [match_id]

默认使用脚本内硬编码的 match_id。
"""
import sys
import os
import re
import requests
from bs4 import BeautifulSoup

# 若未传入 match_id，使用最近一条真实赛事 ID
DEFAULT_MID = 2968635

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://zq.titan007.com/",
}

TEMP_DIR = os.path.dirname(os.path.abspath(__file__))


def fetch_html(mid: int) -> str:
    url = f"https://zq.titan007.com/analysis/{mid}sb.htm"
    print(f"[抓取] {url}")
    resp = requests.get(url, headers=_HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.content.decode("utf-8", errors="replace")


def save_html(html: str, mid: int) -> str:
    path = os.path.join(TEMP_DIR, f"match_detail_{mid}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[保存] HTML 已写入 → {path}")
    return path


def analyze_structure(html: str):
    """列出页面所有带 id 的 div 及其内部 table 数量。"""
    soup = BeautifulSoup(html, "html.parser")

    print("\n─── 所有带 id 的 div 及 table 数量 ───")
    for div in soup.find_all("div", id=True):
        tables = div.find_all("table", recursive=True)
        text_preview = div.get_text(separator=" ", strip=True)[:60]
        print(f"  #{div['id']:20s}  tables={len(tables):2d}  preview: {text_preview!r}")

    return soup


def find_league_table_candidates(soup):
    """尝试在各 div 中找包含'积分/球队/排名'关键词的表格，输出详情。"""
    keywords = {"积分", "球队", "排名", "胜", "平", "负"}

    print("\n─── 候选积分榜 div ───")
    found = []
    for div in soup.find_all("div", id=True):
        text = div.get_text()
        if len(keywords & set(text)) >= 2:
            tables = div.find_all("table")
            print(f"\n[候选] #{div['id']}  (tables={len(tables)})")
            found.append((div["id"], div))
            for ti, tbl in enumerate(tables):
                rows = tbl.find_all("tr")
                print(f"  Table[{ti}]  rows={len(rows)}")
                for ri, row in enumerate(rows[:6]):
                    cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                    print(f"    row[{ri}]: {cells}")
                if len(rows) > 6:
                    print(f"    ... 共 {len(rows)} 行")

    return found


def dump_all_tables(soup, output_path: str):
    """将所有 div[id] 下的表格完整内容写入文件，便于离线分析。"""
    lines = []
    for div in soup.find_all("div", id=True):
        tables = div.find_all("table")
        if not tables:
            continue
        lines.append(f"\n{'='*60}")
        lines.append(f"DIV #{div['id']}")
        for ti, tbl in enumerate(tables):
            rows = tbl.find_all("tr")
            lines.append(f"  --- Table[{ti}]  ({len(rows)} rows) ---")
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                lines.append(f"  {cells}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n[分析] 完整表格结构已写入 → {output_path}")


if __name__ == "__main__":
    mid = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MID
    html = fetch_html(mid)
    save_html(html, mid)

    soup = analyze_structure(html)
    find_league_table_candidates(soup)

    dump_path = os.path.join(TEMP_DIR, f"tables_{mid}.txt")
    dump_all_tables(soup, dump_path)

    print("\n完成。请查看上方输出，并用文本编辑器打开 tables_*.txt 深入分析。")
