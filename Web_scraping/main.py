import argparse
import json
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from scraper import scrape_existing_deals, scrape_potential_deal, scrape_map_properties


def main():
    parser = argparse.ArgumentParser(description='Selenium scraper for Aequitas frontend')
    parser.add_argument('--base-url', default='https://pe-aequitas.vercel.app/', help='Base URL of the running frontend')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    args = parser.parse_args()

    chrome_options = Options()
    if args.headless:
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    result = {
        'existing_deals': [],
        'potential_deal': {},
        'map_properties': []
    }

    try:
        # Dashboard page - scrape existing deals
        dashboard_url = args.base_url.rstrip('/') + '/'
        driver.get(dashboard_url)
        result['existing_deals'] = scrape_existing_deals(driver, wait)

        # Underwriting page - scrape potential deal
        underwriting_url = args.base_url.rstrip('/') + '/underwriting'
        driver.get(underwriting_url)
        result['potential_deal'] = scrape_potential_deal(driver, wait)

        # Map page - scrape properties
        map_url = args.base_url.rstrip('/') + '/map'
        driver.get(map_url)
        result['map_properties'] = scrape_map_properties(driver, wait)

        # Derive available and potential properties
        available_props = result.get('map_properties', [])
        potential_props = []
        try:
            uw = result.get('potential_deal', {}) or {}
            # try to extract city from underwriting location (e.g. 'Austin, TX')
            loc = (uw.get('location') or '')
            city = ''
            if loc:
                city = loc.split(',')[0].strip().lower()

            # parse purchase price if available
            purchase_price = None
            try:
                pp = uw.get('purchase_price') or uw.get('purchasePrice') or uw.get('purchase_price')
                if pp:
                    purchase_price = int(str(pp).replace(',', '').strip())
            except Exception:
                purchase_price = None

            def parse_price(pstr: str):
                # convert strings like '$625k' or '$1.2M' to integer value in dollars
                if not pstr:
                    return None
                s = str(pstr).strip().replace('$', '').replace(',', '').lower()
                try:
                    if s.endswith('k'):
                        return int(float(s[:-1]) * 1000)
                    if s.endswith('m'):
                        return int(float(s[:-1]) * 1_000_000)
                    return int(float(s))
                except Exception:
                    return None

            for p in available_props:
                added = False
                addr = (p.get('address') or '').lower()
                if city and city in addr:
                    potential_props.append(p)
                    added = True
                if not added and purchase_price is not None:
                    prop_price = parse_price(p.get('price'))
                    if prop_price is not None and prop_price <= purchase_price:
                        potential_props.append(p)
        except Exception:
            potential_props = []

        result['available_properties'] = available_props
        result['potential_properties'] = potential_props

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    # Write separate property files only
    output_dir = Path('Web_scraping')
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        avail_path = output_dir / 'available_properties.json'
        with open(avail_path, 'w', encoding='utf-8') as f:
            json.dump({'properties': result.get('available_properties', [])}, f, indent=2, ensure_ascii=False)
        print(f'Wrote {avail_path}')

        potential_path = output_dir / 'potential_properties.json'
        with open(potential_path, 'w', encoding='utf-8') as f:
            json.dump({'properties': result.get('potential_properties', [])}, f, indent=2, ensure_ascii=False)
        print(f'Wrote {potential_path}')
    except Exception as e:
        print(f'Error writing property files: {e}')


if __name__ == '__main__':
    main()
