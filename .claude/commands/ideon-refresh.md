# Ideon Data Refresh

Re-download fresh data from Ideon and regenerate all CSVs.

## Instructions

1. Navigate to the project and activate the virtual environment:
```bash
cd /Users/gabrielviggers/Downloads/ideon-scraper-repo
source venv/bin/activate
```

2. Delete the cached data to force fresh download:
```bash
rm -f county_data_raw.json
```

3. Re-export county data (this downloads fresh data):
```bash
python scripts/export_county_data.py --year 2026 -o data/ideon_counties_2026.csv
```

4. Re-export state data:
```bash
python scripts/export_state_data.py --year 2026 -o data/ideon_states_2026.csv
```

5. Copy both CSVs to Downloads:
```bash
cp data/ideon_counties_2026.csv data/ideon_states_2026.csv ~/Downloads/
```

6. Run verification to confirm data is accurate:
```bash
python scripts/auto_verify.py
```

7. Tell the user:
   - Fresh data has been downloaded from Ideon
   - County CSV: `~/Downloads/ideon_counties_2026.csv`
   - State CSV: `~/Downloads/ideon_states_2026.csv`
   - Verification status (passed/failed)

$ARGUMENTS
