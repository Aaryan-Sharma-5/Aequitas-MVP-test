"""Web scraping data models for property listing extraction."""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class AddressData:
    """Parsed address components from listing URL."""

    street_address: str
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to camelCase dictionary for JSON response."""
        return {
            'streetAddress': self.street_address,
            'city': self.city,
            'state': self.state,
            'zipcode': self.zipcode
        }


@dataclass
class PropertyData:
    """Extracted property information from listing."""

    # Basic Information
    property_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None

    # Location Data
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    walk_score: Optional[int] = None
    transit_score: Optional[int] = None

    # Property Details
    property_type: Optional[str] = None
    building_size_sf: Optional[int] = None
    lot_size_acres: Optional[float] = None
    year_built: Optional[int] = None
    num_units: Optional[int] = None
    num_stories: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    zoning: Optional[str] = None
    parcel_id: Optional[str] = None

    # Financial Data
    asking_price: Optional[float] = None
    price_per_sf: Optional[float] = None
    price_per_unit: Optional[float] = None
    cap_rate: Optional[float] = None
    noi: Optional[float] = None
    gross_income: Optional[float] = None
    occupancy_rate: Optional[float] = None

    # Parking
    parking_spaces: Optional[int] = None
    parking_type: Optional[str] = None
    parking_ratio: Optional[float] = None

    # Listing Information
    listing_url: Optional[str] = None
    listing_id: Optional[str] = None
    days_on_market: Optional[int] = None
    listing_status: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to camelCase dictionary for JSON response."""
        return {
            # Basic Information
            'propertyName': self.property_name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zipcode': self.zipcode,

            # Location Data
            'latitude': self.latitude,
            'longitude': self.longitude,
            'walkScore': self.walk_score,
            'transitScore': self.transit_score,

            # Property Details
            'propertyType': self.property_type,
            'buildingSizeSf': self.building_size_sf,
            'lotSizeAcres': self.lot_size_acres,
            'yearBuilt': self.year_built,
            'numUnits': self.num_units,
            'numStories': self.num_stories,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'zoning': self.zoning,
            'parcelId': self.parcel_id,

            # Financial Data
            'askingPrice': self.asking_price,
            'pricePerSf': self.price_per_sf,
            'pricePerUnit': self.price_per_unit,
            'capRate': self.cap_rate,
            'noi': self.noi,
            'grossIncome': self.gross_income,
            'occupancyRate': self.occupancy_rate,

            # Parking
            'parkingSpaces': self.parking_spaces,
            'parkingType': self.parking_type,
            'parkingRatio': self.parking_ratio,

            # Listing Information
            'listingUrl': self.listing_url,
            'listingId': self.listing_id,
            'daysOnMarket': self.days_on_market,
            'listingStatus': self.listing_status
        }


@dataclass
class EnrichmentData:
    """API enrichment data from RentCast and other sources."""

    # RentCast Data
    estimated_rent: Optional[float] = None
    rent_range_low: Optional[float] = None
    rent_range_high: Optional[float] = None
    estimated_value: Optional[float] = None
    value_range_low: Optional[float] = None
    value_range_high: Optional[float] = None

    # Market Data
    market_avg_rent: Optional[float] = None
    market_median_rent: Optional[float] = None
    market_inventory_level: Optional[str] = None

    # Comparable Properties
    comparable_count: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to camelCase dictionary for JSON response."""
        return {
            'estimatedRent': self.estimated_rent,
            'rentRangeLow': self.rent_range_low,
            'rentRangeHigh': self.rent_range_high,
            'estimatedValue': self.estimated_value,
            'valueRangeLow': self.value_range_low,
            'valueRangeHigh': self.value_range_high,
            'marketAvgRent': self.market_avg_rent,
            'marketMedianRent': self.market_median_rent,
            'marketInventoryLevel': self.market_inventory_level,
            'comparableCount': self.comparable_count
        }


@dataclass
class ScrapingResult:
    """Complete result of property scraping operation."""

    # Status
    status: str  # 'success', 'partial', 'failed'
    method: Optional[str] = None  # 'tier1_direct', 'tier2_syndication', 'tier3_api_enrichment'

    # Data
    extracted_data: Optional[PropertyData] = None
    enrichment_data: Optional[EnrichmentData] = None

    # Metadata
    confidence_score: Optional[float] = None
    missing_fields: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    requires_user_input: bool = False

    # Error Information
    error_type: Optional[str] = None  # 'blocked', 'parse_error', 'network_error', 'not_found'
    error_message: Optional[str] = None
    suggested_action: Optional[str] = None

    # Source Information
    source_url: Optional[str] = None
    source_platform: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to camelCase dictionary for JSON response."""
        return {
            'status': self.status,
            'method': self.method,
            'extractedData': self.extracted_data.to_dict() if self.extracted_data else None,
            'enrichmentData': self.enrichment_data.to_dict() if self.enrichment_data else None,
            'confidenceScore': self.confidence_score,
            'missingFields': self.missing_fields,
            'warnings': self.warnings,
            'requiresUserInput': self.requires_user_input,
            'errorType': self.error_type,
            'errorMessage': self.error_message,
            'suggestedAction': self.suggested_action,
            'sourceUrl': self.source_url,
            'sourcePlatform': self.source_platform
        }
