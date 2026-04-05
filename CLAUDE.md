# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Quant** is a desktop quantitative football-odds analysis app built with [NiceGUI](https://nicegui.io/) in native mode. It scrapes match data and odds from titan007.com, stores them in a local SQLite database, and presents them in a desktop GUI window.

## Development Commands

```bash
# Run the app
python main.py

# Build a distributable executable (onedir mode)
python build.py
```

The build script creates a temporary `.build_venv`, installs deps, runs PyInstaller, then cleans up. Output goes to `dist/Quant/`.

## Architecture

### Entry Point & App Constants

`main.py` boots NiceGUI in native (desktop window) mode. App constants (`PORT=19193`, `NAME`, `ICON`, `SIZE=(1260,840)`) and page routes live in `src/ui/index.py`.

### Module Structure

```
src/
  ui/
    index.py              — app constants + NiceGUI page wiring
    router.py             — custom Router (tab_panel-based navigation)
    frame/navigation_bar.py — left sidebar, 56px wide
    page/
      match_list.py       — main historical data table + matching-odds panels
      match_detail.py     — per-match standings + recent 6 games + odds
      dashboard.py        — placeholder (unused)
    panel/
      home.py             — Lottie animation placeholder
      info.py             — TODO checklist
  service/
    match_list.py         — fetch + parse match list (GBK JS array, 53 fields)
    match_detail.py       — fetch + parse standings & recent 6 matches (UTF-8 HTML)
    match_odds_list.py    — European (1x2) odds snapshot
    match_odds_history.py — European odds change history
    match_asian_handicap_list.py    — Asian handicap odds snapshot
    match_asian_handicap_history.py — Asian handicap history
    browser_filter.py     — reads Chrome/Edge LevelDB localStorage for match whitelist
  db/
    connection.py         — SQLite singleton (WAL mode, FK enabled)
    schema.py             — idempotent DDL + migration helpers; call create_all() on startup
    repo/                 — one module per table, each exposes upsert_*()
  sync/
    coordinator.py        — freshness-aware should_fetch_*() decision logic
  scraper/                — legacy modules, not used in current flow
```

### Data Flow

```
titan007.com → service/*.py (fetch + parse)
            → db/repo/*.py (upsert into SQLite data/quant.db)
            → UI reads via service modules (direct SQL JOINs)
```

### Data Sources

| Service | URL | Encoding |
|---------|-----|----------|
| match_list | `https://bf.titan007.com/VbsXml/bfdata.js` | GBK |
| match_detail | `https://zq.titan007.com/analysis/{mid}sb.htm` | UTF-8 |
| match_odds_list | `https://1x2d.titan007.com/{mid}.js` | UTF-8 |
| match_odds_history | `https://1x2.titan007.com/OddsHistory.aspx?...` | UTF-8 |
| match_asian_handicap_list | `https://vip.titan007.com/AsianOdds_n.aspx?id={mid}` | GB2312 |
| match_asian_handicap_history | `https://vip.titan007.com/changeDetail/handicap.aspx?...` | GB2312 |

### Database Schema (10 Tables)

**Dimension tables** (write-once via `INSERT OR IGNORE`): `leagues`, `teams`, `companies`

**Match fact tables**: `matches` (status/scores), `match_standings` (16 rows per match: 2 sides × 2 periods × 4 scopes), `match_recent` (recent 6 games per team)

**Odds fact tables**: `match_odds`, `odds_history`, `match_asian_odds`, `asian_odds_history`

All odds history tables track direction (up/down/unchanged) derived from HTML font color (green=up, red=down).

### Freshness Logic (`src/sync/coordinator.py`)

UI calls `should_fetch_*()` before each network request:

| Entity | Completed match | In-progress (status 1/3) | Not started (status 0) |
|--------|----------------|--------------------------|------------------------|
| match_list | — | — | stale after 10 min |
| match_detail | fetch once | skip refetch | stale after 6 hrs |
| match_odds | fetch once | stale after 2 min | stale after 10 min |
| odds_history | fetch once | always fetch | always fetch |

### Key Patterns

- **Custom router**: `src/ui/router.py` pre-renders all pages on mount; navigation switches tab-panel visibility rather than re-rendering.
- **Async IO**: Long HTTP requests use `run.io_bound()` wrapper to avoid blocking NiceGUI's event loop.
- **Browser filter**: `browser_filter.py` reads Chrome/Edge LevelDB localStorage to extract user's match whitelist from the `Bet007live_hiddenID` key.
- **match_list SQL**: The main table query in `src/service/match_list.py` JOINs matches with William Hill odds (company_id=115) directly in SQL.
- **match_detail parsing**: `h_data`/`a_data` JS arrays (20–22 fields each, reverse-chronological) extracted via regex from raw HTML; standings via BeautifulSoup on `div#porlet_5` tables.

### Build Notes

- `ONE_FILE = False` → onedir mode (faster startup than single-file)
- `DEV_MODE = False` → `--windowed` (no console); set `True` for debugging
- NiceGUI's package directory must be passed via `--add-data` for PyInstaller
