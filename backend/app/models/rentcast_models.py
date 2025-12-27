"""RentCast API data models for rental market intelligence."""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class RentEstimateData:
    """Property rent estimate with range."""

    address: str
    zipcode: str
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_footage: Optional[int] = None
    estimated_rent: Optional[float] = None
    rent_range_low: Optional[float] = None
    rent_range_high: Optional[float] = None
    price_per_sqft: Optional[float] = None
    property_type: Optional[str] = None
    last_updated: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to camelCase dictionary for JSON response."""
        return {
            'address': self.address,
            'zipcode': self.zipcode,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'squareFootage': self.square_footage,
            'estimatedRent': self.estimated_rent,
            'rentRangeLow': self.rent_range_low,
            'rentRangeHigh': self.rent_range_high,
            'pricePerSqft': self.price_per_sqft,
            'propertyType': self.property_type,
            'lastUpdated': self.last_updated
        }


@dataclass
class RentalComparable:
    """Individual comparable rental property."""

    address: str
    distance_miles: float
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    square_footage: Optional[int] = None
    listed_rent: Optional[float] = None
    price_per_sqft: Optional[float] = None
    property_type: Optional[str] = None
    days_on_market: Optional[int] = None
    listing_url: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to camelCase dictionary for JSON response."""
        return {
            'address': self.address,
            'distanceMiles': self.distance_miles,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'squareFootage': self.square_footage,
            'listedRent': self.listed_rent,
            'pricePerSqft': self.price_per_sqft,
            'propertyType': self.property_type,
            'daysOnMarket': self.days_on_market,
            'listingUrl': self.listing_url
        }


@dataclass
class MarketStatistics:
    """ZIP-level rental market statistics."""

    zipcode: str
    data_month: str
    avg_rent_all: Optional[float] = None
    median_rent_all: Optional[float] = None
    avg_rent_1bed: Optional[float] = None
    avg_rent_2bed: Optional[float] = None
    avg_rent_3bed: Optional[float] = None
    avg_rent_4bed: Optional[float] = None
    total_listings: Optional[int] = None
    avg_days_on_market: Optional[int] = None
    inventory_level: Optional[str] = None
    last_updated: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to camelCase dictionary for JSON response."""
        return {
            'zipcode': self.zipcode,
            'dataMonth': self.data_month,
            'avgRentAll': self.avg_rent_all,
            'medianRentAll': self.median_rent_all,
            'avgRent1bed': self.avg_rent_1bed,
            'avgRent2bed': self.avg_rent_2bed,
            'avgRent3bed': self.avg_rent_3bed,
            'avgRent4bed': self.avg_rent_4bed,
            'totalListings': self.total_listings,
            'avgDaysOnMarket': self.avg_days_on_market,
            'inventoryLevel': self.inventory_level,
            'lastUpdated': self.last_updated
        }


@dataclass
class MarketTrend:
    """Historical rental market trend data point."""

    date: str
    avg_rent: Optional[float] = None
    median_rent: Optional[float] = None
    listing_count: Optional[int] = None

    def to_dict(self) -> dict:
        """Convert to camelCase dictionary for JSON response."""
        return {
            'date': self.date,
            'avgRent': self.avg_rent,
            'medianRent': self.median_rent,
            'listingCount': self.listing_count
        }


@dataclass
class PropertyValuation:
    """Complete property valuation package."""

    rent_estimate: RentEstimateData
    comparables: List[RentalComparable]
    market_stats: Optional[MarketStatistics] = None
    last_updated: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to camelCase dictionary for JSON response."""
        return {
            'rentEstimate': self.rent_estimate.to_dict(),
            'comparables': [comp.to_dict() for comp in self.comparables],
            'marketStats': self.market_stats.to_dict() if self.market_stats else None,
            'lastUpdated': self.last_updated
        }
