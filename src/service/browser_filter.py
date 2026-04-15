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
import struct
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

# LevelDB SSTable 魔数（文件末尾 8 字节）
_SST_MAGIC    = b"\x57\xfb\x80\x8b\x24\x75\x47\xdb"
_SST_FOOTER   = 48           # footer 固定大小
_BLOCK_SNAPPY = 1            # block 压缩类型：Snappy

# LevelDB .log 物理块大小（32 KB）
_LOG_BLOCK_SIZE  = 32768
_LOG_HEADER_SIZE = 7         # checksum(4) + length(2) + type(1)


# ──────────────────────────────────────────────
#  内部工具
# ──────────────────────────────────────────────

def _read_varint(buf: bytes, pos: int) -> tuple[int, int]:
    """读取无符号 varint，返回 (value, new_pos)."""
    result = shift = 0
    while pos < len(buf):
        b = buf[pos]; pos += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            return result, pos
        shift += 7
    raise ValueError("varint 读取超出缓冲区")


def _snappy_decompress(data: bytes) -> bytes:
    """Snappy raw format 解压（无 stream framing，LevelDB block 级别使用此格式）."""
    pos = 0
    # 前导 varint 是解压后长度，此处仅用于跳过，不做长度校验
    _, pos = _read_varint(data, pos)
    output = bytearray()

    while pos < len(data):
        tag = data[pos]; pos += 1
        tag_type = tag & 0x03

        if tag_type == 0x00:  # literal
            lc = tag >> 2
            if lc < 60:
                length = lc + 1
            elif lc == 60:
                length = data[pos] + 1; pos += 1
            elif lc == 61:
                length = struct.unpack_from("<H", data, pos)[0] + 1; pos += 2
            elif lc == 62:
                length = int.from_bytes(data[pos:pos+3], "little") + 1; pos += 3
            else:
                length = struct.unpack_from("<I", data, pos)[0] + 1; pos += 4
            output.extend(data[pos:pos+length])
            pos += length

        elif tag_type == 0x01:  # copy-1（1 字节偏移）
            length = ((tag >> 2) & 7) + 4
            offset = ((tag >> 5) << 8) | data[pos]; pos += 1
            _copy_snappy(output, offset, length)

        elif tag_type == 0x02:  # copy-2（2 字节偏移）
            length = (tag >> 2) + 1
            offset = struct.unpack_from("<H", data, pos)[0]; pos += 2
            _copy_snappy(output, offset, length)

        else:  # copy-4（4 字节偏移）
            length = (tag >> 2) + 1
            offset = struct.unpack_from("<I", data, pos)[0]; pos += 4
            _copy_snappy(output, offset, length)

    return bytes(output)


def _copy_snappy(output: bytearray, offset: int, length: int) -> None:
    """Snappy 回溯复制：从 output 末尾向前 offset 字节起复制 length 字节（允许重叠）."""
    if offset <= 0 or offset > len(output):
        return
    start = len(output) - offset
    for i in range(length):
        output.append(output[start + i])


def _parse_block_handle(buf: bytes, pos: int) -> tuple[int, int, int]:
    """解析 LevelDB BlockHandle（offset varint + size varint），返回 (offset, size, new_pos)."""
    b_off, pos = _read_varint(buf, pos)
    b_sz, pos = _read_varint(buf, pos)
    return b_off, b_sz, pos


def _read_block(fdata: bytes, offset: int, size: int) -> tuple[bytes, int]:
    """读取 SSTable block：返回 (raw_content, compression_type)."""
    content = fdata[offset:offset + size]
    ctype   = fdata[offset + size]
    return content, ctype


def _decompress_block(content: bytes, ctype: int) -> bytes:
    """按压缩类型解压 block 内容."""
    if ctype == _BLOCK_SNAPPY:
        return _snappy_decompress(content)
    return content  # type 0 = 无压缩，原样返回


def _iter_sst_data_blocks(fdata: bytes):
    """迭代 SSTable 文件中所有 data block 的明文字节（generator）.

    解析流程：
      footer → index block handle → 解压 index block → 枚举 data block handles
      → 解压每个 data block → yield 明文。
    """
    if len(fdata) < _SST_FOOTER:
        return
    footer = fdata[-_SST_FOOTER:]
    if footer[-8:] != _SST_MAGIC:
        return

    # 解析 footer：metaindex_handle（跳过）+ index_handle
    _, pos        = _read_varint(footer, 0)
    _, pos        = _read_varint(footer, pos)
    ix_off, ix_sz, pos = _parse_block_handle(footer, pos)

    # 读取并解压 index block
    ix_raw, ix_type = _read_block(fdata, ix_off, ix_sz)
    ix_data         = _decompress_block(ix_raw, ix_type)

    # index block 末尾：num_restarts × 4 bytes + num_restarts(4)
    num_restarts = struct.unpack_from("<I", ix_data, len(ix_data) - 4)[0]
    entries_end  = len(ix_data) - 4 - num_restarts * 4
    if entries_end < 0:
        return

    # 遍历 index block entries，每条 entry 的 value = data block 的 BlockHandle
    p = 0
    while p < entries_end:
        _shared,    p = _read_varint(ix_data, p)
        non_shared, p = _read_varint(ix_data, p)
        val_len,    p = _read_varint(ix_data, p)
        p += non_shared                             # 跳过 key 字节
        db_off, db_sz, _ = _parse_block_handle(ix_data, p)
        p += val_len

        db_raw, db_type = _read_block(fdata, db_off, db_sz)
        db_data         = _decompress_block(db_raw, db_type)
        yield db_data


