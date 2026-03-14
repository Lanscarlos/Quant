"""
Database schema definitions.

All DDL is kept here so there is a single source of truth.
create_all() is idempotent: safe to call on every startup.
"""
import sqlite3

_DDL = [
    # ------------------------------------------------------------------
    # 1. leagues — 联赛字典
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS leagues (
        league_abbr    TEXT    PRIMARY KEY,
        league_name_cn TEXT,
        league_color   TEXT,
        country_id     INTEGER
    )
    """,

    # ------------------------------------------------------------------
    # 2. teams — 球队字典
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS teams (
        team_id      INTEGER PRIMARY KEY,
        team_name_cn TEXT,
        team_name_en TEXT
    )
    """,

    # ------------------------------------------------------------------
    # 3. matches — 赛事列表
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS matches (
        schedule_id       INTEGER PRIMARY KEY,
        match_time        TEXT    NOT NULL,
        status            INTEGER NOT NULL DEFAULT 0,
        league_abbr       TEXT    REFERENCES leagues(league_abbr),
        home_team_id      INTEGER NOT NULL REFERENCES teams(team_id),
        home_rank         INTEGER,
        away_team_id      INTEGER NOT NULL REFERENCES teams(team_id),
        away_rank         INTEGER,
        home_score        INTEGER,
        away_score        INTEGER,
        home_half_score   INTEGER,
        away_half_score   INTEGER,
        home_red_cards    INTEGER DEFAULT 0,
        away_red_cards    INTEGER DEFAULT 0,
        home_yellow_cards INTEGER DEFAULT 0,
        away_yellow_cards INTEGER DEFAULT 0,
        fetched_at        TEXT    NOT NULL DEFAULT (datetime('now', '+8 hours'))
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_matches_time      ON matches(match_time)",
    "CREATE INDEX IF NOT EXISTS idx_matches_status    ON matches(status)",
    "CREATE INDEX IF NOT EXISTS idx_matches_league    ON matches(league_abbr)",
    "CREATE INDEX IF NOT EXISTS idx_matches_home_team ON matches(home_team_id)",
    "CREATE INDEX IF NOT EXISTS idx_matches_away_team ON matches(away_team_id)",

    # ------------------------------------------------------------------
    # 4. match_standings — 联赛排名详情
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS match_standings (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        schedule_id   INTEGER NOT NULL REFERENCES matches(schedule_id) ON DELETE CASCADE,
        side          TEXT    NOT NULL CHECK(side   IN ('home', 'away')),
        period        TEXT    NOT NULL CHECK(period IN ('ft', 'ht')),
        scope         TEXT    NOT NULL CHECK(scope  IN ('total', 'home', 'away', 'last6')),
        played        INTEGER,
        win           INTEGER,
        draw          INTEGER,
        loss          INTEGER,
        goals_for     INTEGER,
        goals_against INTEGER,
        goal_diff     INTEGER,
        points        INTEGER,
        rank          INTEGER,
        win_rate      REAL,
        fetched_at    TEXT    NOT NULL DEFAULT (datetime('now', '+8 hours')),
        UNIQUE(schedule_id, side, period, scope)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_standings_match ON match_standings(schedule_id)",

    # ------------------------------------------------------------------
    # 5. companies — 博彩公司字典
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS companies (
        company_id   INTEGER PRIMARY KEY,
        company_name TEXT    NOT NULL,
        label        TEXT
    )
    """,

    # ------------------------------------------------------------------
    # 6. match_odds — 欧赔快照
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS match_odds (
        record_id         INTEGER PRIMARY KEY,
        schedule_id       INTEGER NOT NULL REFERENCES matches(schedule_id) ON DELETE CASCADE,
        company_id        INTEGER NOT NULL REFERENCES companies(company_id),
        open_win          REAL,
        open_draw         REAL,
        open_lose         REAL,
        open_win_prob     REAL,
        open_draw_prob    REAL,
        open_lose_prob    REAL,
        open_payout_rate  REAL,
        cur_win           REAL,
        cur_draw          REAL,
        cur_lose          REAL,
        cur_win_prob      REAL,
        cur_draw_prob     REAL,
        cur_lose_prob     REAL,
        cur_payout_rate   REAL,
        kelly_win         REAL,
        kelly_draw        REAL,
        kelly_lose        REAL,
        hist_kelly_win    REAL,
        hist_kelly_draw   REAL,
        hist_kelly_lose   REAL,
        change_time       TEXT,
        flag1             INTEGER,
        flag2             INTEGER,
        fetched_at        TEXT    NOT NULL DEFAULT (datetime('now', '+8 hours')),
        UNIQUE(schedule_id, company_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_odds_match ON match_odds(schedule_id)",

    # ------------------------------------------------------------------
    # 7. odds_history — 赔率历史变动
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS odds_history (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id    INTEGER NOT NULL REFERENCES match_odds(record_id) ON DELETE CASCADE,
        schedule_id  INTEGER NOT NULL,
        company_id   INTEGER NOT NULL,
        win          REAL,
        draw         REAL,
        lose         REAL,
        win_prob     REAL,
        draw_prob    REAL,
        lose_prob    REAL,
        payout_rate  REAL,
        kelly_win    REAL,
        kelly_draw   REAL,
        kelly_lose   REAL,
        change_time  TEXT    NOT NULL,
        is_opening   INTEGER NOT NULL DEFAULT 0,
        win_dir      TEXT CHECK(win_dir  IN ('up', 'down', 'unchanged')),
        draw_dir     TEXT CHECK(draw_dir IN ('up', 'down', 'unchanged')),
        lose_dir     TEXT CHECK(lose_dir IN ('up', 'down', 'unchanged')),
        UNIQUE(record_id, change_time)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_odds_history_rid   ON odds_history(record_id)",
    "CREATE INDEX IF NOT EXISTS idx_odds_history_match ON odds_history(schedule_id)",

    # ------------------------------------------------------------------
    # 8. match_asian_odds — 亚让赔率快照
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS match_asian_odds (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        schedule_id    INTEGER NOT NULL REFERENCES matches(schedule_id) ON DELETE CASCADE,
        company_id     INTEGER NOT NULL REFERENCES companies(company_id),
        open_handicap  TEXT,
        open_home      REAL,
        open_away      REAL,
        cur_handicap   TEXT,
        cur_home       REAL,
        cur_away       REAL,
        fetched_at     TEXT    NOT NULL DEFAULT (datetime('now', '+8 hours')),
        UNIQUE(schedule_id, company_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_asian_odds_match ON match_asian_odds(schedule_id)",

    # ------------------------------------------------------------------
    # 9. asian_odds_history — 亚让赔率历史变动
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS asian_odds_history (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        schedule_id  INTEGER NOT NULL,
        company_id   INTEGER NOT NULL,
        change_time  TEXT    NOT NULL,
        score        TEXT,
        home_odds    REAL,
        handicap     TEXT,
        away_odds    REAL,
        is_opening   INTEGER NOT NULL DEFAULT 0,
        home_dir     TEXT CHECK(home_dir IN ('up', 'down', 'unchanged')),
        away_dir     TEXT CHECK(away_dir IN ('up', 'down', 'unchanged')),
        UNIQUE(schedule_id, company_id, change_time)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_asian_history_match ON asian_odds_history(schedule_id)",
    "CREATE INDEX IF NOT EXISTS idx_asian_history_co    ON asian_odds_history(schedule_id, company_id)",
]


def create_all(conn: sqlite3.Connection) -> None:
    """Create all tables and indexes. Safe to call on every startup."""
    with conn:
        for stmt in _DDL:
            conn.execute(stmt)