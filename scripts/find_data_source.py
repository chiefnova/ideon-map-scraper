#!/usr/bin/env python3
"""
Quick script to find where the premium data lives.
Fetches page source and looks for embedded data structures.
"""

import asyncio
import json
import re
from playwright.async_api import async_playwright

URL = "https://ideonapi.com/ideon-ichra-insights-by-state/"

async def find_data():
    print("Looking for embedded premium data...")

    all_json_responses = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Capture ALL responses
        async def capture_response(response):
            url = response.url
            content_type = response.headers.get("content-type", "")

            if "json" in content_type.lower() or url.endswith(".json"):
                try:
                    body = await response.json()
                    size = len(json.dumps(body))
                    all_json_responses.append({
                        "url": url,
                        "size": size,
                        "data": body
                    })
                    print(f"  JSON: {url[:80]}... ({size} chars)")
                except:
                    pass

        page.on("response", capture_response)

        print(f"Loading page (30s timeout)...")
        try:
            await page.goto(URL, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(5)  # Let JS execute
        except Exception as e:
            print(f"Page load issue (continuing): {e}")

        # Get page HTML
        print("\nExtracting page source...")
        html = await page.content()

        # Look for large data objects in script tags
        print("\nSearching for embedded data patterns...")

        # Pattern 1: Look for county/premium data arrays
        patterns = [
            (r'countyData\s*[=:]\s*(\[[\s\S]{1000,}?\])', "countyData array"),
            (r'premiumData\s*[=:]\s*(\{[\s\S]{1000,}?\})', "premiumData object"),
            (r'"Individual":\s*[\d.]+', "Individual premium values"),
            (r'"Small Group":\s*[\d.]+', "Small Group premium values"),
            (r'FIPS|fips', "FIPS code references"),
            (r'\d{5}.*?Individual.*?Small\s*Group', "County data rows"),
        ]

        for pattern, name in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f"  ✓ Found: {name} ({len(matches)} matches)")
                if len(matches) <= 3:
                    for m in matches[:3]:
                        preview = str(m)[:200] if isinstance(m, str) else str(m)
                        print(f"    Preview: {preview}...")

        # Look for inline script content with data
        scripts = re.findall(r'<script[^>]*>([\s\S]*?)</script>', html)
        print(f"\nFound {len(scripts)} inline scripts")

        data_scripts = []
        for i, script in enumerate(scripts):
            if len(script) > 5000:  # Large scripts likely have data
                # Check if it has county/premium related content
                if any(kw in script.lower() for kw in ['county', 'premium', 'individual', 'small group', 'fips']):
                    data_scripts.append((i, len(script), script[:500]))
                    print(f"  Script #{i}: {len(script)} chars - likely has data")

        # Save the largest data script for inspection
        if data_scripts:
            largest = max(data_scripts, key=lambda x: x[1])
            with open("largest_script.txt", "w") as f:
                f.write(scripts[largest[0]])
            print(f"\nSaved largest data script to largest_script.txt")

        # Also check for data in window object
        print("\nChecking window object for data...")
        try:
            window_keys = await page.evaluate("""() => {
                const keys = Object.keys(window).filter(k => {
                    try {
                        const val = window[k];
                        if (typeof val === 'object' && val !== null) {
                            const str = JSON.stringify(val);
                            return str && str.length > 1000 &&
                                   (str.includes('county') || str.includes('premium') ||
                                    str.includes('Individual') || str.includes('Small'));
                        }
                    } catch(e) {}
                    return false;
                });
                return keys;
            }""")
            if window_keys:
                print(f"  Found data objects: {window_keys}")
                for key in window_keys[:5]:
                    try:
                        data = await page.evaluate(f"() => JSON.stringify(window['{key}']).slice(0, 500)")
                        print(f"    {key}: {data}...")
                    except:
                        pass
        except Exception as e:
            print(f"  Error checking window: {e}")

        # Save all captured JSON
        print(f"\n{'='*60}")
        print(f"CAPTURED JSON RESPONSES: {len(all_json_responses)}")
        print("="*60)

        for item in sorted(all_json_responses, key=lambda x: x['size'], reverse=True)[:10]:
            print(f"\n{item['url'][:80]}")
            print(f"  Size: {item['size']} chars")

            # Save if it's large and might be county data
            if item['size'] > 10000:
                filename = f"captured_{item['url'].split('/')[-1][:30]}.json"
                with open(filename, "w") as f:
                    json.dump(item['data'], f, indent=2)
                print(f"  Saved to: {filename}")

        await browser.close()

        # Save full HTML for inspection
        with open("page_source.html", "w") as f:
            f.write(html)
        print(f"\nSaved full page source to page_source.html ({len(html)} chars)")

if __name__ == "__main__":
    asyncio.run(find_data())
