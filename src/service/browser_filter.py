"""
从 Chrome / Edge 本地存储读取用户在 titan007 上的赛事筛选白名单。

titan007 将用户"筛选出来要看的比赛 ID"存入 localStorage key Bet007live_hiddenID，
语义为白名单：只显示这些比赛，其余隐藏。

用法:
    from src.service.browser_filter import get_filtered_match_ids
    ids = get_filtered_match_ids()   # list[str]，如 ['2958472', '2958473', ...]
"""

import os
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

_LS_KEY = b"Bet007live_hiddenID"


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
    """扫描 LevelDB 文件，提取 Bet007live_hiddenID 的最新值."""
    json_pattern = b'{"value":'
    last_obj = None

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
            search_start = idx + len(_LS_KEY)
            search_end = min(search_start + 500, len(data))
            json_idx = data.find(json_pattern, search_start, search_end)

            if json_idx != -1:
                depth, end = 0, json_idx
                for j in range(json_idx, min(json_idx + 5000, len(data))):
                    ch = data[j:j + 1]
                    if ch == b"{":
                        depth += 1
                    elif ch == b"}":
                        depth -= 1
                        if depth == 0:
                            end = j + 1
                            break
                try:
                    obj = json.loads(data[json_idx:end].decode("utf-8", errors="ignore"))
                    if "value" in obj and obj["value"] not in ("_", ""):
                        last_obj = obj
                except json.JSONDecodeError:
                    pass

            idx = data.find(_LS_KEY, idx + 1)

        if last_obj is not None:
            break  # 最新文件已找到结果，停止扫描

    if last_obj is None:
        return []
    return _decode_ids(last_obj.get("value", "_"))


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
        return _read_leveldb(ls_dir)
    except Exception:
        return []
