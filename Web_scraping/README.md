# Web_scraping — Selenium Scraper

This folder contains a Selenium-based scraper to extract data from the Aequitas AI frontend:

- **Existing Deals** — from Dashboard page (Recent Deals table)
- **Potential Deal** — from Underwriting page (deal parameters & inputs)
- **Map Properties** — from Map page (property listings)

## Quick Start

To get property data quickly:

```powershell
# 1. Start frontend (from project root)
cd frontend
npm run dev

# 2. In a new terminal, run scraper (from project root)
python .\Web_scraping\main.py

# 3. Check output files
Get-Content .\Web_scraping\available_properties.json | ConvertFrom-Json
Get-Content .\Web_scraping\potential_properties.json | ConvertFrom-Json
```

The scraper will create:
- `available_properties.json` — all properties from Map page
- `potential_properties.json` — properties filtered by Underwriting inputs

## Project Structure

- `scraper.py` — Core scraping functions (reusable library)
  - `scrape_existing_deals(driver, wait)` → List of deals from dashboard
  - `scrape_potential_deal(driver, wait)` → Single deal from underwriting
  - `scrape_map_properties(driver, wait)` → Properties from map

- `main.py` — CLI entry point
  - Parses arguments, manages Selenium driver, orchestrates scraping, writes JSON output

- `requirements.txt` — Dependencies (Selenium 4.10+)

## Usage

### 1. Start the frontend dev server (if not running)

```powershell
cd frontend
npm install
npm run dev
```

### 2. Activate Python environment and install dependencies

```powershell
cd Web_scraping
python -m venv .venv  # only first time
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Or just install directly in your main venv:

```powershell
pip install -r Web_scraping\requirements.txt
```

### 3. Run the scraper

Default (saves to `Web_scraping/available_properties.json` and `Web_scraping/potential_properties.json`):
```powershell
python .\Web_scraping\main.py
```

With custom base URL:
```powershell
python .\Web_scraping\main.py --base-url http://localhost:5173 --headless
```

**Arguments:**
- `--base-url` — Base URL of frontend (default: `http://localhost:5173`)
- `--headless` — Run Chrome in headless mode (no visible browser)

## Output Format

The scraper produces two separate JSON files:

### `available_properties.json`
List of properties extracted from the Map page:
```json
{
  "properties": [
    {
      "price": "$625k",
      "address": "1234 Capitol Mall, Sacramento, CA 95814"
    },
    ...
  ]
}
```

### `potential_properties.json`
Subset of properties filtered based on Underwriting inputs (e.g., location city match or purchase price threshold):
```json
{
  "properties": [
    {
      "price": "$625k",
      "address": "Austin, TX"
    },
    ...
  ]
}
```

## Requirements

- Python 3.8+
- Google Chrome (Selenium Manager will auto-download compatible ChromeDriver)
- Frontend running at the specified base URL

## Notes

- The scraper uses Selenium Manager to automatically find/download a matching ChromeDriver.
- If you prefer Firefox or other browsers, update `webdriver.Chrome()` in `main.py`.
- Popups and dynamic content are handled with WebDriverWait for reliable element detection.
- To reuse scraper functions in other scripts, import from `scraper.py`:
  ```python
  from scraper import scrape_existing_deals, scrape_potential_deal, scrape_map_properties
  ```
