"""
从 Chrome / Edge 浏览器本地存储中读取 titan007 赛事筛选状态。

读取内容:
  - Cookie  win007BfCookie              → 全局配置 (热门/完整、语言、样式等)
  - Cookie  FS007Filter                 → 赛事筛选条件 (联赛ID列表、比赛状态)
  - Cookie  Bet007live_concernId_AllDomain → 置顶比赛ID
  - localStorage  Bet007live_hiddenID   → 筛选比赛ID列表（白名单：选中要看的比赛，其余隐藏）

依赖:
  pip install pywin32 cryptography

用法:
  python -m src.scraper.chrome_filter
  python -m src.scraper.chrome_filter --browser edge
  python -m src.scraper.chrome_filter --profile "Profile 1"
"""

import os
import sys
import json
import shutil
import sqlite3
import tempfile
import base64
import argparse
import glob as _glob


# ---------------------------------------------------------------------------
#  Windows 文件共享读取 (绕过浏览器独占锁)
# ---------------------------------------------------------------------------

def _copy_locked_file(src: str, dst: str):
    """使用 win32file 以共享模式读取被浏览器锁定的文件."""
    import win32file
    import pywintypes

    handle = win32file.CreateFile(
        src,
        win32file.GENERIC_READ,
        win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE | win32file.FILE_SHARE_DELETE,
        None,
        win32file.OPEN_EXISTING,
        win32file.FILE_ATTRIBUTE_NORMAL,
        None,
    )

    try:
        with open(dst, "wb") as f_dst:
            while True:
                hr, chunk = win32file.ReadFile(handle, 1024 * 1024)
                if not chunk:
                    break
                f_dst.write(chunk)
    finally:
        handle.Close()


# ---------------------------------------------------------------------------
#  路径常量
# ---------------------------------------------------------------------------

_BROWSER_PATHS = {
    "chrome": os.path.join(
        os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "User Data"
    ),
    "edge": os.path.join(
        os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Edge", "User Data"
    ),
}


def _detect_browser() -> tuple[str, str]:
    """自动检测可用的浏览器, 返回 (browser_name, user_data_path)."""
    for name, path in _BROWSER_PATHS.items():
        if os.path.isdir(path):
            return name, path
    return "", ""

TARGET_COOKIES = [
    "win007BfCookie",
    "FS007Filter",
    "Bet007live_concernId_AllDomain",
]

LS_KEY = "Bet007live_hiddenID"

# ---------------------------------------------------------------------------
#  Cookie 字段定义
# ---------------------------------------------------------------------------

_BF_COOKIE_FIELDS = [
    ("language",         ["英文(Eng)", "简体中文", "繁体中文"]),
    ("rank",             {0: "隐藏", 1: "显示"}),
    ("explain",          {0: "隐藏", 1: "显示"}),
    ("redcard",          {0: "关", 1: "开"}),
    ("showYellowCard",   {0: "关", 1: "开"}),
    ("detail",           {0: "关", 1: "开"}),
    ("vs",               {0: "关", 1: "开"}),
    ("sound",            {-1: "静音", 0: "默认", 1: "警报", 2: "贝司", 3: "嘟嘟"}),
    ("winLocation",      {-1: "关闭", 0: "正上方", 1: "正下方", 2: "正左方", 3: "正右方",
                          4: "左上角", 5: "右上角", 6: "左下角", 7: "右下角"}),
    ("style",            {0: "默认配色", 1: "浪漫宝蓝", 2: "淡雅浅灰", 4: "梦幻天蓝",
                          5: "雅致蓝白", 6: "典雅灰蓝"}),
    ("oddsSound",        {0: "关", 1: "开"}),
    ("guestSound",       {-1: "静音", 0: "默认", 1: "警报", 2: "贝司", 3: "嘟嘟"}),
    ("showSbOddsDetail", {0: "关", 1: "开"}),
    ("oldOrNew",         {1: "旧版(纯比分)", 2: "新版(二合一)"}),
    ("haveLetGoal",      {0: "隐藏", 1: "显示"}),
    ("haveTotal",        {0: "隐藏", 1: "显示"}),
    ("haveEurope",       {0: "隐藏", 1: "显示"}),
    ("isSimple",         {-1: "自定义筛选", 0: "完整", 1: "热门"}),
    ("cornerPopup",      {0: "关", 1: "开"}),
    ("onlyTopShowWin",   {0: "关", 1: "开"}),
]

