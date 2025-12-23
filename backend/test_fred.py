#!/usr/bin/env python3
"""Test script for FRED API."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.services.fred_service import FREDService

# Initialize service
api_key = os.getenv('FRED_API_KEY')
print(f"API Key loaded: {api_key[:10]}..." if api_key else "No API key!")

try:
    fred = FREDService(api_key=api_key)
    print("\nFetching macroeconomic snapshot...")
    data = fred.get_macroeconomic_snapshot()

    if data:
        print("\n✓ Success!")
        print(f"Federal Funds Rate: {data.interest_rates.federal_funds_rate}%")
        print(f"30-Year Mortgage: {data.interest_rates.mortgage_30yr}%")
        print(f"CPI: {data.inflation.cpi_all_items}")
        print(f"Housing Starts: {data.housing_market.housing_starts}")
    else:
        print("\n✗ No data returned")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
