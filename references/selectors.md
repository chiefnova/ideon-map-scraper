# Selector Reference & Troubleshooting

When Ideon updates their map, the CSS selectors may need updating. This guide helps identify the correct selectors.

## Finding Selectors in DevTools

1. Open the Ideon map page in Chrome
2. Right-click on a county → "Inspect"
3. Look for the element structure

## Common Map Libraries & Their Selectors

### Mapbox GL JS (Canvas-based)
```css
.mapboxgl-canvas          /* Main map canvas */
.mapboxgl-popup           /* Tooltip container */
.mapboxgl-popup-content   /* Tooltip text */
```

### Leaflet (SVG-based)
```css
.leaflet-interactive      /* Clickable features */
.leaflet-popup-content    /* Tooltip text */
path.leaflet-interactive  /* County paths */
```

### D3.js (SVG-based)
```css
svg path                  /* All paths */
path[d]                   /* Paths with data */
.county                   /* If classed */
```

### React Simple Maps
```css
.rsm-geography           /* Geographic features */
.rsm-marker              /* Markers */
```

## Tooltip Text Patterns

The tooltip displays data in this format:
```
{County Name}, {State Abbrev}
Diff (Ind - Small): ${difference}
Individual: ${individual}  Small Group: ${small_group}
```

Example:
```
Shasta County, CA
Diff (Ind - Small): $605.64
Individual: $1,414.50  Small Group: $808.86
```

## Updating the Scraper

If selectors change:

1. **Find new tooltip selector**: Hover over a county, inspect the tooltip element
2. **Update `get_tooltip_text()` in scrape_ideon_map.py**: Add new selector to the list
3. **Find new path selector**: Inspect a county shape, note its element type and classes
4. **Update `find_county_elements()` or adjust the scraping method**

## Debugging Tips

```python
# Print all visible tooltips
tooltips = await page.locator("[class*='popup'], [class*='tooltip']").all()
for t in tooltips:
    print(await t.text_content())

# Print page structure
print(await page.content())

# Screenshot for inspection
await page.screenshot(path="debug.png")
```
