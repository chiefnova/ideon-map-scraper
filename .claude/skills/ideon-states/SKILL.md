---
name: ideon-states
description: Fetches and exports Ideon ICHRA state-level aggregated health insurance premium data to CSV. Use when the user asks for state premium data, state-level health insurance data, Ideon state data, or wants state averages for ACA premiums.
allowed-tools: Bash, Read, Write, Glob
---

# Ideon State Premium Data Export

## What This Does

Fetches state-level aggregated health insurance premium data from Ideon's ICHRA map and exports it to CSV. Averages county data across each state for all 51 states/territories.

## Data Source

Aggregated from county-level JSON endpoint:
```
https://ideonapi.com/wp-content/uploads/json-data/county_lowest_premiums_all_14-12-2025.json
```

## Instructions

1. **Activate the virtual environment**:
   ```bash
   cd /Users/gabrielviggers/Downloads/ideon-scraper-repo
   source venv/bin/activate
   ```

2. **Ensure county data is cached** (run county export first if needed):
   ```bash
   # This downloads and caches the raw data
   python scripts/export_county_data.py --year 2026 -o /dev/null
   ```

3. **Run the state export script** with date-stamped filename:
   ```bash
   # Creates file like: ideon_states_2026_2026-01-16.csv
   python scripts/export_state_data.py --year 2026 -o data/ideon_states_2026_$(date +%Y-%m-%d).csv
   ```

4. **Report the results** to the user:
   - Number of rows exported (should be 306 = 51 states × 6 combos)
   - File location

## Available Filters

| Flag | Options | Default | Description |
|------|---------|---------|-------------|
| `--year` | 2017-2026 | 2026 | Plan year |
| `--output` | filepath | `ideon_states_2026.csv` | Output path |
| `--cache` | filepath | `county_data_raw.json` | Source data file |

## CSV Output Columns

- `state_abbr` - State abbreviation (e.g., TX, CA)
- `state_name` - Full state name
- `individual_premium_avg` - Average monthly individual premium across all counties
- `small_group_premium_avg` - Average monthly small group premium across all counties
- `difference_avg` - Average difference (Individual - Small Group)
- `county_count` - Number of counties in that state
- `year` - Plan year
- `age` - Age used for premium (27 or 50)
- `metal_tier` - Bronze, Silver, or Gold

## Example Output

```csv
state_abbr,state_name,individual_premium_avg,small_group_premium_avg,difference_avg,county_count,year,age,metal_tier
TX,Texas,683.45,712.30,-28.85,254,2026,50,Gold
CA,California,645.22,498.67,146.55,58,2026,50,Gold
```

## Notes

- State averages are simple means across all counties (not population-weighted)
- Alaska has no individual market data (shown as empty for individual premium)
- Each state has 6 rows: 3 metal tiers × 2 age groups