def _iter_log_records(fdata: bytes):
    """迭代 LevelDB .log WAL 文件，yield 每条完整 record 的字节序列.

    .log 文件按 32 KB 物理块组织，每条记录有 7 字节头部。
    record 类型：1=FULL, 2=FIRST, 3=MIDDLE, 4=LAST。
    """
    pos = 0
    fragment = bytearray()

    while pos + _LOG_HEADER_SIZE <= len(fdata):
        # 跳过块尾填充（length=0 且 type=0）
        block_start = (pos // _LOG_BLOCK_SIZE) * _LOG_BLOCK_SIZE
        block_end   = block_start + _LOG_BLOCK_SIZE

        length = struct.unpack_from("<H", fdata, pos + 4)[0]
        rtype  = fdata[pos + 6]
        pos   += _LOG_HEADER_SIZE

        if length == 0 and rtype == 0:
            pos = block_end
            continue

        payload = fdata[pos:pos + length]
        pos    += length

        if rtype == 1:          # FULL
            yield bytes(payload)
        elif rtype == 2:        # FIRST
            fragment = bytearray(payload)
        elif rtype == 3:        # MIDDLE
            fragment.extend(payload)
        elif rtype == 4:        # LAST
            fragment.extend(payload)
            yield bytes(fragment)
            fragment = bytearray()


# ──────────────────────────────────────────────
#  对外接口保持不变
# ──────────────────────────────────────────────

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


def _scan_blocks(blocks) -> str | None:
    """在一组明文 block 字节中扫描 hiddenID，返回最后命中的 val_str（或 None）."""
    last_val = None
    for block in blocks:
        idx = block.find(_LS_KEY)
        while idx != -1:
            # 向前 30 字节确认有 Bet007 前缀，防止误命中其他键
            prefix_start = max(0, idx - 30)
            if _LS_KEY_PREFIX not in block[prefix_start:idx]:
                idx = block.find(_LS_KEY, idx + 1)
                continue

            # 在 key 后 1000 字节内提取 "value":"..." 内容
            window = block[idx + len(_LS_KEY): idx + len(_LS_KEY) + 1000]
            m = re.search(rb'"value"\s*:\s*"([^"]*)"', window, re.DOTALL)
            if m:
                raw_val = m.group(1)
                # 防御性清洗：解压后控制字节理论上已消失，
                # 但保留以兜底未来可能的格式变化
                val = re.sub(rb"[\x00-\x1f]", b"_", raw_val)
                val = re.sub(rb"[^0-9a-zA-Z_]", b"", val)
                val = re.sub(rb"_+", b"_", val)
                val_str = val.decode("ascii", errors="ignore").strip("_")
                if val_str:
                    last_val = val_str

            idx = block.find(_LS_KEY, idx + 1)
    return last_val


def _read_leveldb(ls_dir: str) -> list[str]:
    """扫描 LevelDB 目录，提取 titan007 hiddenID 的最新值.

    处理策略：
    - .ldb（SSTable）：通过 SST footer → index block → data block 正确解压；
      Snappy block-level 压缩会把重复 ID 前缀替换为回溯引用，
      不解压则只能拿到部分 ID。
    - .log（WAL）：无压缩，直接解析 record 拼装后扫描。
    - 按 mtime 倒序扫描，找到第一个有数据的文件即停止。
    """
    last_val: str | None = None

    files = sorted(
        _glob.glob(os.path.join(ls_dir, "*.ldb"))
        + _glob.glob(os.path.join(ls_dir, "*.log")),
        key=os.path.getmtime,
        reverse=True,
    )

    for filepath in files:
        ext = os.path.splitext(filepath)[1].lower()
        try:
            with open(filepath, "rb") as f:
                fdata = f.read()
        except (PermissionError, OSError):
            continue

        try:
            if ext == ".ldb":
                blocks = list(_iter_sst_data_blocks(fdata))
            else:  # .log
                blocks = list(_iter_log_records(fdata))
        except Exception:
            # 解析失败则退回原始字节扫描（兜底）
            blocks = [fdata]

        val = _scan_blocks(blocks)
        if val:
            last_val = val

        if last_val is not None:
            break

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
    ls_dir  = os.path.join(user_data_path, profile, "Local Storage", "leveldb")
    if not os.path.isdir(ls_dir):
        return []

    try:
        ids = _read_leveldb(ls_dir)
        # 过滤掉极小的 ID（真实 titan007 赛事 ID > 100000）
        return [mid for mid in ids if mid.isdigit() and int(mid) > 100_000]
    except Exception:
        return []
