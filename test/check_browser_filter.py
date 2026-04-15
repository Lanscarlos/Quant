"""
browser_filter 诊断脚本

从项目根目录直接运行：
    python test/check_browser_filter.py

依次打印每个诊断步骤的结果，方便定位 get_filtered_match_ids() 读不到数据的原因。
"""
import os
import sys
import glob
import json

# 强制 stdout 使用 UTF-8，避免 Windows GBK 终端在打印二进制片段时崩溃
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 将项目根目录加入 sys.path，使 src.service.browser_filter 可正常 import
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# 导入内部函数（带下划线前缀），用于分步诊断
from src.service.browser_filter import (
    _BROWSER_PATHS,
    _LS_KEY,
    _LS_KEY_PREFIX,
    _detect_user_data_path,
    _first_profile,
    _decode_ids,
    get_filtered_match_ids,
)

SEP = "-" * 60


def step(title: str) -> None:
    print(f"\n{SEP}\n[步骤] {title}\n{SEP}")


# ── 步骤 1：LOCALAPPDATA 环境变量 ────────────────────────────────────────
step("1. 检查 LOCALAPPDATA 环境变量")
local_app_data = os.environ.get("LOCALAPPDATA", "")
print(f"  LOCALAPPDATA = {local_app_data!r}")
if not local_app_data:
    print("  !! 环境变量未设置，后续路径均无法拼接")

# ── 步骤 2：各浏览器 User Data 路径是否存在 ──────────────────────────────
step("2. 检查各浏览器 User Data 路径")
for browser, path in _BROWSER_PATHS.items():
    exists = os.path.isdir(path)
    print(f"  [{browser}] {path}")
    print(f"        存在: {'是' if exists else '否'}")

# ── 步骤 3：自动检测到的 User Data 路径 ─────────────────────────────────
step("3. _detect_user_data_path() 结果")
user_data_path = _detect_user_data_path()
print(f"  检测到: {user_data_path!r}")
if not user_data_path:
    print("  !! 未检测到任何浏览器 User Data，脚本终止")
    sys.exit(1)

# ── 步骤 4：Profile 检测 ─────────────────────────────────────────────────
step("4. _first_profile() 结果")
profile = _first_profile(user_data_path)
print(f"  使用 Profile: {profile!r}")

# 列出所有 Profile 目录（供参考）
try:
    all_entries = os.listdir(user_data_path)
    profiles = [e for e in all_entries
                if e == "Default" or (e.startswith("Profile ") and
                   os.path.isdir(os.path.join(user_data_path, e)))]
    print(f"  可用 Profile 列表: {profiles}")
except Exception as e:
    print(f"  !! 无法列举 Profile 目录: {e}")

# ── 步骤 5：LevelDB 目录 ─────────────────────────────────────────────────
step("5. Local Storage / leveldb 目录")
ls_dir = os.path.join(user_data_path, profile, "Local Storage", "leveldb")
print(f"  路径: {ls_dir}")
print(f"  存在: {'是' if os.path.isdir(ls_dir) else '否'}")
if not os.path.isdir(ls_dir):
    print("  !! 目录不存在，无法继续扫描")
    sys.exit(1)

# ── 步骤 6：列出 .ldb / .log 文件 ────────────────────────────────────────
step("6. LevelDB 文件列表（按修改时间倒序）")
files = sorted(
    glob.glob(os.path.join(ls_dir, "*.ldb")) +
    glob.glob(os.path.join(ls_dir, "*.log")),
    key=os.path.getmtime,
    reverse=True,
)
if not files:
    print("  !! 未找到任何 .ldb / .log 文件")
else:
    for f in files:
        size = os.path.getsize(f)
        print(f"  {os.path.basename(f):30s}  {size:>10,} bytes")

# ── 步骤 6.5：SST 解压后 block 预览 ──────────────────────────────────────
step("6.5. SSTable 解压后 block 预览（验证 Snappy 解压是否正常）")
from src.service.browser_filter import (
    _iter_sst_data_blocks as _sst_blocks,
    _iter_log_records as _log_records,
)
for filepath in files[:3]:
    fname = os.path.basename(filepath)
    ext = os.path.splitext(filepath)[1].lower()
    try:
        fdata = open(filepath, "rb").read()
        blocks = list(_sst_blocks(fdata) if ext == ".ldb" else _log_records(fdata))
        for i, block in enumerate(blocks):
            if _LS_KEY_PREFIX in block:
                idx = block.find(_LS_KEY_PREFIX)
                snippet = block[idx:idx+200].decode("utf-8", errors="replace").replace("\n", " ")
                print(f"  {fname} block[{i}] 包含 Bet007（解压后明文）:")
                print(f"    {snippet[:120]!r}")
                break
        else:
            print(f"  {fname}: 解压后未见 Bet007")
    except Exception as ex:
        print(f"  {fname}: 解压/解析失败 → {ex}")