_SCLASS_LABELS = {0: "所有比赛", 1: "足彩", 2: "竞足", 3: "单场"}
_STATE_LABELS = {0: "全部", 1: "进行中", 2: "已完场", 3: "未开场", 4: "滚球"}
_KIND_LABELS = {1: "联赛筛选", 2: "国家筛选", 3: "盘口筛选", 4: "条件筛选"}


# ---------------------------------------------------------------------------
#  Chrome Cookie 解密 (Windows DPAPI + AES-256-GCM)
# ---------------------------------------------------------------------------

def _get_chrome_aes_key(user_data_path: str) -> bytes:
    """从 Chrome/Edge Local State 提取 AES 密钥 (DPAPI 解密)."""
    import win32crypt

    local_state_path = os.path.join(user_data_path, "Local State")
    if not os.path.exists(local_state_path):
        raise FileNotFoundError(f"未找到 Local State: {local_state_path}")

    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)

    encrypted_key_b64 = local_state["os_crypt"]["encrypted_key"]
    encrypted_key = base64.b64decode(encrypted_key_b64)

    # 前 5 字节是 "DPAPI" 标识
    if encrypted_key[:5] != b"DPAPI":
        raise ValueError("encrypted_key 格式不正确 (缺少 DPAPI 前缀)")

    key = win32crypt.CryptUnprotectData(encrypted_key[5:], None, None, None, 0)[1]
    return key


def _decrypt_value(encrypted_value: bytes, aes_key: bytes) -> str:
    """解密单个 Cookie 值."""
    if not encrypted_value:
        return ""

    # v10 / v20 = AES-256-GCM 加密
    prefix = encrypted_value[:3]
    if prefix in (b"v10", b"v20"):
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        nonce = encrypted_value[3:15]       # 12 bytes
        ciphertext_tag = encrypted_value[15:]  # 密文 + 16 bytes GCM tag
        try:
            return AESGCM(aes_key).decrypt(nonce, ciphertext_tag, None).decode("utf-8")
        except Exception:
            return "[AES 解密失败 — Chrome 版本可能不兼容]"

    # 旧版: 直接 DPAPI
    try:
        import win32crypt
        return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode("utf-8")
    except Exception:
        return "[DPAPI 解密失败]"


# ---------------------------------------------------------------------------
#  读取 Cookie
# ---------------------------------------------------------------------------

def _is_chrome_running() -> bool:
    """检测 Chrome 是否正在运行 (Windows tasklist)."""
    try:
        import subprocess
        out = subprocess.run(
            'tasklist /FI "IMAGENAME eq chrome.exe" /NH /FO CSV',
            shell=True, capture_output=True, text=True, timeout=5,
        ).stdout
        return "chrome.exe" in out.lower()
    except Exception:
        return False


