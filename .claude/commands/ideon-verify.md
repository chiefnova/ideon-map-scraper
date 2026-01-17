# Ideon Data Verification

Verify our CSV data against the live Ideon website to ensure accuracy.

## Instructions

1. Navigate to the project and activate the virtual environment:
```bash
cd /Users/gabrielviggers/Downloads/ideon-scraper-repo
source venv/bin/activate
```

2. Ensure data is cached:
```bash
python scripts/export_county_data.py --year 2026 -o /dev/null 2>/dev/null || true
```

3. Run the verification script:
```bash
python scripts/auto_verify.py
```

4. Report the results to the user:
   - Show the comparison table (Website vs Our CSV)
   - Highlight any mismatches
   - Confirm if verification passed or failed

5. If verification fails (mismatches found), offer to refresh the data:
```bash
rm county_data_raw.json
python scripts/export_county_data.py --year 2026 -o data/ideon_counties_2026.csv
python scripts/export_state_data.py --year 2026 -o data/ideon_states_2026.csv
```

$ARGUMENTS
