#!/usr/bin/env python3
"""
Export Ideon state-level aggregated premium data to CSV.
Aggregates county data by state (mean of all counties).

Usage:
    python export_state_data.py --year 2026 --output states_2026.csv
"""

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

DATA_URL = "https://ideonapi.com/wp-content/uploads/json-data/county_lowest_premiums_all_14-12-2025.json"

# Full state names
STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
    "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
    "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
    "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
    "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", "PR": "Puerto Rico"
}


def load_data(cache_file: Path) -> list:
    """Load data from cache file."""
    if not cache_file.exists():
        print(f"Error: Cache file not found: {cache_file}")
        print("Run export_county_data.py first to download the data.")
        return []

    print(f"Loading from: {cache_file}")
    with open(cache_file) as f:
        return json.load(f)


def aggregate_by_state(data: list, year: int) -> list:
    """Aggregate county data to state level (mean per state/age/metal combo)."""
    year_code = year - 2000

    # Filter to year
    year_data = [r for r in data if r.get("year") == year_code]

    # Group by state + age + metal
    groups = defaultdict(list)
    for row in year_data:
        key = (row.get("st"), row.get("age"), row.get("lvl"))
        groups[key].append(row)

    # Calculate means
    results = []
    for (state, age, metal), rows in groups.items():
        # Filter out None values for each field
        individual_vals = [r["i"] for r in rows if r.get("i") is not None]
        small_group_vals = [r["s"] for r in rows if r.get("s") is not None]
        diff_vals = [r["d"] for r in rows if r.get("d") is not None]

        results.append({
            "state_abbr": state,
            "state_name": STATE_NAMES.get(state, state),
            "age": age,
            "metal_tier": metal.capitalize() if metal else "",
            "individual_premium_avg": round(mean(individual_vals), 2) if individual_vals else None,
            "small_group_premium_avg": round(mean(small_group_vals), 2) if small_group_vals else None,
            "difference_avg": round(mean(diff_vals), 2) if diff_vals else None,
            "county_count": len(rows),
            "year": year
        })

    return results


def export_states_csv(data: list, output_path: str):
    """Export state data to CSV."""
    if not data:
        print("No data to export!")
        return 0

    fieldnames = [
        "state_abbr",
        "state_name",
        "individual_premium_avg",
        "small_group_premium_avg",
        "difference_avg",
        "county_count",
        "year",
        "age",
        "metal_tier"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Sort by state
        sorted_data = sorted(data, key=lambda x: (x.get("state_abbr", ""), x.get("age", 0), x.get("metal_tier", "")))
        writer.writerows(sorted_data)

    return len(sorted_data)


def main():
    parser = argparse.ArgumentParser(description="Export Ideon state-level premium data to CSV")
    parser.add_argument("--year", type=int, default=2026, help="Year (2017-2026)")
    parser.add_argument("--output", "-o", default="ideon_states_2026.csv", help="Output CSV path")
    parser.add_argument("--cache", type=str, default="county_data_raw.json", help="Cache JSON file path")

    args = parser.parse_args()

    # Load data
    data = load_data(Path(args.cache))
    if not data:
        return

    print(f"Total records loaded: {len(data)}")

    # Aggregate by state
    state_data = aggregate_by_state(data, args.year)
    print(f"State-level aggregations: {len(state_data)}")

    # Export
    count = export_states_csv(state_data, args.output)
    print(f"\nExported {count} rows to {args.output}")

    # Summary
    states = len(set(r["state_abbr"] for r in state_data))
    print(f"  States: {states}")


if __name__ == "__main__":
    main()
