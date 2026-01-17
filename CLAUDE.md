# CLAUDE.md - Project Guide for Claude Code

## Project Overview

This project extracts county-level health insurance premium data from Ideon's interactive ICHRA map at https://ideonapi.com/ideon-ichra-insights-by-state/

**Data source discovered**: Direct JSON endpoint (no scraping needed!)
```
https://ideonapi.com/wp-content/uploads/json-data/county_lowest_premiums_all_14-12-2025.json
```

**Coverage**: ~3,143 US counties, years 2017-2026, ages 27/50, metal tiers Bronze/Silver/Gold

## Quick Start - Slash Commands

Business team can use these commands directly in Claude Code:

| Command | What it does |
|---------|--------------|
| `/ideon-counties` | Export all county-level premium data to CSV |
| `/ideon-states` | Export state-level aggregated data to CSV |
| `/ideon-verify` | Verify CSV data against live website |
| `/ideon-refresh` | Re-download fresh data and regenerate all CSVs |

### Example Usage

```
You: /ideon-counties
Claude: [Runs export, creates CSV at ~/Downloads/ideon_counties_2026.csv]

You: /ideon-verify
Claude: [Checks data against live site, reports pass/fail]
```

## File Structure

```
ideon-scraper-repo/
├── .claude/
│   ├── commands/           # Slash commands for business team
│   │   ├── ideon-counties.md
│   │   ├── ideon-states.md
│   │   ├── ideon-verify.md
│   │   └── ideon-refresh.md
│   └── skills/             # Auto-triggered skills
│       ├── ideon-counties/
│       ├── ideon-states/
│       └── ideon-verify/
├── data/                   # Output CSVs (committed to repo)
│   ├── ideon_counties_2026.csv
│   └── ideon_states_2026.csv
├── scripts/
│   ├── export_county_data.py   # Main county export script
│   ├── export_state_data.py    # State aggregation script
│   ├── auto_verify.py          # Automated verification
│   ├── find_data_source.py     # Data source discovery
│   ├── inspect_network.py      # Network inspector
│   └── scrape_ideon_map.py     # Fallback hover scraper
├── references/
│   └── selectors.md
├── requirements.txt
└── CLAUDE.md
```

## Manual Usage

If not using slash commands, run directly:

```bash
cd /Users/gabrielviggers/Downloads/ideon-scraper-repo
source venv/bin/activate

# Export county data
python scripts/export_county_data.py --year 2026 -o data/ideon_counties_2026.csv

# Export state data
python scripts/export_state_data.py --year 2026 -o data/ideon_states_2026.csv

# Verify against live site
python scripts/auto_verify.py
```

### Filtering Options

```bash
# All 2026 data (18,858 rows)
python scripts/export_county_data.py --year 2026

# Just Gold tier, Age 50 (3,143 rows)
python scripts/export_county_data.py --year 2026 --age 50 --metal gold

# Different year
python scripts/export_county_data.py --year 2025
```

## CSV Output Format

### Counties CSV (ideon_counties_2026.csv)

| Column | Description |
|--------|-------------|
| fips | 5-digit FIPS county code |
| county | County name |
| state_abbr | State abbreviation (TX, CA, etc.) |
| state_name | Full state name |
| individual_premium | Monthly individual ACA premium |
| small_group_premium | Monthly small group premium |
| difference | Individual minus Small Group |
| year | Plan year (2017-2026) |
| age | Age for premium (27 or 50) |
| metal_tier | Bronze, Silver, or Gold |

### States CSV (ideon_states_2026.csv)

Same columns but with `_avg` suffix for averaged values, plus `county_count`.

## Data Notes

- **Alaska**: No individual market data (values are null)
- **Negative difference**: Small Group is cheaper than Individual
- **Data freshness**: JSON endpoint is updated periodically by Ideon
- **Verification**: Use `/ideon-verify` to confirm data matches live site

## GitHub Repository

CSVs are committed to the repo for easy download:
- https://github.com/chiefnova/ideon-map-scraper/raw/main/data/ideon_counties_2026.csv
- https://github.com/chiefnova/ideon-map-scraper/raw/main/data/ideon_states_2026.csv

## Dependencies

```bash
pip install playwright pandas
playwright install chromium
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `venv not found` | Run `python3 -m venv venv` first |
| `playwright not installed` | Run `pip install playwright && playwright install chromium` |
| Data seems outdated | Run `/ideon-refresh` to re-download |
| Verification fails | Ideon may have updated data - run `/ideon-refresh` |
