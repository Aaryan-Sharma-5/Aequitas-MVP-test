"""
Update Market Decile Thresholds
Fetches rent data from RentCast API and calculates decile thresholds

This script should be run monthly to keep thresholds current
"""

import sys
import os
from datetime import datetime
import statistics

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db
from app.services.rent_tier_service import RentTierService
from app.services.rentcast_service import RentCastService
from app import create_app


def calculate_deciles(rent_values):
    """
    Calculate decile thresholds from list of rent values

    Args:
        rent_values: List of rental prices

    Returns:
        Dictionary with d1_threshold through d10_threshold
    """
    if not rent_values or len(rent_values) < 10:
        raise ValueError("Need at least 10 rent values to calculate deciles")

    sorted_rents = sorted(rent_values)
    n = len(sorted_rents)

    deciles = {}
    for i in range(1, 11):
        # Calculate index for this decile (10th, 20th, ..., 90th, 100th percentile)
        percentile = i * 10
        index = int((percentile / 100) * n) - 1

        # Ensure index is within bounds
        index = max(0, min(index, n - 1))

        deciles[f'd{i}_threshold'] = sorted_rents[index]

    return deciles


def update_thresholds_for_geography(geography, major_cities=None):
    """
    Update thresholds for a specific geography

    Args:
        geography: 'national', state code, or zipcode
        major_cities: List of zipcodes to sample (for national/state level)
    """
    print(f"\nUpdating thresholds for: {geography}")

    # For national/state level, we need to sample multiple markets
    # For zipcode level, we can get market stats directly

    if major_cities:
        all_rents = {1: [], 2: [], 3: [], 4: []}  # By bedroom count

        for city_zip in major_cities:
            try:
                print(f"  Fetching data for {city_zip}...")
                # Get market statistics from RentCast
                market_stats = RentCastService.get_market_statistics(city_zip)

                if market_stats:
                    # Extract rent values by bedroom count
                    for br in [1, 2, 3, 4]:
                        br_key = f'{br}br'  # RentCast uses '1br', '2br', etc.
                        if br_key in market_stats:
                            rent = market_stats[br_key].get('median_rent')
                            if rent and rent > 0:
                                all_rents[br].append(rent)

            except Exception as e:
                print(f"    Warning: Could not fetch data for {city_zip}: {e}")
                continue

        # Calculate deciles for each bedroom count
        current_year = datetime.now().year

        for bedrooms, rents in all_rents.items():
            if len(rents) >= 10:
                print(f"  Calculating {bedrooms}BR thresholds from {len(rents)} data points...")
                deciles = calculate_deciles(rents)

                # Save to database
                RentTierService.update_market_thresholds(
                    geography=geography,
                    bedrooms=bedrooms,
                    thresholds=deciles,
                    data_year=current_year
                )
                print(f"    ✓ Updated {bedrooms}BR thresholds")
                print(f"      D1 (low): ${deciles['d1_threshold']:.0f}")
                print(f"      D5 (median): ${deciles['d5_threshold']:.0f}")
                print(f"      D10 (high): ${deciles['d10_threshold']:.0f}")
            else:
                print(f"    ⚠ Not enough data for {bedrooms}BR ({len(rents)} points)")

    else:
        print("  Skipping - need major_cities list for sampling")


def main():
    """
    Main threshold update function
    """
    print("=" * 60)
    print("MARKET DECILE THRESHOLD UPDATE")
    print("=" * 60)
    print()

    app = create_app()

    with app.app_context():
        # Major US cities for national sampling (representative MSAs)
        major_us_cities = [
            '10001',  # New York, NY
            '90012',  # Los Angeles, CA
            '60601',  # Chicago, IL
            '77001',  # Houston, TX
            '85001',  # Phoenix, AZ
            '19102',  # Philadelphia, PA
            '78701',  # Austin, TX
            '94102',  # San Francisco, CA
            '30301',  # Atlanta, GA
            '02101',  # Boston, MA
            '98101',  # Seattle, WA
            '20001',  # Washington, DC
            '55401',  # Minneapolis, MN
            '80201',  # Denver, CO
            '33101',  # Miami, FL
            '97201',  # Portland, OR
            '28201',  # Charlotte, NC
            '75201',  # Dallas, TX
            '63101',  # St. Louis, MO
            '15201'   # Pittsburgh, PA
        ]

        # Update national thresholds
        print("\n" + "=" * 60)
        print("UPDATING NATIONAL THRESHOLDS")
        print("=" * 60)
        update_thresholds_for_geography('national', major_us_cities)

        # Update California thresholds
        ca_cities = [
            '94102',  # San Francisco
            '90012',  # Los Angeles
            '92101',  # San Diego
            '95113',  # San Jose
            '94102',  # Oakland
            '95814'   # Sacramento
        ]

        print("\n" + "=" * 60)
        print("UPDATING CALIFORNIA THRESHOLDS")
        print("=" * 60)
        update_thresholds_for_geography('CA', ca_cities)

        # Update Texas thresholds
        tx_cities = [
            '77001',  # Houston
            '78701',  # Austin
            '75201',  # Dallas
            '78205'   # San Antonio
        ]

        print("\n" + "=" * 60)
        print("UPDATING TEXAS THRESHOLDS")
        print("=" * 60)
        update_thresholds_for_geography('TX', tx_cities)

        # Summary
        print("\n" + "=" * 60)
        print("UPDATE COMPLETE")
        print("=" * 60)
        print("\nThreshold updates completed successfully.")
        print("\nNote: These thresholds should be refreshed monthly to stay current.")
        print("Set up a cron job to run this script on the 1st of each month.")
        print()


if __name__ == '__main__':
    main()
