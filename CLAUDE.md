# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Conventions

- **回答语言**：总结性回复、说明、最终结论一律使用中文，保持与用户沟通语种一致。
- **代码注释**：所有新增或修改的注释必须使用中文（包括函数 docstring、行内注释、TODO 等）；仅当必须引用外部英文术语/标识符时保留英文。

## Project Overview

**Quant** is a desktop football-odds analysis app built on [NiceGUI](https://nicegui.io/) in native mode. It scrapes match data and odds from titan007.com, stores them in local SQLite, and presents an analysis UI in a desktop window.

## Commands

```bash
python main.py   # 运行应用
python build.py  # 打包（创建临时 .build_venv → pip install → PyInstaller → 清理）
```

Build output: `dist/Quant/` (onedir mode). No test suite or linter is configured.

## Entry Point

`main.py` calls `init_db()` **and** `init_history_db()` before `ui.run(native=True)`. App constants (`PORT=19193`, `NAME`, `ICON`, `SIZE=(1260,840)`) live in `src/ui/index.py`, which also does all route wiring.

## Two SQLite Databases

Both opened as WAL + FK ON, `row_factory=sqlite3.Row`, frozen-aware path resolution (`sys.frozen` → `sys.executable.parent`, else repo root).

| DB | File | Purpose | Module |
|----|------|---------|--------|
| Live | `data/quant.db` | All scraped data | `src/db/connection.py` + `schema.py` |
| History | `data/history.db` | User-saved analysis snapshots | `src/db/history_connection.py` + `history_schema.py` |

`quant.db` tables (14): dimension `leagues`, `teams`, `companies`; match `matches`, `match_standings` (16 rows/match = 2 sides × 2 periods × 4 scopes), `match_recent` (每侧最多 8 条近期赛事), `match_h2h` (最多 20 条交手), `league_table_snapshot` (pre-match league table, only for isShowIntegral=1 leagues); odds `odds_wh` / `odds_wh_history` (WH, company 115), `odds_coral` / `odds_coral_history` (Ladbrokes, company 82), `asian_odds_365` / `asian_odds_365_history` (Bet365).

`history.db` tables: `saved_matches` (denormalized flat row for list/filter) + `saved_snapshots` (JSON blobs keyed by `saved_match_id` with ON DELETE CASCADE). Schema has inline `_migrate()` adding `wh_h30_*` columns.

## Navigation & Routing

`src/ui/router.py` — custom `Router` over `ui.tab_panels`. All pages are **pre-rendered once** on `mount()`; `navigate(key)` calls `set_value()` to flip the visible panel. If a page's `render()` returns a value (e.g., a `trigger(mid)` callable), the router stores it in `_apis` retrievable via `get_api(key)`.

Five routes registered in `src/ui/index.py`: `match_list`, `fetch`, `conclusion`, `history`, `settings`. Navigation bar is 56px wide (`src/ui/frame/navigation_bar.py`).

**Inter-page handoff** (done in `index.py` via holder lists to break circular init):
- `match_list` rowClick → navigate `fetch` → fetch's `trigger(mid)` kicks off pipeline
- `fetch` on_complete → navigate `conclusion` → conclusion's `trigger(mid)`
- `history` rowClick → navigate `conclusion` → `trigger(mid, source='history')` (loads from history.db snapshot)
- `conclusion` back button → `on_back(source)` returns to `match_list` or `history`

## Fetch Pipeline (`src/ui/page/fetch/`)

6 steps across 4 phases in `steps.py`. Each step declares `KEY`, `LABEL`, `ICON`, `PHASE`, `DEPENDS_ON`, `should_skip(mid, force)`, `async fetch(mid, ctx, tracker)`. Same-phase steps run in parallel via `asyncio.gather()`. `ctx` dict threads state across phases (`record_ids`, `match_year`).

```
Phase 1  StepMatchDetail   (排名 + 近六场 + 交手)
Phase 2  StepSubOdds       (子比赛赔率) — BACKGROUND=True，不阻塞后续阶段
Phase 3  StepEuroOdds │ StepAsianOdds      (parallel)
Phase 4  StepEuroHistory │ StepAsianHistory (parallel, Euro depends on Phase 3 record_ids)
```

`StepEuroHistory` falls back to `_load_record_ids_from_db()` when phase 3 was freshness-skipped. `_get_match_year()` similarly backfills from `matches.match_time` if not in ctx.

Progress UI uses `ProgressTracker` + `SubTask` (`progress.py`): `run.io_bound` threads call `tracker.task(key, label)` as a context manager; `loop.call_soon_threadsafe` triggers `@ui.refreshable` re-renders.

## Service Layer (`src/service/`)

Self-contained fetch+parse+upsert pipelines, one per data source:

| Module | URL | Encoding | Writes |
|--------|-----|----------|--------|
| `match_list.py` | `bf.titan007.com/VbsXml/bfdata.js` | GBK | `leagues`, `teams`, `matches` |
| `match_detail.py` | `zq.titan007.com/analysis/{mid}sb.htm` | UTF-8 | `match_standings`, `match_recent`, `match_h2h`, `league_table_snapshot` |
| `euro_odds.py` | `1x2d.titan007.com/{mid}.js` | UTF-8 | `odds_wh`, `odds_coral` |
| `euro_odds_history.py` | `1x2.titan007.com/OddsHistory.aspx?...` | UTF-8 | `odds_wh_history`, `odds_coral_history` |
| `asian_odds.py` | `vip.titan007.com/AsianOdds_n.aspx?id={mid}` | GB2312 | `asian_odds_365` |
| `asian_odds_history.py` | `vip.titan007.com/changeDetail/handicap.aspx?...` | GB2312 | `asian_odds_365_history` |
| `live_score.py` | `live.titan007.com/jsData/{prefix}/{sid}.js` | GBK/UTF-8 | returns `{home_score, away_score, status}`; infers finished if 110+ min past kickoff |
| `browser_filter.py` | Chrome/Edge LevelDB (binary scan) | — | returns `list[str]` IDs (Base36-decoded) |
| `freshness.py` | DB queries | — | `should_fetch_*()` bool helpers |
| `config.py` | `data/config.json` | — | `get/set_refresh_interval()`; default 1200 s |

### Freshness thresholds (`src/service/freshness.py`)

| Entity | Finished (-1) | In-progress (1/3) | Not started (0) |
|--------|---------------|-------------------|-----------------|
| match_list | never | 2 min | 10 min |
| match_detail | once | skip | 6 hrs |
| euro / asian odds | once | 2 min | 10 min |
| odds history | once | always | always |

## Parsing Notes

- **match_list**: GBK; each `A[i]` is `^`-delimited with ~53 fields (see `_FIELDS` map).
- **match_detail**: inline `h_data` / `a_data` / `v_data` JS arrays extracted via regex + `ast.literal_eval`. Each entry has 20–22 fields, reverse-chronological:
  - `[0]` YY-MM-DD, `[2]` league, `[4]/[6]` team IDs, `[5]/[7]` team HTML (strip `<span class=hp>` handicap marker before extracting name), `[8]/[9]` FT goals, `[10]` HT "H-A", `[11]` handicap, `[12]` result (1/0/-1), `[13]` hc_result (-2 no data / -1 loss / 0 push / 1 win), `[15]` match_id.
  - Standings parsed via BeautifulSoup on `div#porlet_5`.
- **odds history**: direction (up/down/unchanged) derived from font color (green=up, red=down).
- **browser_filter**: scans LevelDB `.ldb`/`.log` bytes for the `Bet007live_hiddenID` key (Base36-encoded match IDs).

## History Page (`src/ui/page/history/`)

List view over `history.db.saved_matches` with four filter dialogs (`dialogs.py` — time/league/team/odds). `list_saved_matches()` in `db/repo/history.py` supports a `filters` dict with keys: `time_from/to`, `league` (list), `team` (list) + `team_role` (home/away/both), `odds_type` (whitelisted via `_ODDS_COLS`) + `odds_min/max`, `limit`. `save_match(mid)` in the same repo reads from `quant.db`, writes denormalized columns + JSON snapshot into `history.db`, using `INSERT OR REPLACE` on `schedule_id`. `backfill_h30()` runs on page load to patch legacy rows with missing `wh_h30_*` (30-min-pre-match WH odds).

## Key Patterns

- **Async IO**: every HTTP call wrapped in `run.io_bound()` so it doesn't block NiceGUI's event loop.
- **`@ui.refreshable`**: used for tables and step rows; call `.refresh()` for fine-grained re-render.
- **Conclusion page** reads either live (`queries.load_all_from_quant`) or snapshot (`repo.history.load_snapshot`) depending on `source` passed to its trigger; both return the same `{match, extras, recent, h2h, odds, asian_odds, league_table}` shape.
- **Match-list rank prefix**: `queries._rank_prefix(name, rank)` prepends `[N]` to team names; prefers standings data, falls back to `matches.home_rank / away_rank`.
- **Config persistence**: `src/service/config.py` reads/writes `data/config.json`; `refresh_interval` defaults to 1200 s (20 min), range 60–3600 s.
- **`src/scraper/`**: legacy, not used by the current flow.

## Build Notes

`build.py` constants: `ONE_FILE=False` (onedir, faster startup), `DEV_MODE=False` (`--windowed`, flip to `True` for console). NiceGUI's package dir is passed to PyInstaller via `--add-data` (resolved from the freshly-built venv).
