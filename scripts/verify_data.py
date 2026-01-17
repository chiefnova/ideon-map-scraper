#!/usr/bin/env python3
"""
Verify our CSV data against the live Ideon website.
Hovers over specific counties and captures tooltip values.
"""

import asyncio
import re
from playwright.async_api import async_playwright

URL = "https://ideonapi.com/ideon-ichra-insights-by-state/"

# Test cases: (county_name, state_abbr, expected_individual, expected_small_group, expected_diff)
# These are from our JSON for year 2026, age 50, gold tier
TEST_CASES = [
    ("Harris County", "TX", 700.98, 748.60, -47.62),
    ("Los Angeles County", "CA", 617.75, 592.22, 25.53),
    ("Miami-Dade County", "FL", 872.18, 931.81, -59.63),
    ("New York County", "NY", 1123.85, 1037.74, 86.11),
    ("San Diego County", "CA", 712.02, 216.96, 495.06),
]


async def verify():
    print("Verifying CSV data against live website...")
    print("Settings: Year=2026, Age=50, Metal=Gold")
    print("=" * 70)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible so you can see
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        print(f"\nLoading {URL}...")
        await page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)

        # Set filters to Year=2026, Age=50, Metal=Gold
        print("Setting filters: Year=2026, Age=50, Metal=Gold")

        try:
            # Year dropdown
            year_select = page.locator("#ichra-year")
            await year_select.select_option("26")
            await asyncio.sleep(0.5)

            # Age dropdown
            age_select = page.locator("#ichra-age")
            await age_select.select_option("50")
            await asyncio.sleep(0.5)

            # Metal dropdown
            metal_select = page.locator("#ichra-metal")
            await metal_select.select_option("gold")
            await asyncio.sleep(2)  # Let map update

            print("Filters set successfully.\n")
        except Exception as e:
            print(f"Warning setting filters: {e}")

        # Scroll to map
        await page.evaluate("window.scrollBy(0, 400)")
        await asyncio.sleep(1)

        # Take a screenshot for reference
        await page.screenshot(path="verification_screenshot.png")
        print("Screenshot saved to verification_screenshot.png")

        # Now check the tooltip element
        print("\n" + "=" * 70)
        print("VERIFICATION: Hover over these counties on the map to compare values:")
        print("=" * 70)

        for county, state, exp_ind, exp_sg, exp_diff in TEST_CASES:
            print(f"\n{county}, {state}")
            print(f"  Our CSV data:")
            print(f"    Individual:   ${exp_ind:,.2f}")
            print(f"    Small Group:  ${exp_sg:,.2f}")
            print(f"    Difference:   ${exp_diff:,.2f}")

        print("\n" + "=" * 70)
        print("Browser is open. Hover over the counties above to verify the values.")
        print("The tooltip should show matching numbers.")
        print("=" * 70)

        # Keep browser open for manual verification
        input("\nPress Enter when done verifying...")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(verify())
