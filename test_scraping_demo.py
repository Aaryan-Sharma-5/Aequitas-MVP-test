"""
Demo script to test property scraping with a real LoopNet URL
Run this to see what data would be extracted
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.scraping_service import ScrapingService

# Test URL
test_url = "https://www.loopnet.com/Listing/2255-2297-E-Shaw-Ave-Fresno-CA/35748247/"

print("=" * 80)
print("🏢 PROPERTY SCRAPING DEMO")
print("=" * 80)
print(f"\n📍 URL: {test_url}\n")

# Initialize scraping service
scraping_service = ScrapingService(cache_ttl=3600)

print("🔍 Starting extraction process...\n")

# Extract property data
result = scraping_service.extract_from_url(test_url, enrich=False)

print("-" * 80)
print("📊 EXTRACTION RESULTS")
print("-" * 80)

print(f"\n✅ Status: {result.status}")
print(f"🎯 Method: {result.method}")
print(f"📈 Confidence Score: {result.confidence_score:.2%}" if result.confidence_score else "📈 Confidence Score: N/A")
print(f"🌐 Source Platform: {result.source_platform}")

if result.extracted_data:
    print("\n" + "=" * 80)
    print("📋 EXTRACTED PROPERTY DATA")
    print("=" * 80)

    data = result.extracted_data

    # Address Information
    print("\n🏠 ADDRESS INFORMATION:")
    print(f"  • Street Address: {data.address or 'Not extracted'}")
    print(f"  • City: {data.city or 'Not extracted'}")
    print(f"  • State: {data.state or 'Not extracted'}")
    print(f"  • ZIP Code: {data.zipcode or 'Not extracted'}")

    # Property Details
    print("\n🏗️  PROPERTY DETAILS:")
    print(f"  • Property Name: {data.property_name or 'Not extracted'}")
    print(f"  • Property Type: {data.property_type or 'Not extracted'}")
    print(f"  • Building Size: {f'{data.building_size_sf:,} SF' if data.building_size_sf else 'Not extracted'}")
    print(f"  • Lot Size: {f'{data.lot_size_acres:.2f} acres' if data.lot_size_acres else 'Not extracted'}")
    print(f"  • Year Built: {data.year_built or 'Not extracted'}")
    print(f"  • Number of Units: {data.num_units or 'Not extracted'}")
    print(f"  • Number of Stories: {data.num_stories or 'Not extracted'}")

    # Financial Data
    print("\n💰 FINANCIAL DATA:")
    print(f"  • Asking Price: {f'${data.asking_price:,.0f}' if data.asking_price else 'Not extracted'}")
    print(f"  • Price per SF: {f'${data.price_per_sf:,.2f}' if data.price_per_sf else 'Not extracted'}")
    print(f"  • Price per Unit: {f'${data.price_per_unit:,.0f}' if data.price_per_unit else 'Not extracted'}")
    print(f"  • Cap Rate: {f'{data.cap_rate}%' if data.cap_rate else 'Not extracted'}")
    print(f"  • NOI: {f'${data.noi:,.0f}' if data.noi else 'Not extracted'}")

    # Location Data
    if data.latitude or data.longitude or data.walk_score or data.transit_score:
        print("\n📍 LOCATION DATA:")
        if data.latitude and data.longitude:
            print(f"  • Coordinates: {data.latitude:.6f}, {data.longitude:.6f}")
        if data.walk_score:
            print(f"  • Walk Score: {data.walk_score}")
        if data.transit_score:
            print(f"  • Transit Score: {data.transit_score}")

    # Parking
    if data.parking_spaces or data.parking_type:
        print("\n🚗 PARKING:")
        print(f"  • Parking Spaces: {data.parking_spaces or 'Not extracted'}")
        print(f"  • Parking Type: {data.parking_type or 'Not extracted'}")

if result.warnings:
    print("\n" + "=" * 80)
    print("⚠️  WARNINGS")
    print("=" * 80)
    for warning in result.warnings:
        print(f"  • {warning}")

if result.missing_fields:
    print("\n" + "=" * 80)
    print("📝 MISSING FIELDS (User input recommended)")
    print("=" * 80)
    print(f"  {', '.join(result.missing_fields)}")

if result.error_message:
    print("\n" + "=" * 80)
    print("❌ ERROR")
    print("=" * 80)
    print(f"  Type: {result.error_type}")
    print(f"  Message: {result.error_message}")
    if result.suggested_action:
        print(f"  Suggested Action: {result.suggested_action}")

print("\n" + "=" * 80)
print("✨ DEMO COMPLETE")
print("=" * 80)
print("\nThis is what the user would see in the preview card after clicking 'Extract Property Data'")
print("They can then click 'Use This Data' to populate the deal form.")
print("=" * 80 + "\n")
