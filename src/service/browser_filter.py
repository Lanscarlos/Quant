"""
从 Chrome / Edge 本地存储读取用户在 titan007 上的赛事筛选白名单。

titan007 将用户"筛选出来要看的比赛 ID"存入 localStorage key Bet007live_hiddenID，
语义为白名单：只显示这些比赛，其余隐藏。

用法:
    from src.service.browser_filter import get_filtered_match_ids
    ids = get_filtered_match_ids()   # list[str]，如 ['2958472', '2958473', ...]
"""

import os
import re
import json
import glob as _glob

_BROWSER_PATHS = {
    "chrome": os.path.join(
        os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data"
    ),
    "edge": os.path.join(
        os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Edge", "User Data"
    ),
}

# Chrome LevelDB 实际存储时，Bet007 与 _hiddenID 之间会夹入若干记录格式字节，
# 因此不能搜索完整的 "Bet007live_hiddenID"，改为以 "_hiddenID" 为锚点，
# 并向前 30 字节确认存在 "Bet007" 前缀以防误命中。
_LS_KEY        = b"_hiddenID"
_LS_KEY_PREFIX = b"Bet007"


def _detect_user_data_path() -> str:
    for path in _BROWSER_PATHS.values():
        if os.path.isdir(path):
            return path
    return ""


def _first_profile(user_data_path: str) -> str:
    if os.path.isdir(os.path.join(user_data_path, "Default")):
        return "Default"
    for name in sorted(os.listdir(user_data_path)):
        if name.startswith("Profile ") and os.path.isdir(os.path.join(user_data_path, name)):
            return name
    return "Default"


def _decode_ids(value: str) -> list[str]:
    """将 base36 编码的比赛 ID 还原为十进制列表."""
    parts = [p for p in value.split("_") if p]
    if not parts:
        return []
    # 若第一个 part 已是纯数字，整体已是十进制，无需解码
    if parts[0].isdigit():
        return parts
    result = []
    for p in parts:
        try:
            result.append(str(int(p, 36)))
        except ValueError:
            result.append(p)
    return result


def _read_leveldb(ls_dir: str) -> list[str]:
    """扫描 LevelDB 文件，提取 titan007 hiddenID 的最新值.

    Chrome 在 LevelDB 中存储 localStorage 条目时：
    1. Bet007 与 _hiddenID 之间插有若干 SSTable 记录格式字节
    2. JSON 字符串内部也可能夹杂控制字节（Snappy 块格式 overhead）

    因此不做 JSON 解析，改为：
    a) 以 _hiddenID 为锚点 + Bet007 前缀确认
    b) 用 regex 从原始字节直接提取 "value":"..." 中的内容
    c) 将控制字节视为 ID 分隔符，清理后交给 _decode_ids
    """
    last_val: str | None = None

    files = sorted(
        _glob.glob(os.path.join(ls_dir, "*.ldb"))
        + _glob.glob(os.path.join(ls_dir, "*.log")),
        key=os.path.getmtime,
        reverse=True,
    )

    for filepath in files:
        try:
            with open(filepath, "rb") as f:
                data = f.read()
        except (PermissionError, OSError):
            continue

        idx = data.find(_LS_KEY)
        while idx != -1:
            # 向前 30 字节确认有 Bet007 前缀，防止误命中其他键
            prefix_start = max(0, idx - 30)
            if _LS_KEY_PREFIX not in data[prefix_start:idx]:
                idx = data.find(_LS_KEY, idx + 1)
                continue

            # 在 key 后 1000 字节内用 regex 直接提取 "value":"..." 内容
            window = data[idx + len(_LS_KEY): idx + len(_LS_KEY) + 1000]
            m = re.search(rb'"value"\s*:\s*"([^"]*)"', window, re.DOTALL)
            if m:
                raw_val = m.group(1)
                # 将控制字节（SSTable 格式字节、Chrome 内部元数据）替换为 "_" 分隔符
                val = re.sub(rb'[\x00-\x1f]', b'_', raw_val)
                # 去掉非 base36 / 十进制 / 下划线的字符（如 |）
                val = re.sub(rb'[^0-9a-zA-Z_]', b'', val)
                # 合并连续下划线
                val = re.sub(rb'_+', b'_', val)
                val_str = val.decode('ascii', errors='ignore').strip('_')
                if val_str:
                    last_val = val_str

            idx = data.find(_LS_KEY, idx + 1)

        if last_val is not None:
            break  # 最新文件已找到结果，停止扫描

    if last_val is None:
        return []
    return _decode_ids(last_val)


def get_filtered_match_ids() -> list[str]:
    """返回用户在 titan007 中筛选出来要看的比赛 ID 列表（白名单）.

    Returns:
        list[str]: 比赛 ID 字符串列表，如 ['2958472', '2958473']。
                   若读取失败或未设置筛选，返回空列表。
    """
    user_data_path = _detect_user_data_path()
    if not user_data_path:
        return []

    profile = _first_profile(user_data_path)
    ls_dir = os.path.join(user_data_path, profile, "Local Storage", "leveldb")
    if not os.path.isdir(ls_dir):
        return []

    try:
        ids = _read_leveldb(ls_dir)
        # 过滤掉因控制字节误解析出的极小 ID（真实 titan007 赛事 ID > 100000）
        return [mid for mid in ids if mid.isdigit() and int(mid) > 100_000]
    except Exception:
        return []
