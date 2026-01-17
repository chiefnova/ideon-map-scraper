---
name: ideon-counties
description: Fetches and exports Ideon ICHRA county-level health insurance premium data to CSV. Use when the user asks for county premium data, county health insurance data, Ideon county data, or wants to download county-level ACA premiums.
allowed-tools: Bash, Read, Write, Glob
---

# Ideon County Premium Data Export

## What This Does

Fetches county-level health insurance premium data from Ideon's ICHRA map and exports it to CSV. Covers all ~3,143 US counties with Individual vs Small Group ACA plan pricing.

## Data Source

Direct JSON endpoint (no scraping needed):
```
https://ideonapi.com/wp-content/uploads/json-data/county_lowest_premiums_all_14-12-2025.json
```

## Instructions

1. **Activate the virtual environment**:
   ```bash
   cd /Users/gabrielviggers/Downloads/ideon-scraper-repo
   source venv/bin/activate
   ```

2. **Run the export script** with desired filters:
   ```bash
   # All 2026 data (all metals, all ages) - 18,858 rows
   python scripts/export_county_data.py --year 2026 -o data/ideon_counties_2026.csv

   # Filtered: just Gold tier, Age 50
   python scripts/export_county_data.py --year 2026 --age 50 --metal gold -o data/ideon_counties_2026_gold_50.csv
   ```

3. **Report the results** to the user:
   - Number of rows exported
   - Number of unique counties
   - Number of states covered
   - File location

## Available Filters

| Flag | Options | Default | Description |
|------|---------|---------|-------------|
| `--year` | 2017-2026 | 2026 | Plan year |
| `--age` | 27, 50 | (all) | Age for premium calculation |
| `--metal` | bronze, silver, gold | (all) | Metal tier |
| `--output` | filepath | `ideon_county_data.csv` | Output path |

## CSV Output Columns

- `fips` - 5-digit FIPS county code
- `county` - County name
- `state_abbr` - State abbreviation (e.g., TX, CA)
- `state_name` - Full state name
- `individual_premium` - Monthly individual ACA premium
- `small_group_premium` - Monthly small group premium
- `difference` - Individual minus Small Group (positive = individual more expensive)
- `year` - Plan year (2017-2026)
- `age` - Age used for premium (27 or 50)
- `metal_tier` - Bronze, Silver, or Gold

## Example Output

```csv
fips,county,state_abbr,state_name,individual_premium,small_group_premium,difference,year,age,metal_tier
48201,Harris County,TX,Texas,700.98,748.60,-47.62,2026,50,Gold
06037,Los Angeles County,CA,California,617.75,592.22,25.53,2026,50,Gold
```

## Notes

- Alaska counties have no individual market data (shown as empty)
- Data is sorted by state, then county name
- The cache file `county_data_raw.json` speeds up subsequent runs
