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

### Entry Point

`main.py` boots NiceGUI in native (desktop window) mode and calls `init_db()`.  
App constants (`PORT=19193`, `NAME`, `ICON`, `SIZE=(1260,840)`) and all page route wiring live in `src/ui/index.py`.

### Navigation & Routing

`src/ui/router.py` implements a custom `Router` backed by `ui.tab_panels`. All pages are **pre-rendered once** on `mount()`; navigation calls `set_value()` to switch the visible panel without re-rendering. Pages can return a callable from their `render()` function to expose a trigger API (used by `fetch` → `conclusion` handoff).

The left sidebar (`src/ui/frame/navigation_bar.py`, 56px wide) has four entries: 赛事列表, 抓取数据, 结论, 设置.

### Three-Page Flow

```
赛事列表 (match_list)
    ↓ rowClick on a match
抓取数据 (fetch) — 6-step phased pipeline
    ↓ on_complete callback
结论 (conclusion) — display fetched analysis data
```

### Service Layer

All HTTP fetching and parsing lives in `src/service/`. Each module is a self-contained fetch+parse+upsert pipeline:

| Module | Source URL | Encoding | Writes to |
|--------|-----------|----------|-----------|
| `match_list.py` | `bf.titan007.com/VbsXml/bfdata.js` | GBK | `leagues`, `teams`, `matches` |
| `match_detail.py` | `zq.titan007.com/analysis/{mid}sb.htm` | UTF-8 | `match_standings`, `match_recent`, `match_h2h` |
| `euro_odds.py` | `1x2d.titan007.com/{mid}.js` | UTF-8 | `odds_wh`, `odds_coral` |
| `euro_odds_history.py` | `1x2.titan007.com/OddsHistory.aspx?...` | UTF-8 | `odds_wh_history`, `odds_coral_history` |
| `asian_odds.py` | `vip.titan007.com/AsianOdds_n.aspx?id={mid}` | GB2312 | `asian_odds_365` |
| `asian_odds_history.py` | `vip.titan007.com/changeDetail/handicap.aspx?...` | GB2312 | `asian_odds_365_history` |
| `browser_filter.py` | Chrome/Edge LevelDB localStorage | — | returns `list[str]` IDs |
| `freshness.py` | DB queries only | — | returns bool |

**Company IDs**: William Hill = 115, Ladbrokes (Coral) = 82, Bet365 for asian odds.

### Fetch Pipeline (`src/ui/page/fetch/`)

6 steps in 4 phases; same-phase steps run via `asyncio.gather()`. Each step class defines `KEY`, `LABEL`, `ICON`, `PHASE`, `DEPENDS_ON`, `should_skip(mid)`, and `async fetch(mid, ctx, tracker)`. The `ctx` dict is shared across steps to pass `record_ids` and `match_year`.

```
Phase 1: StepMatchDetail   (赛事详情)
Phase 2: StepSubOdds       (近六场+交手的子比赛赔率)
Phase 3: StepEuroOdds  ┐
         StepAsianOdds ┘ (parallel)
Phase 4: StepEuroHistory  ┐
         StepAsianHistory ┘ (parallel)
```

Progress display uses `ProgressTracker` + `SubTask` (`progress.py`): io_bound threads call `tracker.task(key, label)` as a context manager; `loop.call_soon_threadsafe` triggers UI refreshes.

### Freshness Logic (`src/service/freshness.py`)

`should_fetch_*()` functions are called by the UI before each HTTP request:

| Entity | Completed (-1) | In-progress (1/3) | Not started (0) |
|--------|---------------|-------------------|-----------------|
| match_list | never re-fetch | 2 min | 10 min |
| match_detail | fetch once | skip | 6 hrs |
| euro/asian odds | fetch once | 2 min | 10 min |
| odds history | fetch once | always | always |

### Database (`src/db/`)

- `connection.py`: SQLite singleton at `data/quant.db`, WAL mode, FK ON, `row_factory = sqlite3.Row`
- `schema.py`: all DDL + `_migrate()` for incremental column additions; `create_all()` is idempotent
- `repo/`: one file per table, each exposes `upsert_*()` using `INSERT OR REPLACE` or `INSERT OR IGNORE`

**11 tables**: `leagues`, `teams`, `matches`, `match_standings`, `match_recent`, `match_h2h`, `odds_wh`, `odds_wh_history`, `odds_coral`, `odds_coral_history`, `asian_odds_365`, `asian_odds_365_history`

`match_standings` stores 16 rows per match: 2 sides (`home`/`away`) × 2 periods (`ft`/`ht`) × 4 scopes (`total`/`home`/`away`/`last6`).

### Parsing Notes

- **match_list**: GBK JS file; each `A[i]` is a `^`-delimited string with 53 fields; field index map in `_FIELDS` dict
- **match_detail**: `h_data`/`a_data`/`v_data` inline JS arrays extracted with regex, evaluated with `ast.literal_eval`; team HTML contains `<span class=hp>` for handicap recipient marker (strip before extracting name); standings parsed via BeautifulSoup on `div#porlet_5`
- **odds history**: direction (`up`/`down`/`unchanged`) derived from HTML font color (green = up, red = down)
- **browser_filter**: reads LevelDB `.ldb`/`.log` files directly (binary scan), decodes Base36-encoded match IDs from `Bet007live_hiddenID` key

### Key Patterns

- **Async IO**: all HTTP calls wrapped in `run.io_bound()` so they don't block NiceGUI's event loop
- **`@ui.refreshable`**: used for data table and step status rows; call `.refresh()` to re-render just that component
- **Conclusion page API**: `render()` returns a `trigger(mid)` callable; the router stores it via `get_api('conclusion')` and the fetch page calls it on completion
- **`scraper/`**: legacy modules, not part of the current data flow

### Build Notes

- `ONE_FILE = False` → onedir mode (faster startup)
- `DEV_MODE = False` → `--windowed` (no console); set `True` for a visible console during debugging
- NiceGUI's package directory must be passed via `--add-data` for PyInstaller
