#!/usr/bin/env python3
"""
Export Ideon county premium data to CSV.
Fetches data directly from Ideon's JSON endpoint (no scraping needed).

Usage:
    python export_county_data.py --year 2026 --output counties_2026.csv
    python export_county_data.py --year 2026 --age 50 --metal gold --output filtered.csv
"""

import argparse
import csv
import json
import urllib.request
from pathlib import Path

DATA_URL = "https://ideonapi.com/wp-content/uploads/json-data/county_lowest_premiums_all_14-12-2025.json"

# US state FIPS to name mapping
FIPS_TO_STATE = {
    "01": "Alabama", "02": "Alaska", "04": "Arizona", "05": "Arkansas",
    "06": "California", "08": "Colorado", "09": "Connecticut", "10": "Delaware",
    "11": "District of Columbia", "12": "Florida", "13": "Georgia", "15": "Hawaii",
    "16": "Idaho", "17": "Illinois", "18": "Indiana", "19": "Iowa",
    "20": "Kansas", "21": "Kentucky", "22": "Louisiana", "23": "Maine",
    "24": "Maryland", "25": "Massachusetts", "26": "Michigan", "27": "Minnesota",
    "28": "Mississippi", "29": "Missouri", "30": "Montana", "31": "Nebraska",
    "32": "Nevada", "33": "New Hampshire", "34": "New Jersey", "35": "New Mexico",
    "36": "New York", "37": "North Carolina", "38": "North Dakota", "39": "Ohio",
    "40": "Oklahoma", "41": "Oregon", "42": "Pennsylvania", "44": "Rhode Island",
    "45": "South Carolina", "46": "South Dakota", "47": "Tennessee", "48": "Texas",
    "49": "Utah", "50": "Vermont", "51": "Virginia", "53": "Washington",
    "54": "West Virginia", "55": "Wisconsin", "56": "Wyoming", "72": "Puerto Rico"
}


def fetch_data(cache_file: Path = None) -> list:
    """Fetch data from Ideon's JSON endpoint or cache."""
    if cache_file and cache_file.exists():
        print(f"Loading from cache: {cache_file}")
        with open(cache_file) as f:
            return json.load(f)

    print(f"Fetching data from {DATA_URL}...")
    with urllib.request.urlopen(DATA_URL, timeout=60) as response:
        data = json.loads(response.read().decode())

    if cache_file:
        print(f"Caching to: {cache_file}")
        with open(cache_file, "w") as f:
            json.dump(data, f)

    return data


def filter_data(data: list, year: int = None, age: int = None, metal: str = None) -> list:
    """Filter data by year, age, and/or metal tier."""
    filtered = data

    if year:
        year_code = year - 2000  # 2026 -> 26
        filtered = [r for r in filtered if r.get("year") == year_code]

    if age:
        filtered = [r for r in filtered if r.get("age") == age]

    if metal:
        filtered = [r for r in filtered if r.get("lvl", "").lower() == metal.lower()]

    return filtered


def export_counties_csv(data: list, output_path: str):
    """Export county data to CSV."""
    if not data:
        print("No data to export!")
        return 0

    fieldnames = [
        "fips",
        "county",
        "state_abbr",
        "state_name",
        "individual_premium",
        "small_group_premium",
        "difference",
        "year",
        "age",
        "metal_tier"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        # Sort by state, then county
        sorted_data = sorted(data, key=lambda x: (x.get("st", ""), x.get("n", "")))

        for row in sorted_data:
            fips = row.get("f", "")
            state_fips = fips[:2] if len(fips) >= 2 else ""

            writer.writerow({
                "fips": fips,
                "county": row.get("n", ""),
                "state_abbr": row.get("st", ""),
                "state_name": FIPS_TO_STATE.get(state_fips, ""),
                "individual_premium": row.get("i"),
                "small_group_premium": row.get("s"),
                "difference": row.get("d"),
                "year": 2000 + row.get("year", 0),
                "age": row.get("age"),
                "metal_tier": row.get("lvl", "").capitalize()
            })

    return len(sorted_data)


def main():
    parser = argparse.ArgumentParser(description="Export Ideon county premium data to CSV")
    parser.add_argument("--year", type=int, default=2026, help="Year (2017-2026)")
    parser.add_argument("--age", type=int, choices=[27, 50], help="Age filter (27 or 50)")
    parser.add_argument("--metal", choices=["bronze", "silver", "gold"], help="Metal tier filter")
    parser.add_argument("--output", "-o", default="ideon_counties_2026.csv", help="Output CSV path")
    parser.add_argument("--cache", type=str, help="Cache JSON file path")
    parser.add_argument("--all-combinations", action="store_true",
                        help="Export all age/metal combinations (separate rows)")

    args = parser.parse_args()

    # Fetch data
    cache_path = Path(args.cache) if args.cache else Path("county_data_raw.json")
    data = fetch_data(cache_path)
    print(f"Total records loaded: {len(data)}")

    # Filter data
    filtered = filter_data(data, year=args.year, age=args.age, metal=args.metal)
    print(f"Records after filtering (year={args.year}, age={args.age}, metal={args.metal}): {len(filtered)}")

    # Export
    count = export_counties_csv(filtered, args.output)
    print(f"\nExported {count} rows to {args.output}")

    # Summary stats
    if filtered:
        states = len(set(r.get("st") for r in filtered))
        counties = len(set(r.get("f") for r in filtered))
        print(f"  States: {states}")
        print(f"  Unique counties (FIPS): {counties}")


if __name__ == "__main__":
    main()