# ── 步骤 7：逐文件搜索键，用 regex 提取 value 字段 ────────────────────────
step(f"7. 在各文件中搜索键 {_LS_KEY.decode()!r}（Bet007 前缀 + regex 提取）")
key_found_in: list[str] = []
raw_values: list[tuple[str, str]] = []  # (文件名, 清理后的 value 字符串)

for filepath in files:
    fname = os.path.basename(filepath)
    try:
        with open(filepath, "rb") as f:
            data = f.read()
    except (PermissionError, OSError) as e:
        print(f"  {fname}: 读取失败 → {e}")
        continue

    idx = data.find(_LS_KEY)
    while idx != -1:
        # 确认 Bet007 前缀
        prefix_start = max(0, idx - 30)
        if _LS_KEY_PREFIX not in data[prefix_start:idx]:
            idx = data.find(_LS_KEY, idx + 1)
            continue

        if fname not in key_found_in:
            key_found_in.append(fname)
        print(f"  {fname}: 找到键 (offset={idx})")

        # regex 提取 "value":"..." 内容
        window = data[idx + len(_LS_KEY): idx + len(_LS_KEY) + 1000]
        import re as _re
        m = _re.search(rb'"value"\s*:\s*"([^"]*)"', window, _re.DOTALL)
        if m:
            raw_val = m.group(1)
            print(f"       -> 原始字节: {raw_val!r}")
            # 控制字节当分隔符，去掉非法字符
            val = _re.sub(rb'[\x00-\x1f]', b'_', raw_val)
            val = _re.sub(rb'[^0-9a-zA-Z_]', b'', val)
            val = _re.sub(rb'_+', b'_', val)
            val_str = val.decode('ascii', errors='ignore').strip('_')
            print(f"       -> 清理后: {val_str!r}")
            if val_str:
                raw_values.append((fname, val_str))
        else:
            print(f"       -> 未找到 \"value\" 字段")
        idx = data.find(_LS_KEY, idx + 1)

if not key_found_in:
    print(f"  !! 所有文件中均未发现键 {_LS_KEY.decode()!r}")
    print("  可能原因：")
    print("    1. 从未在 titan007 中做过筛选（Bet007live_hiddenID 键尚未写入）")
    print("    2. Chrome 正在运行且文件被锁定（关闭 Chrome 后重试）")
    print("    3. 使用的是非 Default Profile（如 Profile 1）")

    # 额外：扫描文件中与 titan007 / bet007 相关的可读字符串，帮助确认实际写入的键名
    print("\n  [额外] 扫描文件中包含 'titan007' / 'bet007' 的可读片段：")
    keywords = [b"titan007", b"Titan007", b"bet007", b"Bet007", b"hiddenID", b"HiddenID"]
    found_any = False
    for filepath in files:
        fname = os.path.basename(filepath)
        try:
            with open(filepath, "rb") as f:
                data = f.read()
        except (PermissionError, OSError):
            continue
        for kw in keywords:
            idx = data.find(kw)
            while idx != -1:
                snippet_start = max(0, idx - 60)
                snippet_end = min(len(data), idx + 80)
                raw = data[snippet_start:snippet_end]
                text = raw.decode("utf-8", errors="replace").replace("\n", " ").replace("\r", " ")
                print(f"    {fname} offset={idx}: ...{text}...")
                found_any = True
                idx = data.find(kw, idx + 1)
    if not found_any:
        print("    未找到任何相关字符串 —— 确认 titan007 从未在此 Profile 中写过数据")

# ── 步骤 7.5：对找到 'Bet007' 的位置做十六进制精确 dump ──────────────────
step("7.5. Bet007 附近字节的十六进制 dump（用于确认实际 key 名称）")
for filepath in files:
    fname = os.path.basename(filepath)
    try:
        with open(filepath, "rb") as f:
            data = f.read()
    except (PermissionError, OSError):
        continue
    idx = data.find(b"Bet007")
    while idx != -1:
        # 取 Bet007 开始往后 64 字节做 hex dump
        chunk = data[idx: idx + 64]
        hex_str = " ".join(f"{b:02x}" for b in chunk)
        txt_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"  {fname} offset={idx}:")
        # 每 16 字节一行
        for i in range(0, len(chunk), 16):
            h = " ".join(f"{b:02x}" for b in chunk[i:i+16])
            t = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk[i:i+16])
            print(f"    {idx+i:6d}  {h:<48}  {t}")
        idx = data.find(b"Bet007", idx + 1)

# ── 步骤 8：解码 ID ───────────────────────────────────────────────────────
step("8. _decode_ids() 结果")
if raw_values:
    fname, raw = raw_values[0]
    print(f"  使用来源文件: {fname}")
    print(f"  原始值: {raw!r}")
    decoded = _decode_ids(raw)
    print(f"  解码后共 {len(decoded)} 条 ID: {decoded}")
else:
    print("  无可解码的值（步骤 7 未找到有效 value）")

# ── 步骤 9：调用公开接口 ──────────────────────────────────────────────────
step("9. get_filtered_match_ids() 最终结果")
result = get_filtered_match_ids()
print(f"  返回 {len(result)} 条 ID: {result}")
