"""
应用配置管理。

以 data/config.json 为持久化存储，提供 get/set 接口。
支持打包环境（sys.frozen）路径解析，与 DB connection 保持一致。
"""
import json
import sys
from pathlib import Path


def _get_config_path() -> Path:
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent.parent.parent
    return base / "data" / "config.json"


_CONFIG_PATH = _get_config_path()

_DEFAULTS: dict = {
    "refresh_interval": 1200,  # 赛事列表自动刷新间隔（秒），默认 20 分钟
}


def _load() -> dict:
    if _CONFIG_PATH.exists():
        try:
            data = json.loads(_CONFIG_PATH.read_text(encoding='utf-8'))
            return {**_DEFAULTS, **data}
        except Exception:
            pass
    return dict(_DEFAULTS)


def _save(data: dict) -> None:
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CONFIG_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding='utf-8',
    )


def get_refresh_interval() -> int:
    """返回赛事列表自动刷新间隔（秒）。"""
    return int(_load().get("refresh_interval", _DEFAULTS["refresh_interval"]))


def set_refresh_interval(seconds: int) -> None:
    """持久化保存赛事列表自动刷新间隔（秒）。"""
    data = _load()
    data["refresh_interval"] = seconds
    _save(data)
