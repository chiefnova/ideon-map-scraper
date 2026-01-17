#!/usr/bin/env python3
"""
Ideon ICHRA Map Scraper
Extracts county-level premium data from Ideon's interactive map.

Usage:
    python scrape_ideon_map.py --year 2026 --age 50 --metal gold --output data.csv
"""

import argparse
import asyncio
import csv
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Error: playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)


URL = "https://ideonapi.com/ideon-ichra-insights-by-state/"

# Tooltip parsing pattern - matches format like:
# "Shasta County, CA\nDiff (Ind - Small): $605.64\nIndividual: $1,414.50  Small Group: $808.86"
TOOLTIP_PATTERN = re.compile(
    r"(?P<county>[^,]+),\s*(?P<state>[A-Z]{2})\s*"
    r"Diff\s*\(Ind\s*[-–]\s*Small\):\s*\$?(?P<diff>[\d,.-]+)\s*"
    r"Individual:\s*\$?(?P<individual>[\d,.-]+)\s*"
    r"Small\s*Group:\s*\$?(?P<small_group>[\d,.-]+)",
    re.IGNORECASE | re.DOTALL
)


def parse_money(value: str) -> float:
    """Convert money string to float."""
    if not value:
        return None
    cleaned = value.replace(",", "").replace("$", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def parse_tooltip(text: str) -> dict | None:
    """Parse tooltip text into structured data."""
    if not text:
        return None
    
    # Normalize whitespace
    text = " ".join(text.split())
    
    match = TOOLTIP_PATTERN.search(text)
    if match:
        return {
            "county": match.group("county").strip(),
            "state": match.group("state").strip(),
            "individual_premium": parse_money(match.group("individual")),
            "small_group_premium": parse_money(match.group("small_group")),
            "difference": parse_money(match.group("diff")),
        }
    
    # Fallback: try simpler pattern
    # Format: "County Name, ST" followed by numbers
    simple = re.search(r"([^,]+),\s*([A-Z]{2})", text)
    if simple:
        numbers = re.findall(r"\$?([\d,]+\.?\d*)", text)
        if len(numbers) >= 2:
            return {
                "county": simple.group(1).strip(),
                "state": simple.group(2).strip(),
                "individual_premium": parse_money(numbers[-2]) if len(numbers) >= 2 else None,
                "small_group_premium": parse_money(numbers[-1]) if len(numbers) >= 1 else None,
                "difference": parse_money(numbers[0]) if len(numbers) >= 3 else None,
            }
    
    return None


async def set_map_filters(page, year: int, age: int, metal: str):
    """Set the year, age, and metal dropdowns on the map."""
    print(f"Setting filters: Year={year}, Age={age}, Metal={metal}")
    
    # Wait for the map container to load
    await page.wait_for_selector("text=Individual vs Small Group", timeout=30000)
    await asyncio.sleep(2)  # Let dropdowns initialize
    
    # Find and set Year dropdown
    try:
        year_select = page.locator("select").filter(has_text=str(year)).first
        if await year_select.count() == 0:
            # Try finding by nearby label
            year_select = page.locator("select").nth(0)
        await year_select.select_option(str(year))
        await asyncio.sleep(0.5)
    except Exception as e:
        print(f"Warning: Could not set year filter: {e}")
    
    # Find and set Age dropdown
    try:
        age_select = page.locator("select").nth(1)
        await age_select.select_option(str(age))
        await asyncio.sleep(0.5)
    except Exception as e:
        print(f"Warning: Could not set age filter: {e}")
    
    # Find and set Metal dropdown
    try:
        metal_select = page.locator("select").nth(2)
        await metal_select.select_option(metal.capitalize())
        await asyncio.sleep(0.5)
    except Exception as e:
        print(f"Warning: Could not set metal filter: {e}")
    
    # Wait for map to update
    await asyncio.sleep(2)


async def find_county_elements(page) -> list:
    """Find all county path elements in the map."""
    # Common selectors for choropleth maps (Mapbox, Leaflet, D3, etc.)
    selectors = [
        "path[class*='county']",
        "path[class*='feature']",
        "path[d]",  # Any SVG path
        ".leaflet-interactive",
        "[class*='mapbox'] path",
        "svg path",
        "canvas",  # Mapbox GL uses canvas
    ]
    
    for selector in selectors:
        elements = await page.locator(selector).all()
        if len(elements) > 100:  # Likely found county paths
            print(f"Found {len(elements)} elements with selector: {selector}")
            return elements
    
    # If no paths found, the map might be canvas-based (Mapbox GL)
    return []


async def get_tooltip_text(page) -> str | None:
    """Extract text from any visible tooltip."""
    # Common tooltip selectors
    tooltip_selectors = [
        ".mapboxgl-popup-content",
        ".leaflet-popup-content", 
        "[class*='tooltip']",
        "[class*='Tooltip']",
        "[role='tooltip']",
        ".popup",
        "[class*='popup']",
        "[class*='info-box']",
        "[class*='hover']",
    ]
    
    for selector in tooltip_selectors:
        try:
            tooltip = page.locator(selector).first
            if await tooltip.is_visible():
                text = await tooltip.text_content()
                if text and ("$" in text or "Individual" in text or "Small Group" in text):
                    return text
        except:
            continue
    
    return None


async def scrape_svg_map(page, args) -> list[dict]:
    """Scrape data from SVG-based map by hovering over paths."""
    results = []
    seen = set()
    
    paths = await page.locator("svg path[d]").all()
    paths = [p for p in paths if await p.bounding_box()]  # Filter visible paths
    
    print(f"Found {len(paths)} SVG paths to process")
    
    for i, path in enumerate(paths):
        try:
            box = await path.bounding_box()
            if not box or box["width"] < 2 or box["height"] < 2:
                continue
            
            # Hover over center of path
            await path.hover(force=True, timeout=1000)
            await asyncio.sleep(0.15)
            
            # Get tooltip
            tooltip_text = await get_tooltip_text(page)
            if tooltip_text:
                data = parse_tooltip(tooltip_text)
                if data:
                    key = f"{data['county']}, {data['state']}"
                    if key not in seen:
                        seen.add(key)
                        data["year"] = args.year
                        data["age"] = args.age
                        data["metal"] = args.metal
                        results.append(data)
                        
                        if len(results) % 100 == 0:
                            print(f"  Scraped {len(results)} counties...")
            
            if args.debug and i % 50 == 0:
                print(f"  Progress: {i}/{len(paths)} paths checked, {len(results)} counties found")
                
        except PlaywrightTimeout:
            continue
        except Exception as e:
            if args.debug:
                print(f"  Error on path {i}: {e}")
            continue
    
    return results


async def scrape_canvas_map(page, args) -> list[dict]:
    """Scrape data from canvas-based map (Mapbox GL) using coordinate grid."""
    results = []
    seen = set()
    
    # Find the map canvas
    canvas = page.locator("canvas").first
    box = await canvas.bounding_box()
    
    if not box:
        print("Error: Could not find map canvas")
        return results
    
    print(f"Map canvas found: {box['width']}x{box['height']}")
    
    # Create a grid of points to hover over
    # Denser grid = more complete but slower
    step_x = 8  # pixels between hover points
    step_y = 8
    
    total_points = int((box["width"] / step_x) * (box["height"] / step_y))
    print(f"Scanning {total_points} points across map...")
    
    points_checked = 0
    
    for y in range(int(box["y"]), int(box["y"] + box["height"]), step_y):
        for x in range(int(box["x"]), int(box["x"] + box["width"]), step_x):
            try:
                await page.mouse.move(x, y)
                await asyncio.sleep(0.05)  # Brief pause for tooltip to appear
                
                tooltip_text = await get_tooltip_text(page)
                if tooltip_text:
                    data = parse_tooltip(tooltip_text)
                    if data:
                        key = f"{data['county']}, {data['state']}"
                        if key not in seen:
                            seen.add(key)
                            data["year"] = args.year
                            data["age"] = args.age
                            data["metal"] = args.metal
                            results.append(data)
                            
                            if len(results) % 50 == 0:
                                print(f"  Found {len(results)} unique counties...")
                
                points_checked += 1
                if points_checked % 5000 == 0:
                    print(f"  Scanned {points_checked}/{total_points} points, found {len(results)} counties")
                    
            except Exception as e:
                if args.debug:
                    print(f"  Error at ({x},{y}): {e}")
                continue
    
    return results


async def scrape_map(args):
    """Main scraping function."""
    print(f"\n{'='*60}")
    print(f"Ideon ICHRA Map Scraper")
    print(f"{'='*60}")
    print(f"URL: {URL}")
    print(f"Parameters: Year={args.year}, Age={args.age}, Metal={args.metal}")
    print(f"Output: {args.output}")
    print(f"{'='*60}\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=not args.debug,
            args=["--disable-web-security"]  # Help with some CORS issues
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        
        page = await context.new_page()
        
        print("Loading page...")
        await page.goto(URL, wait_until="networkidle", timeout=60000)
        print("Page loaded.")
        
        # Set filters
        await set_map_filters(page, args.year, args.age, args.metal)
        
        # Scroll to map section
        await page.evaluate("window.scrollBy(0, 400)")
        await asyncio.sleep(1)
        
        # Determine map type and scrape accordingly
        svg_paths = await page.locator("svg path[d]").count()
        canvas_elements = await page.locator("canvas").count()
        
        print(f"Detected: {svg_paths} SVG paths, {canvas_elements} canvas elements")
        
        if svg_paths > 100:
            print("Using SVG scraping method...")
            results = await scrape_svg_map(page, args)
        elif canvas_elements > 0:
            print("Using canvas/Mapbox scraping method...")
            results = await scrape_canvas_map(page, args)
        else:
            print("Warning: Could not detect map type. Trying both methods...")
            results = await scrape_svg_map(page, args)
            if len(results) < 50:
                results = await scrape_canvas_map(page, args)
        
        await browser.close()
        
        return results


def write_csv(results: list[dict], output_path: str):
    """Write results to CSV file."""
    if not results:
        print("No data to write!")
        return
    
    fieldnames = [
        "county", "state", "fips", "individual_premium", 
        "small_group_premium", "difference", "year", "age", "metal"
    ]
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        
        # Sort by state, then county
        sorted_results = sorted(results, key=lambda x: (x.get("state", ""), x.get("county", "")))
        writer.writerows(sorted_results)
    
    print(f"\nWrote {len(results)} rows to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Ideon ICHRA map for county premium data"
    )
    parser.add_argument("--year", type=int, default=2026, 
                        help="Plan year (2017-2026)")
    parser.add_argument("--age", type=int, default=50, choices=[27, 50],
                        help="Age for premium calculation")
    parser.add_argument("--metal", type=str, default="gold",
                        choices=["bronze", "silver", "gold"],
                        help="Metal tier")
    parser.add_argument("--output", "-o", type=str, default="ideon_county_data.csv",
                        help="Output CSV file path")
    parser.add_argument("--state", type=str, default=None,
                        help="Filter to single state (e.g., TX, CA)")
    parser.add_argument("--debug", action="store_true",
                        help="Show browser and verbose output")
    
    args = parser.parse_args()
    
    # Run scraper
    start_time = datetime.now()
    results = asyncio.run(scrape_map(args))
    
    # Filter by state if requested
    if args.state:
        results = [r for r in results if r.get("state", "").upper() == args.state.upper()]
        print(f"Filtered to {len(results)} counties in {args.state.upper()}")
    
    # Write output
    write_csv(results, args.output)
    
    elapsed = datetime.now() - start_time
    print(f"\nCompleted in {elapsed.total_seconds():.1f} seconds")
    print(f"Found {len(results)} unique counties")


if __name__ == "__main__":
    main()
