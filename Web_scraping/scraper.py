"""Selenium-based web scraper for Aequitas frontend."""

import time
from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC


def scrape_map_properties(driver, wait: WebDriverWait) -> List[Dict]:
    """Scrape property markers from the Map page."""
    props = []

    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.custom-marker')))
        markers = driver.find_elements(By.CSS_SELECTOR, '.custom-marker')

        for m in markers:
            try:
                price_text = m.text.strip()
                # Click marker to open popup
                try:
                    driver.execute_script('arguments[0].scrollIntoView(true);', m)
                    m.click()
                except Exception:
                    pass

                time.sleep(0.3)
                address = ''
                try:
                    popup = driver.find_element(By.CSS_SELECTOR, '.leaflet-popup-content')
                    popup_text = popup.text.strip()
                    lines = [ln.strip() for ln in popup_text.splitlines() if ln.strip()]
                    if len(lines) >= 2:
                        address = lines[1]
                    elif len(lines) == 1:
                        address = lines[0]
                except Exception:
                    address = ''

                props.append({'price': price_text, 'address': address})
            except Exception:
                continue
    except Exception:
        pass

    return props


def scrape_existing_deals(driver, wait: WebDriverWait) -> List[Dict]:
    """Scrape existing deals from the Dashboard Recent Deals table."""
    deals = []
    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tbody > tr')))
        deal_rows = driver.find_elements(By.CSS_SELECTOR, 'tbody > tr')

        for row in deal_rows:
            try:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) < 5:
                    continue

                deal_name = cells[0].text.strip()
                location = cells[1].text.strip()
                units = cells[2].text.strip()
                ami = cells[3].text.strip()
                status = cells[4].text.strip()

                deals.append({
                    'name': deal_name,
                    'location': location,
                    'units': units,
                    'ami': ami,
                    'status': status
                })
            except Exception:
                continue
    except Exception:
        pass

    return deals


def scrape_potential_deal(driver, wait: WebDriverWait) -> Dict:
    """Scrape potential deal from the Underwriting page."""
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        def get_input_value(label_text: str) -> str:
            try:
                elem = driver.find_element(By.XPATH, f"//label[contains(normalize-space(.), '{label_text}')]/following-sibling::input")
                return elem.get_attribute('value')
            except Exception:
                return ''

        def get_select_value(label_text: str) -> str:
            try:
                sel = driver.find_element(By.XPATH, f"//label[contains(normalize-space(.), '{label_text}')]/following::select[1]")
                s = Select(sel)
                return s.first_selected_option.text
            except Exception:
                return ''

        return {
            'name': get_input_value('Deal Name'),
            'location': get_input_value('Location'),
            'units': get_input_value('Total Units'),
            'purchase_price': get_input_value('Purchase Price'),
            'construction_cost': get_input_value('Construction Cost'),
            'avg_monthly_rent': get_input_value('Average Monthly Rent'),
            'ami_target': get_select_value('AMI Target'),
            'gp_partner': get_select_value('GP Partner'),
            'status': 'Potential'
        }
    except Exception:
        return {}
