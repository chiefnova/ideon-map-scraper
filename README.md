# Ideon ICHRA Map Scraper

Extracts county-level health insurance premium data from [Ideon's interactive ICHRA map](https://ideonapi.com/ideon-ichra-insights-by-state/).

## Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/ideon-map-scraper.git
cd ideon-map-scraper

# Install dependencies
pip install playwright pandas
playwright install chromium
```

## Quick Start

### Step 1: Find the data source (recommended)

First, run the network inspector to see if there's a direct JSON endpoint:

```bash
python scripts/inspect_network.py
```

This opens a browser and captures network requests. If it finds a JSON data source, you can fetch it directly instead of scraping.

### Step 2: Run the scraper

```bash
# Test on one state first
python scripts/scrape_ideon_map.py --state CA --debug

# Full scrape (takes 15-20 min for all ~3,100 counties)
python scripts/scrape_ideon_map.py --year 2026 --age 50 --metal gold --output county_data.csv
```

## Options

| Flag | Options | Default | Description |
|------|---------|---------|-------------|
| `--year` | 2017-2026 | 2026 | Plan year |
| `--age` | 27, 50 | 50 | Age for premium calculation |
| `--metal` | bronze, silver, gold | gold | Metal tier |
| `--output` | filepath | `ideon_county_data.csv` | Output CSV path |
| `--state` | state code | (all) | Scrape single state only |
| `--debug` | flag | False | Show browser window |

## Output

CSV with columns:
- `county` - County name
- `state` - State abbreviation
- `individual_premium` - Monthly individual ACA premium
- `small_group_premium` - Monthly small group premium  
- `difference` - Individual minus Small Group
- `year`, `age`, `metal` - Query parameters

## Troubleshooting

See `references/selectors.md` if the map structure changes and selectors need updating.