def read_cookies(user_data_path: str, profile: str = "Default") -> dict[str, str]:
    """读取浏览器中 titan007.com 相关的目标 Cookie.

    Chrome 运行时: 走 Playwright 路径（让 Chrome 自己解密 v20 cookies）
    Chrome 未运行时: 直接读 SQLite（数据已完整刷盘，v10 DPAPI 可解密）
    """
    profile_dir = os.path.join(user_data_path, profile)

    cookies_db = os.path.join(profile_dir, "Network", "Cookies")
    if not os.path.exists(cookies_db):
        cookies_db = os.path.join(profile_dir, "Cookies")
    if not os.path.exists(cookies_db):
        raise FileNotFoundError(
            f"未找到 Cookies 数据库\n"
            f"  尝试路径: {profile_dir}/Network/Cookies\n"
            f"  尝试路径: {profile_dir}/Cookies"
        )

    # Chrome 运行中 → 磁盘数据可能是旧的，且 v20 加密无法在外部解密
    # 必须走 Playwright 让 Chrome 自己处理
    if _is_chrome_running():
        return _read_cookies_via_playwright(user_data_path, profile)

    # Chrome 未运行 → SQLite 已完整刷盘，v10 cookies 可用 DPAPI 解密
    tmp = None
    try:
        tmp = tempfile.mktemp(suffix=".db")
        shutil.copy2(cookies_db, tmp)
        conn = sqlite3.connect(tmp)
        aes_key = _get_chrome_aes_key(user_data_path)
        cur = conn.cursor()
        result: dict[str, str] = {}
        for name in TARGET_COOKIES:
            cur.execute(
                "SELECT value, encrypted_value FROM cookies WHERE name = ?",
                (name,),
            )
            row = cur.fetchone()
            if row:
                plain, encrypted = row
                result[name] = plain if plain else _decrypt_value(encrypted, aes_key)
        conn.close()
        return result
    except Exception:
        return {}
    finally:
        if tmp and os.path.exists(tmp):
            try:
                os.unlink(tmp)
            except OSError:
                pass


