# CLAUDE.md - Project Guide for Claude Code

## Project Overview

This project scrapes county-level health insurance premium data from Ideon's interactive ICHRA map at https://ideonapi.com/ideon-ichra-insights-by-state/

**Goal**: Extract Individual vs Small Group ACA plan pricing for all ~3,100 US counties into structured CSV format.

**Data available on the map** (per county):
- County name, State
- Individual premium (monthly, for age 27 or 50)
- Small Group premium
- Price difference (Individual - Small Group)

**Map filters**: Year (2017-2026), Age (27/50), Metal tier (Bronze/Silver/Gold)

**Target output columns**: `county, state, individual_premium, small_group_premium, difference, year, age, metal`

## File Structure

```
ideon-scraper-repo/
├── scripts/
│   ├── inspect_network.py    # Network inspector - finds data source
│   └── scrape_ideon_map.py   # Main scraper - hover-based extraction
├── references/
│   └── selectors.md          # CSS selector troubleshooting guide
├── requirements.txt          # playwright, pandas
├── README.md                 # User documentation
└── CLAUDE.md                 # This file
```

## How to Run

```bash
# Install dependencies
pip install playwright pandas
playwright install chromium

# Step 1: Run network inspector first (find if there's a JSON endpoint)
python scripts/inspect_network.py

# Step 2: If no API found, run the hover scraper
python scripts/scrape_ideon_map.py --year 2026 --age 50 --metal gold --output data.csv

# Debug mode (visible browser, single state)
python scripts/scrape_ideon_map.py --state CA --debug
```

## Architecture & Approach

### Two-Phase Strategy

1. **Phase 1: Network Inspection** (`inspect_network.py`)
   - Opens browser, captures all network requests
   - Looks for `.json`, `.geojson`, `api`, `data` URLs
   - Saves any large JSON responses to `captured_data.json`
   - **Preferred if found**: Direct API fetch is faster and more reliable than scraping

2. **Phase 2: Hover Scraping** (`scrape_ideon_map.py`)
   - Falls back to this if no direct data source exists
   - Detects map type (SVG vs Canvas/Mapbox GL)
   - **SVG maps**: Hover over each `<path>` element
   - **Canvas maps**: Grid-scan the canvas at 8px intervals
   - Parses tooltip text with regex, dedupes by county+state

### Key Functions in `scrape_ideon_map.py`

| Function | Purpose |
|----------|---------|
| `parse_tooltip()` | Regex extraction from tooltip text |
| `set_map_filters()` | Sets year/age/metal dropdowns |
| `scrape_svg_map()` | Hovers over SVG `<path>` elements |
| `scrape_canvas_map()` | Grid-scans Mapbox canvas |
| `get_tooltip_text()` | Finds visible tooltip element |

### Tooltip Pattern

The scraper expects tooltip text like:
```
Shasta County, CA
Diff (Ind - Small): $605.64
Individual: $1,414.50  Small Group: $808.86
```

## Current Status

- [x] Network inspector script complete
- [x] Hover-based scraper with SVG/Canvas support
- [x] Tooltip regex parsing
- [x] CSV output with sorting
- [ ] **NOT YET TESTED** - Need to run inspector to find data source
- [ ] May need selector updates if map structure differs from expected

## Next Steps

1. **Run the inspector**: `python scripts/inspect_network.py`
   - Look for JSON endpoints in the output
   - Check `captured_data.json` if created

2. **If JSON/API found**:
   - Create a simpler `fetch_data.py` that hits the endpoint directly
   - Much faster and more reliable than hover scraping

3. **If no API (must scrape)**:
   - Test scraper on single state: `python scripts/scrape_ideon_map.py --state TX --debug`
   - Watch for tooltip detection issues
   - Update selectors in `get_tooltip_text()` if needed

4. **Selector troubleshooting**: See [references/selectors.md](references/selectors.md) for common map library selectors

## Common Issues

| Issue | Solution |
|-------|----------|
| Tooltip not detected | Add new selector to `get_tooltip_text()` |
| Map doesn't load | Increase timeout in `page.goto()` |
| Filters don't work | Inspect dropdown elements, update `set_map_filters()` |
| Slow scraping | Decrease grid step in canvas mode (but takes longer) |
| Missing counties | Decrease `step_x`/`step_y` in `scrape_canvas_map()` |

## Dependencies

- `playwright` - Browser automation
- `pandas` - Data processing (optional, for analysis)
- Chromium browser (installed via `playwright install chromium`)
