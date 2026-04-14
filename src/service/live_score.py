"""
实时比分抓取 — live.titan007.com/jsData/{prefix}/{sid}.js

数据格式：JS 文件包含 sOdds8（主）或 sOdds（备）数组，
每条记录：[阶段, 主队得分, 客队得分, ...赔率字段]
末条即为当前（或终场）比分与阶段。

阶段 → status 映射：
  '未开场' / '早餐' → 0（未开赛）
  数字字符串（分钟）→ 1（进行中）
  '中场'           → 3（中场）
  '终场'           → -1（完赛）
"""
import ast
import re

import requests

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://zq.titan007.com/",
}

_PHASE_TO_STATUS: dict[str, int] = {
    "未开场": 0,
    "早餐":   0,
    "中场":   3,
    "终场":  -1,
}


def _build_url(match_id: int | str) -> str:
    sid = str(match_id)
    return f"https://live.titan007.com/jsData/{sid[:2]}/{sid[2:4]}/{sid}.js"


def _parse_odds_array(text: str) -> list | None:
    """从 JS 文本中解析 sOdds8 或 sOdds 数组，返回列表；两者均无数据则返回 None。"""
    for varname in ("sOdds8", "sOdds"):
        m = re.search(rf"var\s+{varname}\s*=\s*(\[.*?\])\s*;", text, re.DOTALL)
        if not m:
            continue
        raw = m.group(1)
        # 连续逗号之间的空字段补 None，使 ast.literal_eval 可解析
        fixed = re.sub(r",(?=,|\])", ",None", raw)
        try:
            arr = ast.literal_eval(fixed)
        except (ValueError, SyntaxError):
            continue
        if arr:
            return arr
    return None


def fetch_live_score(match_id: int | str, match_time: str | None = None) -> dict | None:
    """抓取并解析赛事实时比分与状态。

    Args:
        match_id:   赛事 ID。
        match_time: 可选，赛事开球时间字符串（如 '2026-04-08 03:00'）。
                    当 live 端点未返回 '终场' 标记时，用此字段判断赛事是否已完赛：
                    若当前时间超过开球时间 110 分钟，则视为完赛（status=-1）。
    Returns:
        {'home_score': int, 'away_score': int, 'status': int}
        或 None（网络错误 / 无数据）。
    """
    try:
        resp = requests.get(
            _build_url(match_id), headers=_HEADERS, timeout=10
        )
        resp.raise_for_status()
        # 文件使用 GBK 编码，先尝试 GBK，失败则 UTF-8
        try:
            text = resp.content.decode("gbk")
        except UnicodeDecodeError:
            text = resp.content.decode("utf-8", errors="replace")
        # 去掉 BOM
        text = text.lstrip("\ufeff")
    except Exception:
        return None

    arr = _parse_odds_array(text)
    if not arr:
        return None

    last = arr[-1]
    if len(last) < 3:
        return None

    phase      = str(last[0]) if last[0] is not None else ""
    home_score = int(last[1]) if last[1] is not None else 0
    away_score = int(last[2]) if last[2] is not None else 0

    if phase in _PHASE_TO_STATUS:
        status = _PHASE_TO_STATUS[phase]
    elif phase.lstrip("-").isdigit():
        # 数字字符串（分钟数）表示进行中，但若 match_time 已过 110 分钟则视为完赛
        status = _infer_status_from_time(match_time)
    else:
        status = 0

    return {
        "home_score": home_score,
        "away_score": away_score,
        "status":     status,
    }


def _infer_status_from_time(match_time: str | None) -> int:
    """根据开球时间推断赛事是否已完赛。

    超过开球时间 110 分钟（全场 90 + 加时 + 半场休息）视为完赛返回 -1，
    否则视为进行中返回 1。match_time 为 None 时返回 1。
    """
    if not match_time:
        return 1
    from datetime import datetime, timedelta
    try:
        mt = datetime.strptime(match_time, "%Y-%m-%d %H:%M")
        if datetime.now() - mt > timedelta(minutes=110):
            return -1
    except ValueError:
        pass
    return 1
