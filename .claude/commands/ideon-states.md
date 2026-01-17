# Ideon State Data Export

Export state-level aggregated health insurance premium data from Ideon's ICHRA map.

## Instructions

1. Navigate to the project and activate the virtual environment:
```bash
cd /Users/gabrielviggers/Downloads/ideon-scraper-repo
source venv/bin/activate
```

2. Ensure county data is cached first:
```bash
python scripts/export_county_data.py --year 2026 -o /dev/null 2>/dev/null || true
```

3. Run the state export script for 2026 data:
```bash
python scripts/export_state_data.py --year 2026 -o data/ideon_states_2026.csv
```

4. Copy the CSV to Downloads for easy sharing:
```bash
cp data/ideon_states_2026.csv ~/Downloads/
```

5. Tell the user:
   - The file is ready at `~/Downloads/ideon_states_2026.csv`
   - It contains 306 rows (51 states × 3 metals × 2 ages)
   - Columns: state_abbr, state_name, individual_premium_avg, small_group_premium_avg, difference_avg, county_count, year, age, metal_tier

$ARGUMENTS
