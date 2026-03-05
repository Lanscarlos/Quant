# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Quant** is a desktop quantitative analysis app built with [NiceGUI](https://nicegui.io/) in native mode. It scrapes football match data (league standings) from titan007.com and presents it in a desktop GUI window.

## Development Commands

```bash
# Run the app in development mode
python main.py

# Build a distributable executable (onedir mode)
python build.py
```

The build script (`build.py`) creates a temporary `.build_venv`, installs dependencies, runs PyInstaller, then cleans up the venv and `.spec`/`build/` artifacts. Output goes to `dist/Quant/`.

## Architecture

### Entry Point
`main.py` calls `ui.run()` in NiceGUI **native mode** (desktop window, no browser). App metadata (port, title, icon, window size) is imported from `src/app.py`.

### Module Structure
- `src/app.py` — App constants (`PORT`, `NAME`, `ICON`, `SIZE`) and NiceGUI page routes defined with `@ui.page('/')`. Import business logic modules here to wire them into the UI.
- `src/hello.py` — Example business logic module (template for new features).
- `src/parse.py` — Web scraper: fetches a titan007.com match analysis page, parses league ranking tables with BeautifulSoup, and outputs a DataFrame saved as `ranking.csv`.

### Key Patterns
- **NiceGUI routing**: Pages are registered via `@ui.page('/route')` decorators in `src/app.py`.
- **Logic separation**: UI code stays in `src/app.py`; data/business logic lives in separate `src/` modules imported by `app.py`.
- **Scraping**: `parse.py` targets `div#porlet_5` tables on titan007 pages. Table indices [2–5] correspond to home/away × full/half-time standings.

### Build Notes
- `ONE_FILE = False` in `build.py` uses onedir mode for faster startup.
- `DEV_MODE = False` builds a windowless (`--windowed`) executable; set to `True` for a console window during debugging.
- NiceGUI's package directory must be explicitly passed via `--add-data` for PyInstaller to include it.