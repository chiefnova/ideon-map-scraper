---
name: ideon-verify
description: Verifies Ideon premium data against the live website by hovering over counties and comparing tooltip values. Use when the user wants to verify data accuracy, check if CSV matches the website, or validate Ideon premium data.
allowed-tools: Bash, Read, Write, Glob
---

# Ideon Data Verification

## What This Does

Automatically verifies our CSV data against the live Ideon website by:
1. Loading the interactive map
2. Setting filters (year, age, metal tier)
3. Hovering over counties to capture tooltip values
4. Comparing captured values against our CSV data

## Instructions

1. **Activate the virtual environment**:
   ```bash
   cd /Users/gabrielviggers/Downloads/ideon-scraper-repo
   source venv/bin/activate
   ```

2. **Ensure data is cached** (required for comparison):
   ```bash
   python scripts/export_county_data.py --year 2026 -o /dev/null
   ```

3. **Run the verification script**:
   ```bash
   python scripts/auto_verify.py
   ```

4. **Report the results** to the user:
   - List of counties checked
   - Side-by-side comparison (Website vs Our CSV)
   - Any mismatches found
   - Overall pass/fail status

## What Gets Verified

The script checks:
- Individual premium values
- Small group premium values
- Difference calculations

Settings used: Year=2026, Age=50, Metal=Gold

## Expected Output

```
County                              Source     Individual  Small Group       Diff
--------------------------------------------------------------------------------
Harris County, TX                   Website       $700.98      $748.60    $-47.62
                                    Our CSV       $700.98      $748.60    $-47.62

Los Angeles County, CA              Website       $617.75      $592.22     $25.53
                                    Our CSV       $617.75      $592.22     $25.53
...
======================================================================
✅ VERIFICATION PASSED - All values match!
```

## Interpreting Results

- **✅ VERIFICATION PASSED**: Data matches the live website
- **⚠️ MISMATCH**: Values differ - may indicate Ideon updated their data
- **NOT FOUND**: County in our data but not captured from website (normal for small samples)

## If Verification Fails

If mismatches are found, the data source may have been updated. Re-run the export:

```bash
# Delete cache to force fresh download
rm county_data_raw.json

# Re-export county data
python scripts/export_county_data.py --year 2026 -o data/ideon_counties_2026.csv

# Re-export state data
python scripts/export_state_data.py --year 2026 -o data/ideon_states_2026.csv

# Verify again
python scripts/auto_verify.py
```

## Notes

- Verification samples ~15-20 random counties (not all 3,143)
- Runs headless (no visible browser)
- The website sometimes hides negative differences as "N/A" in tooltips, but our CSV has the actual values
