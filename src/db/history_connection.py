"""
SQLite connection manager for history database.

Provides a singleton connection to data/history.db.
Call init_history_db() once at app startup to create all tables.
"""
import sys
import sqlite3
from pathlib import Path


def _get_history_db_path() -> Path:
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).parent.parent.parent
    return base / "data" / "history.db"


_DB_PATH = _get_history_db_path()

_conn: sqlite3.Connection | None = None


def get_history_conn() -> sqlite3.Connection:
    """Return the shared history SQLite connection, creating it on first call."""
    global _conn
    if _conn is None:
        _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False, timeout=5)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL")
        _conn.execute("PRAGMA foreign_keys=ON")
    return _conn


def init_history_db() -> None:
    """Initialize the history database: create all tables and indexes."""
    from .history_schema import create_all
    create_all(get_history_conn())
