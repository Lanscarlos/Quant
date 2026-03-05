import re
import requests
import pandas as pd

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

GAME_COLS = [
    "公司ID", "记录ID", "公司名",
    "主胜(即)", "平(即)", "客胜(即)",
    "主%", "平%", "客%", "返还率(即)",
    "主胜(初)", "平(初)", "客胜(初)",
    "主初%", "平初%", "客初%", "返还率(初)",
    "凯利主(即)", "凯利平(即)", "凯利客(即)",
    "时间", "来源", "f1", "f2",
    "凯利主(初)", "凯利平(初)", "凯利客(初)",
]

DETAIL_COLS = ["主胜", "平", "客胜", "时间", "凯利主", "凯利平", "凯利客", "年份"]


def fetch_odds(match_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    请求赛事 JS 数据文件，返回 (game_df, detail_df)。
    game_df   — 各公司当前即时/初始赔率
    detail_df — 各公司历史赔率变化明细
    """
    url = f"https://1x2d.titan007.com/{match_id}.js"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.encoding = "utf-8"
    raw = resp.text

    game_df = _parse_game(raw)
    detail_df = _parse_detail(raw)
    return game_df, detail_df


def _parse_game(raw: str) -> pd.DataFrame:
    m = re.search(r'var game=Array\("(.+?)"\);', raw, re.DOTALL)
    if not m:
        return pd.DataFrame()

    records = m.group(1).split('","')
    rows = [r.split("|") for r in records]

    n_cols = len(GAME_COLS)
    rows = [r[:n_cols] + [""] * max(0, n_cols - len(r)) for r in rows]
    return pd.DataFrame(rows, columns=GAME_COLS)


def _parse_detail(raw: str) -> pd.DataFrame:
    m = re.search(r'var gameDetail=Array\("(.+?)"\);', raw, re.DOTALL)
    if not m:
        return pd.DataFrame()

    entries = m.group(1).split('","')
    rows = []
    for entry in entries:
        company_id, _, rest = entry.partition("^")
        for change in rest.split(";"):
            if not change.strip():
                continue
            fields = change.split("|")
            if len(fields) >= len(DETAIL_COLS):
                rows.append([company_id] + fields[:len(DETAIL_COLS)])

    cols = ["公司ID"] + DETAIL_COLS
    return pd.DataFrame(rows, columns=cols)


if __name__ == "__main__":
    match_id = "2915135"
    game_df, detail_df = fetch_odds(match_id)

    print("=== 即时/初始赔率 ===")
    print(game_df[["公司名", "主胜(即)", "平(即)", "客胜(即)", "返还率(即)",
                    "主胜(初)", "平(初)", "客胜(初)", "返还率(初)"]].to_string(index=False))

    print(f"\n=== 历史变化（共 {len(detail_df)} 条）前10条 ===")
    print(detail_df.head(10).to_string(index=False))