def _read_cookies_via_playwright(user_data_path: str = "", profile: str = "Default") -> dict[str, str]:
    """Chrome 运行时读取 Cookie。

    Chrome 127+ 使用 App-Bound Encryption (v20)，外部脚本无法直接解密。
    解决方案：将用户的 Cookies + Local State 复制到临时目录，用真正的
    Chrome (channel="chrome") 加载，Chrome 自身调用 ChromeElevationService
    解密 v20 cookies，再通过 context.cookies() 拿到明文值。
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError(
            "Cookies 文件被浏览器锁定, 需要 Playwright 回退读取\n"
            "  pip install playwright && playwright install chromium"
        )

    profile_dir = os.path.join(user_data_path, profile) if user_data_path else ""
    tmp_dir = None

    try:
        # ── 构建最小化临时 Profile ──────────────────────────────────────
        tmp_dir = tempfile.mkdtemp(prefix="quant_chrome_")
        tmp_default = os.path.join(tmp_dir, "Default")
        os.makedirs(tmp_default, exist_ok=True)

        # Local State 和 Cookies 均使用 win32file 共享读取，避免 Chrome 独占锁导致 WinError 32
        local_state_src = os.path.join(user_data_path, "Local State")
        if os.path.exists(local_state_src):
            try:
                _copy_locked_file(local_state_src, os.path.join(tmp_dir, "Local State"))
            except Exception:
                pass  # 无法复制则跳过，Chrome 仍可能读到部分 cookies

        if profile_dir:
            cookies_src = os.path.join(profile_dir, "Network", "Cookies")
            if not os.path.exists(cookies_src):
                cookies_src = os.path.join(profile_dir, "Cookies")
            if os.path.exists(cookies_src):
                net_dir = os.path.join(tmp_default, "Network")
                os.makedirs(net_dir, exist_ok=True)
                try:
                    _copy_locked_file(cookies_src, os.path.join(net_dir, "Cookies"))
                except Exception:
                    pass  # 无法复制则跳过

        # ── 用 Chrome 打开临时 Profile，让 Chrome 自己解密 v20 Cookies ──
        query_urls = [
            "https://live.titan007.com",
            "https://titan007.com",
            "https://bf.titan007.com",
        ]

        with sync_playwright() as p:
            try:
                context = p.chromium.launch_persistent_context(
                    tmp_dir,
                    channel="chrome",          # 必须用 Chrome 本体解密 v20
                    headless=True,
                    args=[
                        "--no-first-run",
                        "--disable-sync",
                        "--disable-extensions",
                        "--disable-background-networking",
                        "--disable-component-update",
                        "--no-sandbox",
                    ],
                )
            except Exception:
                # Chrome 未安装则回退 Chromium（仅能解密 v10）
                context = p.chromium.launch_persistent_context(
                    tmp_dir,
                    headless=True,
                    args=["--no-first-run", "--disable-sync", "--no-sandbox"],
                )

            cookies_list = context.cookies(query_urls)
            context.close()

        return {c["name"]: c["value"] for c in cookies_list if c["name"] in TARGET_COOKIES}

    finally:
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
#  读取 localStorage (扫描 LevelDB 原始文件)
# ---------------------------------------------------------------------------

def _de_cookie_schedule(ids: str) -> str:
    """将 base36 编码的比赛 ID 还原为十进制 (与 JS deCookieSchedule 等价)."""
    parts = ids.split("_")
    decoded = []
    for p in parts:
        if not p:
            continue
        try:
            int(p)          # 已经是十进制
            return ids      # 无需解码
        except ValueError:
            pass
        try:
            decoded.append(str(int(p, 36)))
        except ValueError:
            decoded.append(p)
    return "_" + "_".join(decoded) + "_" if decoded else "_"


def read_localstorage(user_data_path: str, profile: str = "Default") -> dict | None:
    """从浏览器 localStorage LevelDB 中读取 Bet007live_hiddenID.

    Returns:
        解析后的 dict: {"value": "_id1_id2_...", "expiry": int} 或 None
    """
    ls_dir = os.path.join(user_data_path, profile, "Local Storage", "leveldb")
    if not os.path.exists(ls_dir):
        return None

    # 在 LevelDB 的 .ldb 和 .log 文件中搜索目标 key
    target = LS_KEY.encode("utf-8")
    json_pattern = b'{"value":'

    for filepath in sorted(
        _glob.glob(os.path.join(ls_dir, "*.ldb"))
        + _glob.glob(os.path.join(ls_dir, "*.log")),
        key=os.path.getmtime,
        reverse=True,  # 最新文件优先
    ):
        try:
            with open(filepath, "rb") as f:
                data = f.read()
        except (PermissionError, OSError):
            continue

        # LevelDB .log 文件是追加写：同一 key 可能出现多次，最后一次才是最新值。
        # 扫描文件内所有出现位置，保留最后一个成功解析的 JSON。
        last_obj = None
        idx = data.find(target)
        while idx != -1:
            search_start = idx + len(target)
            search_end = min(search_start + 500, len(data))
            json_idx = data.find(json_pattern, search_start, search_end)

            if json_idx != -1:
                depth = 0
                end = json_idx
                for j in range(json_idx, min(json_idx + 5000, len(data))):
                    ch = data[j:j + 1]
                    if ch == b"{":
                        depth += 1
                    elif ch == b"}":
                        depth -= 1
                        if depth == 0:
                            end = j + 1
                            break

                raw = data[json_idx:end]
                try:
                    obj = json.loads(raw.decode("utf-8", errors="ignore"))
                    if "value" in obj and obj["value"] != "_":
                        obj["value_decoded"] = _de_cookie_schedule(obj["value"])
                    last_obj = obj          # 继续扫描，找更新的值
                except json.JSONDecodeError:
                    pass

            idx = data.find(target, idx + 1)

        if last_obj is not None:
            return last_obj                 # 返回该文件内最新的一条

    return None


# ---------------------------------------------------------------------------
#  解析 & 格式化输出
# ---------------------------------------------------------------------------

def parse_bf_cookie(raw: str) -> dict:
    """解析 win007BfCookie."""
    parts = raw.split("^")
    if len(parts) != 20:
        return {"_raw": raw, "_error": f"字段数不匹配 (期望 20, 实际 {len(parts)})"}

    result = {}
    for i, (name, mapping) in enumerate(_BF_COOKIE_FIELDS):
        val = int(parts[i]) if parts[i].lstrip("-").isdigit() else parts[i]
        if isinstance(mapping, list):
            label = mapping[val] if 0 <= val < len(mapping) else str(val)
        elif isinstance(mapping, dict):
            label = mapping.get(val, str(val))
        else:
            label = str(val)
        result[name] = {"value": val, "label": label}
    return result


def parse_fs_filter(raw: str) -> dict:
    """解析 FS007Filter."""
    parts = raw.split("^")
    if len(parts) < 3:
        return {"_raw": raw, "_error": "字段数不足"}

    kind = int(parts[0]) if parts[0].isdigit() else 0
    odds_type = int(parts[1]) if parts[1].lstrip("-").isdigit() else 0
    id_list_raw = parts[2] if len(parts) > 2 else ""
    sclass_type = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0

    # 提取联赛 ID
    league_ids = [x for x in id_list_raw.split("_") if x]

    return {
        "kind": {"value": kind, "label": _KIND_LABELS.get(kind, str(kind))},
        "match_state": {"value": odds_type, "label": _STATE_LABELS.get(odds_type, str(odds_type))},
        "sclass_type": {"value": sclass_type, "label": _SCLASS_LABELS.get(sclass_type, str(sclass_type))},
        "league_ids": league_ids,
        "league_count": len(league_ids),
        "_raw": raw,
    }


def parse_hidden_ids(ls_data: dict) -> list[str]:
    """从 localStorage 数据中提取筛选的比赛 ID 列表（白名单，只显示这些比赛）."""
    value = ls_data.get("value_decoded") or ls_data.get("value", "_")
    return [x for x in value.split("_") if x]


def parse_concern_ids(raw: str) -> list[str]:
    """解析置顶比赛 ID."""
    if not raw or raw == "_":
        return []
    return [x for x in raw.split("_") if x]


# ---------------------------------------------------------------------------
#  获取可用的 Chrome Profile 列表
# ---------------------------------------------------------------------------

def list_profiles(user_data_path: str) -> list[str]:
    """列出 User Data 下的所有 Profile 目录."""
    if not os.path.exists(user_data_path):
        return []
    profiles = []
    for name in os.listdir(user_data_path):
        full = os.path.join(user_data_path, name)
        if not os.path.isdir(full):
            continue
        # Default 或 Profile N
        if name == "Default" or name.startswith("Profile "):
            # 读取 profile 显示名
            prefs = os.path.join(full, "Preferences")
            display_name = name
            if os.path.exists(prefs):
                try:
                    with open(prefs, "r", encoding="utf-8") as f:
                        p = json.load(f)
                    display_name = p.get("profile", {}).get("name", name)
                except Exception:
                    pass
            profiles.append((name, display_name))
    return profiles


# ---------------------------------------------------------------------------
#  主函数
# ---------------------------------------------------------------------------

def read_filter(user_data_path: str, profile: str = "Default") -> dict:
    """读取并返回完整的筛选状态.

    Returns:
        {
            'config': dict,         # win007BfCookie 解析结果
            'filter': dict,         # FS007Filter 解析结果
            'hidden_ids': list,     # 隐藏比赛 ID
            'concern_ids': list,    # 置顶比赛 ID
            'raw_cookies': dict,    # 原始 Cookie 值
            'raw_localstorage': dict | None,
        }
    """
    try:
        cookies = read_cookies(user_data_path, profile)
    except Exception as e:
        print(f"  [警告] Cookie 读取失败: {e}")
        cookies = {}
    ls_data = read_localstorage(user_data_path, profile)

    bf_raw = cookies.get("win007BfCookie", "")
    config = parse_bf_cookie(bf_raw) if bf_raw and bf_raw != "null" else None
    fs_raw = cookies.get("FS007Filter", "")
    fs_filter = parse_fs_filter(fs_raw) if fs_raw and fs_raw != "null" else None
    concern_ids = parse_concern_ids(cookies.get("Bet007live_concernId_AllDomain", ""))
    hidden_ids = parse_hidden_ids(ls_data) if ls_data else []

    return {
        "config": config,
        "filter": fs_filter,
        "hidden_ids": hidden_ids,
        "concern_ids": concern_ids,
        "raw_cookies": cookies,
        "raw_localstorage": ls_data,
    }


def print_result(result: dict, browser_label: str = "Browser"):
    """格式化打印筛选结果."""
    SEP = "-" * 55

    # 1) 全局配置
    print(f"\n{'=' * 55}")
    print(f"  {browser_label} - titan007 赛事筛选状态")
    print(f"{'=' * 55}")

    config = result["config"]
    if config and "_error" not in config:
        print(f"\n[全局配置] win007BfCookie")
        print(SEP)
        # 只打印关键字段
        key_fields = [
            ("isSimple",       "显示模式"),
            ("language",       "语言"),
            ("style",          "样式"),
            ("rank",           "排名"),
            ("showYellowCard", "黄牌"),
            ("explain",        "信息"),
            ("sound",          "主队声音"),
            ("guestSound",     "客队声音"),
            ("cornerPopup",    "角球弹窗"),
        ]
        for field, label in key_fields:
            if field in config:
                v = config[field]
                print(f"  {label:<10s}: {v['label']}")
    elif config:
        print(f"\n[全局配置] 解析失败: {config.get('_error')}")
        print(f"  原始值: {config.get('_raw')}")
    else:
        print("\n[全局配置] 未找到 win007BfCookie")

    # 2) 筛选条件
    fs = result["filter"]
    if fs and "_error" not in fs:
        print(f"\n[筛选条件] FS007Filter")
        print(SEP)
        print(f"  筛选方式  : {fs['kind']['label']}")
        print(f"  赛事类型  : {fs['sclass_type']['label']}")
        print(f"  比赛状态  : {fs['match_state']['label']}")
        print(f"  选中联赛数: {fs['league_count']}")
        if fs["league_ids"]:
            ids_preview = ", ".join(fs["league_ids"][:20])
            if len(fs["league_ids"]) > 20:
                ids_preview += f" ... (共 {len(fs['league_ids'])} 个)"
            print(f"  联赛 ID   : {ids_preview}")
    elif fs:
        print(f"\n[筛选条件] 解析失败: {fs.get('_error')}")
    else:
        print("\n[筛选条件] 未找到 FS007Filter (可能已过期重置)")

    # 3) 筛选比赛（白名单：只显示这些，其余隐藏）
    hidden = result["hidden_ids"]
    print(f"\n[筛选比赛] localStorage Bet007live_hiddenID")
    print(SEP)
    if hidden:
        preview = ", ".join(hidden[:20])
        if len(hidden) > 20:
            preview += f" ... (共 {len(hidden)} 场)"
        print(f"  筛选的比赛ID ({len(hidden)} 场): {preview}")
        if result["raw_localstorage"] and "expiry" in result["raw_localstorage"]:
            from datetime import datetime
            exp = datetime.fromtimestamp(result["raw_localstorage"]["expiry"] / 1000)
            print(f"  过期时间: {exp.strftime('%Y-%m-%d %H:%M')}")
    else:
        print("  无数据 (未做筛选 或 已过期)")

    # 4) 置顶比赛
    concern = result["concern_ids"]
    print(f"\n[置顶比赛] Cookie Bet007live_concernId_AllDomain")
    print(SEP)
    if concern:
        print(f"  置顶比赛ID ({len(concern)} 场): {', '.join(concern)}")
    else:
        print("  无置顶比赛")

    print()


# ---------------------------------------------------------------------------
#  诊断：查看目标 Cookie 实际存储的域名
# ---------------------------------------------------------------------------

def _diagnose_cookies(user_data_path: str, profile: str = "Default"):
    """不过滤域名，列出所有匹配目标 Cookie 名的记录及其 host_key."""
    profile_dir = os.path.join(user_data_path, profile)
    cookies_db = os.path.join(profile_dir, "Network", "Cookies")
    if not os.path.exists(cookies_db):
        cookies_db = os.path.join(profile_dir, "Cookies")
    if not os.path.exists(cookies_db):
        print("错误: 未找到 Cookies 数据库")
        return

    tmp = tempfile.mktemp(suffix=".db")
    try:
        _copy_locked_file(cookies_db, tmp)
        conn = sqlite3.connect(tmp)
    except Exception as e:
        print(f"复制 Cookies 文件失败: {e}")
        return

    aes_key = _get_chrome_aes_key(user_data_path)
    cur = conn.cursor()

    print(f"\n{'=' * 60}")
    print(f"  诊断模式 — 目标 Cookie 实际存储位置")
    print(f"{'=' * 60}")

    for name in TARGET_COOKIES:
        cur.execute(
            "SELECT host_key, value, encrypted_value, expires_utc "
            "FROM cookies WHERE name = ?",
            (name,),
        )
        rows = cur.fetchall()
        print(f"\n  Cookie: {name}")
        if not rows:
            print(f"    [未找到] — Chrome 中不存在此 Cookie")
        else:
            for host_key, plain, encrypted, expires_utc in rows:
                decrypted = plain or _decrypt_value(encrypted, aes_key)
                preview = decrypted[:60] + "..." if len(decrypted) > 60 else decrypted
                print(f"    host_key : {host_key}")
                print(f"    value    : {preview}")
                print(f"    expires  : {expires_utc}")

    conn.close()
    try:
        os.unlink(tmp)
    except OSError:
        pass


# ---------------------------------------------------------------------------
#  CLI 入口
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="读取 Chrome/Edge 中 titan007 赛事筛选状态")
    parser.add_argument(
        "--browser", default=None, choices=["chrome", "edge"],
        help="浏览器类型 (默认自动检测)",
    )
    parser.add_argument(
        "--profile", default=None,
        help="Profile 目录名 (默认自动选择). 例如: Default, 'Profile 1'",
    )
    parser.add_argument(
        "--list-profiles", action="store_true",
        help="列出可用的 Profile",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="以 JSON 格式输出",
    )
    parser.add_argument(
        "--diagnose", action="store_true",
        help="诊断模式：不过滤域名，列出所有匹配目标名称的 Cookie 及其 host_key",
    )
    args = parser.parse_args()

    # 确定浏览器和数据路径
    if args.browser:
        browser_name = args.browser
        user_data_path = _BROWSER_PATHS[browser_name]
    else:
        browser_name, user_data_path = _detect_browser()
        if not browser_name:
            print("错误: 未检测到 Chrome 或 Edge 浏览器")
            for name, path in _BROWSER_PATHS.items():
                print(f"  {name}: {path}")
            sys.exit(1)

    browser_label = {"chrome": "Chrome", "edge": "Edge"}.get(browser_name, browser_name)

    if args.list_profiles:
        profiles = list_profiles(user_data_path)
        if not profiles:
            print(f"未找到 {browser_label} 用户数据目录")
        else:
            print(f"{browser_label} 可用的 Profile:")
            for dirname, display in profiles:
                print(f"  {dirname:<15s}  ({display})")
        return

    # 自动选择 profile
    profile = args.profile
    if profile is None:
        profiles = list_profiles(user_data_path)
        if not profiles:
            print(f"错误: 未找到 {browser_label} 用户数据目录")
            print(f"  路径: {user_data_path}")
            sys.exit(1)
        profile = profiles[0][0]
        if len(profiles) > 1:
            print(f"[{browser_label}] 检测到多个 Profile, 使用: {profile}")
            print(f"  (可通过 --profile 指定, --list-profiles 查看所有)")

    print(f"[{browser_label}] 读取 Profile: {profile}")

    if args.diagnose:
        _diagnose_cookies(user_data_path, profile)
        return

    try:
        result = read_filter(user_data_path, profile)
    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except ImportError as e:
        print(f"缺少依赖: {e}")
        print("请安装: pip install pywin32 cryptography")
        sys.exit(1)
    except Exception as e:
        print(f"读取失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_result(result, browser_label)


if __name__ == "__main__":
    # Windows 终端 GBK 兼容
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=sys.stdout.encoding, errors="replace")
    main()
