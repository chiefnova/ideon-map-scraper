#!/usr/bin/env python3
"""
Automated verification: hovers over map and captures tooltip data.
Compares against our CSV values.
"""

import asyncio
import re
from playwright.async_api import async_playwright

URL = "https://ideonapi.com/ideon-ichra-insights-by-state/"


def parse_tooltip(text: str) -> dict:
    """Parse tooltip text into values."""
    if not text:
        return None

    # Normalize
    text = " ".join(text.split())

    # Pattern: "County, ST Diff (Ind − Small): $X Individual: $Y Small Group: $Z"
    county_match = re.search(r"([^,]+),\s*([A-Z]{2})", text)
    diff_match = re.search(r"Diff[^:]*:\s*\$?([-\d,]+\.?\d*)", text)
    ind_match = re.search(r"Individual:\s*\$?([\d,]+\.?\d*)", text)
    sg_match = re.search(r"Small\s*Group:\s*\$?([\d,]+\.?\d*)", text)

    if county_match:
        return {
            "county": county_match.group(1).strip(),
            "state": county_match.group(2).strip(),
            "difference": float(diff_match.group(1).replace(",", "")) if diff_match else None,
            "individual": float(ind_match.group(1).replace(",", "")) if ind_match else None,
            "small_group": float(sg_match.group(1).replace(",", "")) if sg_match else None,
        }
    return None


async def get_tooltip(page) -> str:
    """Get current tooltip text."""
    try:
        tip = page.locator("#ichra-tip")
        if await tip.is_visible():
            return await tip.text_content()
    except:
        pass
    return None


async def verify():
    print("Automated verification against live website")
    print("Settings: Year=2026, Age=50, Metal=Gold")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        print(f"\nLoading page...")
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(4)

        # Set filters
        print("Setting filters...")
        await page.locator("#ichra-year").select_option("26")
        await asyncio.sleep(0.3)
        await page.locator("#ichra-age").select_option("50")
        await asyncio.sleep(0.3)
        await page.locator("#ichra-metal").select_option("gold")
        await asyncio.sleep(2)

        # Scroll to map
        await page.evaluate("window.scrollBy(0, 350)")
        await asyncio.sleep(1)

        # Find the map container
        map_div = page.locator("#ichra-map")
        box = await map_div.bounding_box()

        if not box:
            print("ERROR: Could not find map")
            await browser.close()
            return

        print(f"Map found at {box['width']:.0f}x{box['height']:.0f}")
        print("\nScanning map for sample counties...")
        print("=" * 70)

        # Collect some samples by scanning the map
        found_counties = {}
        step = 15  # pixels

        for y in range(int(box["y"] + 20), int(box["y"] + box["height"] - 20), step):
            for x in range(int(box["x"] + 20), int(box["x"] + box["width"] - 20), step):
                await page.mouse.move(x, y)
                await asyncio.sleep(0.03)

                tooltip_text = await get_tooltip(page)
                if tooltip_text:
                    data = parse_tooltip(tooltip_text)
                    if data and data["county"]:
                        key = f"{data['county']}, {data['state']}"
                        if key not in found_counties:
                            found_counties[key] = data
                            # Stop after finding enough samples
                            if len(found_counties) >= 20:
                                break
            if len(found_counties) >= 20:
                break

        print(f"\nCaptured {len(found_counties)} unique counties from website:\n")

        # Now compare with our JSON
        import json
        with open("county_data_raw.json") as f:
            our_data = json.load(f)

        # Build lookup for year=26, age=50, metal=gold
        our_lookup = {}
        for r in our_data:
            if r["year"] == 26 and r["age"] == 50 and r["lvl"] == "gold":
                key = f"{r['n']}, {r['st']}"
                our_lookup[key] = r

        print(f"{'County':<35} {'Source':<8} {'Individual':>12} {'Small Group':>12} {'Diff':>10}")
        print("-" * 80)

        mismatches = 0
        for key, web_data in sorted(found_counties.items())[:15]:
            our_record = our_lookup.get(key)

            # Print website values
            web_ind = f"${web_data['individual']:,.2f}" if web_data['individual'] else "N/A"
            web_sg = f"${web_data['small_group']:,.2f}" if web_data['small_group'] else "N/A"
            web_diff = f"${web_data['difference']:,.2f}" if web_data['difference'] else "N/A"
            print(f"{key:<35} {'Website':<8} {web_ind:>12} {web_sg:>12} {web_diff:>10}")

            if our_record:
                our_ind = f"${our_record['i']:,.2f}" if our_record['i'] else "N/A"
                our_sg = f"${our_record['s']:,.2f}" if our_record['s'] else "N/A"
                our_diff = f"${our_record['d']:,.2f}" if our_record['d'] else "N/A"
                print(f"{'':<35} {'Our CSV':<8} {our_ind:>12} {our_sg:>12} {our_diff:>10}")

                # Check for mismatch
                if web_data['individual'] and our_record['i']:
                    if abs(web_data['individual'] - our_record['i']) > 0.01:
                        print(f"{'':<35} ⚠️  MISMATCH on Individual!")
                        mismatches += 1
                if web_data['small_group'] and our_record['s']:
                    if abs(web_data['small_group'] - our_record['s']) > 0.01:
                        print(f"{'':<35} ⚠️  MISMATCH on Small Group!")
                        mismatches += 1
            else:
                print(f"{'':<35} {'Our CSV':<8} {'NOT FOUND':>12}")
                mismatches += 1

            print()

        await browser.close()

        print("=" * 70)
        if mismatches == 0:
            print("✅ VERIFICATION PASSED - All values match!")
        else:
            print(f"⚠️  Found {mismatches} mismatches")

        return mismatches == 0


if __name__ == "__main__":
    asyncio.run(verify())
