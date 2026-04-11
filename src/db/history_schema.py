"""
History database schema definitions.

Two tables:
  saved_matches   — denormalized match + odds summary for list display & search
  saved_snapshots — JSON blobs of full conclusion data for detail view
"""
import sqlite3

_DDL = [
    # ------------------------------------------------------------------
    # 1. saved_matches — 列表展示 + 检索（反范式化）
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS saved_matches (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        schedule_id         INTEGER NOT NULL UNIQUE,
        saved_at            TEXT    NOT NULL DEFAULT (datetime('now', '+8 hours')),
        match_time          TEXT,
        home_team           TEXT,
        away_team           TEXT,
        league              TEXT,
        home_rank           INTEGER,
        away_rank           INTEGER,
        home_score          INTEGER,
        away_score          INTEGER,
        home_half_score     INTEGER,
        away_half_score     INTEGER,

        -- 威廉希尔赔率
        wh_open_win         REAL,
        wh_open_draw        REAL,
        wh_open_lose        REAL,
        wh_h30_win          REAL,
        wh_h30_draw         REAL,
        wh_h30_lose         REAL,
        wh_cur_win          REAL,
        wh_cur_draw         REAL,
        wh_cur_lose         REAL,

        -- 立博赔率
        coral_open_win      REAL,
        coral_open_draw     REAL,
        coral_open_lose     REAL,
        coral_cur_win       REAL,
        coral_cur_draw      REAL,
        coral_cur_lose      REAL,

        -- Bet365 亚盘
        asian_open_handicap TEXT,
        asian_open_home     REAL,
        asian_open_away     REAL,
        asian_cur_handicap  TEXT,
        asian_cur_home      REAL,
        asian_cur_away      REAL,

        -- 积分 & 胜平负
        home_pts            INTEGER,
        away_pts            INTEGER,
        home_wdl_win        INTEGER,
        home_wdl_draw       INTEGER,
        home_wdl_loss       INTEGER,
        away_wdl_win        INTEGER,
        away_wdl_draw       INTEGER,
        away_wdl_loss       INTEGER,

        -- 用户输入
        analysis_note       TEXT,
        tags                TEXT
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_saved_matches_time   ON saved_matches(match_time)",
    "CREATE INDEX IF NOT EXISTS idx_saved_matches_league ON saved_matches(league)",

    # ------------------------------------------------------------------
    # 2. saved_snapshots — 详情展示用 JSON 快照
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS saved_snapshots (
        saved_match_id  INTEGER PRIMARY KEY REFERENCES saved_matches(id) ON DELETE CASCADE,
        match_json      TEXT,
        extras_json     TEXT,
        recent_json     TEXT,
        h2h_json        TEXT,
        odds_json       TEXT,
        asian_odds_json TEXT
    )
    """,
]


def create_all(conn: sqlite3.Connection) -> None:
    """Create all history tables and indexes. Safe to call on every startup."""
    with conn:
        for stmt in _DDL:
            conn.execute(stmt)
        # Incremental migrations for existing databases
        existing = {r[1] for r in conn.execute("PRAGMA table_info(saved_matches)")}
        for col, ddl in [
            ('wh_h30_win',  'ALTER TABLE saved_matches ADD COLUMN wh_h30_win  REAL'),
            ('wh_h30_draw', 'ALTER TABLE saved_matches ADD COLUMN wh_h30_draw REAL'),
            ('wh_h30_lose', 'ALTER TABLE saved_matches ADD COLUMN wh_h30_lose REAL'),
        ]:
            if col not in existing:
                conn.execute(ddl)
