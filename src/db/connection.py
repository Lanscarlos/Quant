"""
SQLite connection manager.

Provides a singleton connection to data/quant.db.
Call init_db() once at app startup to create all tables.
"""
import sys
import sqlite3
from pathlib import Path


def _get_db_path() -> Path:
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent.parent.parent
    return base / "data" / "quant.db"


_DB_PATH = _get_db_path()

_conn: sqlite3.Connection | None = None


def get_conn() -> sqlite3.Connection:
    """Return the shared SQLite connection, creating it on first call."""
    global _conn
    if _conn is None:
        _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False, timeout=5)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("PRAGMA foreign_keys=ON")
    return _conn


def init_db() -> None:
    """Initialize the database: create all tables and indexes."""
    from .schema import create_all
    create_all(get_conn())