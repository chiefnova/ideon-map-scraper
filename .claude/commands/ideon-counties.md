# Ideon County Data Export

Export county-level health insurance premium data from Ideon's ICHRA map.

## Instructions

1. Navigate to the project and activate the virtual environment:
```bash
cd /Users/gabrielviggers/Downloads/ideon-scraper-repo
source venv/bin/activate
```

2. Run the county export script for 2026 data:
```bash
python scripts/export_county_data.py --year 2026 -o data/ideon_counties_2026.csv
```

3. Copy the CSV to Downloads for easy sharing:
```bash
cp data/ideon_counties_2026.csv ~/Downloads/
```

4. Tell the user:
   - The file is ready at `~/Downloads/ideon_counties_2026.csv`
   - It contains ~18,858 rows (3,143 counties × 3 metals × 2 ages)
   - Columns: fips, county, state_abbr, state_name, individual_premium, small_group_premium, difference, year, age, metal_tier

$ARGUMENTS
