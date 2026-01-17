#!/usr/bin/env python3
"""
Ideon Map Inspector
Captures network requests to find the underlying data source.
Run this first to potentially find a direct JSON/API endpoint.

Usage:
    python inspect_network.py
"""

import asyncio
import json
from playwright.async_api import async_playwright

URL = "https://ideonapi.com/ideon-ichra-insights-by-state/"


async def inspect():
    """Capture network requests and look for data sources."""
    print("Starting network inspection...")
    print("=" * 60)
    
    data_urls = []
    json_responses = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible for debugging
        page = await browser.new_page()
        
        # Capture all network responses
        async def handle_response(response):
            url = response.url
            content_type = response.headers.get("content-type", "")
            
            # Look for data files
            if any(x in url.lower() for x in [".json", ".geojson", "api", "data", "county", "premium"]):
                data_urls.append({
                    "url": url,
                    "status": response.status,
                    "content_type": content_type
                })
                print(f"📦 Found: {url[:100]}...")
                
                # Try to capture JSON content
                if "json" in content_type.lower():
                    try:
                        body = await response.json()
                        json_responses.append({
                            "url": url,
                            "data": body,
                            "size": len(str(body))
                        })
                        print(f"   └── JSON data: {len(str(body))} chars")
                    except:
                        pass
        
        page.on("response", handle_response)
        
        print(f"Loading: {URL}")
        await page.goto(URL, wait_until="networkidle", timeout=60000)
        
        # Scroll and interact to trigger lazy loading
        await page.evaluate("window.scrollBy(0, 500)")
        await asyncio.sleep(2)
        
        # Try hovering on the map to trigger data loads
        try:
            canvas = page.locator("canvas").first
            box = await canvas.bounding_box()
            if box:
                # Hover around the map
                for x in range(int(box["x"]), int(box["x"] + box["width"]), 100):
                    await page.mouse.move(x, int(box["y"] + box["height"] / 2))
                    await asyncio.sleep(0.2)
        except:
            pass
        
        await asyncio.sleep(3)
        
        # Print summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        if data_urls:
            print(f"\n📦 Found {len(data_urls)} potential data URLs:\n")
            for item in data_urls:
                print(f"  {item['url']}")
                print(f"    Status: {item['status']}, Type: {item['content_type']}")
        else:
            print("\n⚠️  No obvious data URLs found.")
        
        if json_responses:
            print(f"\n📊 Found {len(json_responses)} JSON responses:\n")
            for item in json_responses:
                print(f"  {item['url'][:80]}...")
                print(f"    Size: {item['size']} chars")
                
                # Save largest JSON for inspection
                if item["size"] > 1000:
                    filename = "captured_data.json"
                    with open(filename, "w") as f:
                        json.dump(item["data"], f, indent=2)
                    print(f"    💾 Saved to {filename}")
        
        # Check page content for embedded data
        print("\n🔍 Checking for embedded data in page...")
        content = await page.content()
        
        # Look for common data patterns
        if "GeoJSON" in content or "geojson" in content:
            print("  Found: GeoJSON reference")
        if "topojson" in content.lower():
            print("  Found: TopoJSON reference")
        if '"features"' in content and '"geometry"' in content:
            print("  Found: Possible embedded GeoJSON features")
        if "county" in content.lower() and "premium" in content.lower():
            print("  Found: County/premium data references")
        
        # List all script sources
        scripts = await page.locator("script[src]").all()
        print(f"\n📜 External scripts ({len(scripts)}):")
        for script in scripts[:10]:  # First 10
            src = await script.get_attribute("src")
            if src:
                print(f"  {src[:80]}...")
        
        input("\nPress Enter to close browser...")
        await browser.close()
    
    return data_urls, json_responses


if __name__ == "__main__":
    asyncio.run(inspect())
