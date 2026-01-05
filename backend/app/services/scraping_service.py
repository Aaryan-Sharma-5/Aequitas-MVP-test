"""Web scraping service for property listing extraction."""

import requests
import re
import json
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from urllib.parse import urlparse, quote_plus
from app.models.scraping_models import (
    PropertyData,
    AddressData,
    EnrichmentData,
    ScrapingResult
)


# Custom Exception Classes
class ScrapingError(Exception):
    """Base exception for scraping errors."""
    pass


class BlockedError(ScrapingError):
    """Raised when site blocks automated access."""
    pass


class ParseError(ScrapingError):
    """Raised when HTML parsing fails."""
    pass


class NetworkError(ScrapingError):
    """Raised when network request fails."""
    pass


class ListingNotFoundError(ScrapingError):
    """Raised when listing not found on any source."""
    pass


class ScrapingCache:
    """Simple in-memory cache with TTL support for scraping results."""

    def __init__(self):
        self._cache: dict[str, tuple] = {}
        self._max_size = 500

    def get(self, key: str) -> Optional[dict]:
        """Retrieve cached value if not expired."""
        if key in self._cache:
            value, expiry = self._cache[key]
            if datetime.now() < expiry:
                return value
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: dict, ttl_seconds: int = 86400):
        """Store value with TTL (default 24 hours)."""
        if len(self._cache) >= self._max_size:
            # Simple LRU: remove oldest entry
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]

        expiry = datetime.now() + timedelta(seconds=ttl_seconds)
        self._cache[key] = (value, expiry)

    def clear(self):
        """Clear all cached entries."""
        self._cache.clear()


class ScrapingService:
    """Service for scraping property listings from LoopNet, Crexi, and syndication sites."""

    # User agent for requests
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    def __init__(self, cache_ttl: int = 86400):
        """
        Initialize scraping service.

        Args:
            cache_ttl: Cache time-to-live in seconds (default 24 hours)
        """
        self.cache_ttl = cache_ttl
        self.cache = ScrapingCache()

    def extract_from_url(
        self,
        url: str,
        enrich: bool = True
    ) -> ScrapingResult:
        """
        Extract property data from listing URL with multi-tier fallback.

        Args:
            url: Listing URL (LoopNet, Crexi, etc.)
            enrich: Whether to enrich with RentCast API

        Returns:
            ScrapingResult object with extracted data
        """
        # Normalize URL for caching
        normalized_url = self._normalize_url(url)
        cache_key = f"scraping:extract:{normalized_url}:{enrich}"

        # Check cache first
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return self._dict_to_scraping_result(cached_data)

        # Determine source platform
        source_platform = self._detect_platform(url)

        try:
            # Tier 1: Extract address from URL
            address_data = self._extract_address_from_url(url, source_platform)
            if not address_data:
                raise ParseError(f"Could not parse address from URL: {url}")

            # Initialize property data with address
            property_data = PropertyData(
                address=address_data.street_address,
                city=address_data.city,
                state=address_data.state,
                zipcode=address_data.zipcode,
                listing_url=url
            )

            # Tier 2: Try scraping syndication sites
            method = 'tier3_api_enrichment'  # Default to tier 3
            warnings = []

            try:
                scraped_data = self._scrape_syndication_sites(address_data)
                if scraped_data:
                    # Merge scraped data into property_data
                    property_data = self._merge_property_data(property_data, scraped_data)
                    method = 'tier2_syndication'
            except (BlockedError, NetworkError) as e:
                warnings.append(f"Web scraping failed: {str(e)}")
                print(f"Scraping error: {str(e)}")

            # Tier 3: Enrich with RentCast API if enabled
            enrichment_data = None
            if enrich and address_data.street_address and address_data.zipcode:
                try:
                    enrichment_data = self._enrich_with_rentcast(
                        address_data.street_address,
                        address_data.zipcode
                    )
                except Exception as e:
                    warnings.append(f"RentCast enrichment failed: {str(e)}")
                    print(f"RentCast error: {str(e)}")

            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(property_data)
            missing_fields = self._identify_missing_fields(property_data)

            # Determine status
            status = 'success' if confidence_score >= 0.7 else 'partial'
            requires_user_input = confidence_score < 0.5

            # Create result
            result = ScrapingResult(
                status=status,
                method=method,
                extracted_data=property_data,
                enrichment_data=enrichment_data,
                confidence_score=confidence_score,
                missing_fields=missing_fields,
                warnings=warnings if warnings else None,
                requires_user_input=requires_user_input,
                source_url=url,
                source_platform=source_platform
            )

            # Cache the result
            self.cache.set(cache_key, result.to_dict(), self.cache_ttl)

            return result

        except BlockedError as e:
            return ScrapingResult(
                status='failed',
                error_type='blocked',
                error_message=str(e),
                suggested_action='Try using a syndicated listing URL (Showcase.com or CityFeet.com)',
                source_url=url,
                source_platform=source_platform
            )
        except ParseError as e:
            return ScrapingResult(
                status='failed',
                error_type='parse_error',
                error_message=str(e),
                suggested_action='Please check the URL format and try again',
                source_url=url,
                source_platform=source_platform
            )
        except NetworkError as e:
            return ScrapingResult(
                status='failed',
                error_type='network_error',
                error_message=str(e),
                suggested_action='Please check your connection and try again',
                source_url=url,
                source_platform=source_platform
            )
        except Exception as e:
            print(f"Unexpected scraping error: {str(e)}")
            return ScrapingResult(
                status='failed',
                error_type='unknown',
                error_message='Internal scraping error',
                suggested_action='Please try again or enter property details manually',
                source_url=url,
                source_platform=source_platform
            )

    def _normalize_url(self, url: str) -> str:
        """Normalize URL for consistent caching."""
        parsed = urlparse(url.lower())
        # Remove query params and fragments
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')

    def _detect_platform(self, url: str) -> str:
        """Detect source platform from URL."""
        url_lower = url.lower()
        if 'loopnet.com' in url_lower:
            return 'loopnet'
        elif 'crexi.com' in url_lower:
            return 'crexi'
        elif 'showcase.com' in url_lower:
            return 'showcase'
        elif 'cityfeet.com' in url_lower:
            return 'cityfeet'
        else:
            return 'unknown'

    def _extract_address_from_url(
        self,
        url: str,
        platform: str
    ) -> Optional[AddressData]:
        """
        Extract address components from listing URL.

        Args:
            url: Listing URL
            platform: Source platform (loopnet, crexi, etc.)

        Returns:
            AddressData object or None if parsing fails
        """
        try:
            if platform == 'loopnet':
                # LoopNet pattern: /Listing/123-Main-St-Sacramento-CA/12345678/
                match = re.search(r'/Listing/([^/]+)/(\d+)', url)
                if match:
                    address_slug = match.group(1)
                    listing_id = match.group(2)
                    return self._parse_address_slug(address_slug)

            elif platform == 'crexi':
                # Crexi pattern: /properties/123456-123-main-st-sacramento-ca-95814
                match = re.search(r'/properties/\d+-([^/]+)', url)
                if match:
                    address_slug = match.group(1)
                    return self._parse_address_slug(address_slug)

            elif platform in ['showcase', 'cityfeet']:
                # Similar patterns for syndication sites
                match = re.search(r'/([^/]+)/?$', url)
                if match:
                    address_slug = match.group(1)
                    return self._parse_address_slug(address_slug)

            return None

        except Exception as e:
            print(f"Error parsing address from URL: {str(e)}")
            return None

    def _parse_address_slug(self, slug: str) -> Optional[AddressData]:
        """
        Parse address components from URL slug.

        Args:
            slug: Address slug (e.g., "123-Main-St-Sacramento-CA-95814")

        Returns:
            AddressData object or None if parsing fails
        """
        try:
            # Replace hyphens with spaces
            parts = slug.replace('-', ' ').split()

            # Try to identify state (2-letter code)
            state_idx = None
            for i, part in enumerate(parts):
                if len(part) == 2 and part.isalpha() and part.isupper():
                    state_idx = i
                    break

            if state_idx is None:
                # No state found, return just the address
                return AddressData(
                    street_address=' '.join(parts)
                )

            # Extract components
            street_address = ' '.join(parts[:state_idx])
            state = parts[state_idx]

            # City is usually before state
            city = parts[state_idx - 1] if state_idx > 0 else None

            # Zipcode might be after state
            zipcode = None
            if state_idx + 1 < len(parts):
                potential_zip = parts[state_idx + 1]
                if re.match(r'^\d{5}$', potential_zip):
                    zipcode = potential_zip

            # Adjust street address to exclude city
            if city:
                street_parts = parts[:state_idx - 1]
                street_address = ' '.join(street_parts) if street_parts else street_address

            return AddressData(
                street_address=street_address,
                city=city,
                state=state,
                zipcode=zipcode
            )

        except Exception as e:
            print(f"Error parsing address slug: {str(e)}")
            return None

    def _scrape_syndication_sites(
        self,
        address_data: AddressData
    ) -> Optional[PropertyData]:
        """
        Try scraping property data from syndication sites.

        Args:
            address_data: Parsed address data

        Returns:
            PropertyData object or None if scraping fails
        """
        # Try Showcase.com first
        try:
            data = self._scrape_showcase(address_data)
            if data:
                return data
        except Exception as e:
            print(f"Showcase scraping failed: {str(e)}")

        # Try CityFeet.com as fallback
        try:
            data = self._scrape_cityfeet(address_data)
            if data:
                return data
        except Exception as e:
            print(f"CityFeet scraping failed: {str(e)}")

        return None

    def _scrape_showcase(
        self,
        address_data: AddressData
    ) -> Optional[PropertyData]:
        """
        Scrape property data from Showcase.com.

        Args:
            address_data: Parsed address data

        Returns:
            PropertyData object or None if scraping fails
        """
        try:
            # Build search URL
            query = f"{address_data.street_address} {address_data.city} {address_data.state}".strip()
            search_url = f"https://www.showcase.com/search?q={quote_plus(query)}"

            response = requests.get(search_url, headers=self.HEADERS, timeout=10)

            if response.status_code == 403 or response.status_code == 429:
                raise BlockedError("Showcase.com blocked the request")

            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.content, 'html5lib')

            # Extract property details
            property_data = PropertyData()

            # Property name
            name_elem = soup.find('h1', class_=re.compile(r'property|listing'))
            if name_elem:
                property_data.property_name = name_elem.text.strip()

            # Parse table rows for property details
            for row in soup.find_all('tr'):
                cells = row.find_all(['th', 'td'])
                if len(cells) == 2:
                    label = cells[0].text.strip().lower()
                    value = cells[1].text.strip()

                    if 'building size' in label or 'square feet' in label:
                        property_data.building_size_sf = self._parse_number(value)
                    elif 'year built' in label:
                        property_data.year_built = self._parse_year(value)
                    elif 'stories' in label:
                        property_data.num_stories = self._parse_number(value)
                    elif 'units' in label:
                        property_data.num_units = self._parse_number(value)
                    elif 'price' in label or 'asking' in label:
                        property_data.asking_price = self._parse_price(value)
                    elif 'parking' in label:
                        property_data.parking_spaces = self._parse_number(value)
                    elif 'lot size' in label:
                        property_data.lot_size_acres = self._parse_acres(value)
                    elif 'property type' in label:
                        property_data.property_type = value
                    elif 'zoning' in label:
                        property_data.zoning = value

            return property_data if property_data.property_name else None

        except BlockedError:
            raise
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error accessing Showcase.com: {str(e)}")
        except Exception as e:
            print(f"Error scraping Showcase.com: {str(e)}")
            return None

    def _scrape_cityfeet(
        self,
        address_data: AddressData
    ) -> Optional[PropertyData]:
        """
        Scrape property data from CityFeet.com.

        Args:
            address_data: Parsed address data

        Returns:
            PropertyData object or None if scraping fails
        """
        try:
            # Build search URL
            query = f"{address_data.street_address} {address_data.city} {address_data.state}".strip()
            search_url = f"https://www.cityfeet.com/search?q={quote_plus(query)}"

            response = requests.get(search_url, headers=self.HEADERS, timeout=10)

            if response.status_code == 403 or response.status_code == 429:
                raise BlockedError("CityFeet.com blocked the request")

            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.content, 'html5lib')

            # Extract property details
            property_data = PropertyData()

            # Property name from h1
            h1 = soup.find('h1')
            if h1:
                property_data.property_name = h1.text.strip().split(' OFF MARKET')[0]

            # Property details from list items
            for li in soup.find_all('li'):
                text = li.text.strip().lower()

                if 'property type' in text:
                    property_data.property_type = li.text.split(':')[-1].strip()
                elif 'building size' in text:
                    property_data.building_size_sf = self._parse_number(li.text)
                elif 'year built' in text:
                    property_data.year_built = self._parse_year(li.text)
                elif 'lot size' in text:
                    property_data.lot_size_acres = self._parse_acres(li.text)
                elif 'zoning' in text:
                    property_data.zoning = li.text.split(':')[-1].strip()
                elif 'units' in text:
                    property_data.num_units = self._parse_number(li.text)

            # Walk/Transit scores
            score_divs = soup.find_all(text=re.compile(r'Score'))
            for div in score_divs:
                if 'Walk' in div:
                    property_data.walk_score = self._parse_number(div)
                elif 'Transit' in div:
                    property_data.transit_score = self._parse_number(div)

            # Parking
            parking_section = soup.find(text=re.compile(r'Spaces Provided'))
            if parking_section:
                property_data.parking_spaces = self._parse_number(parking_section.parent.text)

            return property_data if property_data.property_name else None

        except BlockedError:
            raise
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error accessing CityFeet.com: {str(e)}")
        except Exception as e:
            print(f"Error scraping CityFeet.com: {str(e)}")
            return None

    def _enrich_with_rentcast(
        self,
        address: str,
        zipcode: str
    ) -> Optional[EnrichmentData]:
        """
        Enrich property data with RentCast API.

        Args:
            address: Property address
            zipcode: ZIP code

        Returns:
            EnrichmentData object or None if enrichment fails
        """
        try:
            # Import RentCast service
            from app.services.rentcast_service import RentCastService
            import os

            # Get API key from environment
            api_key = os.getenv('RENTCAST_API_KEY', '')
            if not api_key:
                print("RentCast API key not found, skipping enrichment")
                return None

            # Initialize service
            rentcast_service = RentCastService(api_key=api_key)

            # Get rent estimate
            rent_estimate = rentcast_service.get_rent_estimate(
                address=address,
                zipcode=zipcode
            )

            if not rent_estimate:
                return None

            # Get market statistics
            market_stats = rentcast_service.get_market_statistics(zipcode=zipcode)

            # Create enrichment data
            enrichment = EnrichmentData(
                estimated_rent=rent_estimate.estimated_rent,
                rent_range_low=rent_estimate.rent_range_low,
                rent_range_high=rent_estimate.rent_range_high
            )

            if market_stats:
                enrichment.market_avg_rent = market_stats.avg_rent_all
                enrichment.market_median_rent = market_stats.median_rent_all
                enrichment.market_inventory_level = market_stats.inventory_level

            return enrichment

        except Exception as e:
            print(f"RentCast enrichment error: {str(e)}")
            return None

    def _merge_property_data(
        self,
        base: PropertyData,
        scraped: PropertyData
    ) -> PropertyData:
        """
        Merge scraped data into base property data.

        Args:
            base: Base property data
            scraped: Scraped property data

        Returns:
            Merged PropertyData object
        """
        # Update base with non-None values from scraped
        for field in scraped.__dataclass_fields__:
            scraped_value = getattr(scraped, field)
            if scraped_value is not None:
                setattr(base, field, scraped_value)

        return base

    def _calculate_confidence_score(self, property_data: PropertyData) -> float:
        """
        Calculate confidence score based on extracted fields.

        Args:
            property_data: Extracted property data

        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Define field weights
        critical_fields = [
            'address', 'city', 'state', 'zipcode'
        ]
        important_fields = [
            'asking_price', 'building_size_sf', 'property_type'
        ]
        optional_fields = [
            'year_built', 'num_units', 'bedrooms', 'bathrooms',
            'latitude', 'longitude', 'parking_spaces'
        ]

        # Count filled fields
        critical_count = sum(1 for field in critical_fields if getattr(property_data, field))
        important_count = sum(1 for field in important_fields if getattr(property_data, field))
        optional_count = sum(1 for field in optional_fields if getattr(property_data, field))

        # Calculate weighted score
        critical_score = critical_count / len(critical_fields) * 0.5
        important_score = important_count / len(important_fields) * 0.3
        optional_score = optional_count / len(optional_fields) * 0.2

        return min(critical_score + important_score + optional_score, 1.0)

    def _identify_missing_fields(self, property_data: PropertyData) -> List[str]:
        """
        Identify important fields that are missing.

        Args:
            property_data: Extracted property data

        Returns:
            List of missing field names
        """
        important_fields = [
            'address', 'city', 'state', 'zipcode',
            'asking_price', 'building_size_sf', 'property_type',
            'year_built', 'bedrooms', 'bathrooms'
        ]

        missing = []
        for field in important_fields:
            if getattr(property_data, field) is None:
                # Convert snake_case to readable format
                readable = field.replace('_', ' ').title()
                missing.append(readable)

        return missing

    def _parse_number(self, text: str) -> Optional[int]:
        """Parse integer from text."""
        try:
            match = re.search(r'[\d,]+', text.replace(',', ''))
            if match:
                return int(match.group())
        except:
            pass
        return None

    def _parse_price(self, text: str) -> Optional[float]:
        """Parse price from text (handles $1.2M, $625k, etc.)."""
        try:
            text = text.upper().replace(',', '').replace('$', '')

            if 'M' in text:
                number = float(re.search(r'[\d.]+', text).group())
                return number * 1_000_000
            elif 'K' in text:
                number = float(re.search(r'[\d.]+', text).group())
                return number * 1_000
            else:
                return float(re.search(r'[\d.]+', text).group())
        except:
            pass
        return None

    def _parse_acres(self, text: str) -> Optional[float]:
        """Parse acres from text."""
        try:
            match = re.search(r'([\d.]+)\s*ac', text.lower())
            if match:
                return float(match.group(1))
        except:
            pass
        return None

    def _parse_year(self, text: str) -> Optional[int]:
        """Parse year from text."""
        try:
            match = re.search(r'\b(19|20)\d{2}\b', text)
            if match:
                return int(match.group())
        except:
            pass
        return None

    def _dict_to_scraping_result(self, data: dict) -> ScrapingResult:
        """Convert dictionary to ScrapingResult."""
        extracted_data = None
        if data.get('extractedData'):
            extracted_data = PropertyData(**data['extractedData'])

        enrichment_data = None
        if data.get('enrichmentData'):
            enrichment_data = EnrichmentData(**data['enrichmentData'])

        return ScrapingResult(
            status=data['status'],
            method=data.get('method'),
            extracted_data=extracted_data,
            enrichment_data=enrichment_data,
            confidence_score=data.get('confidenceScore'),
            missing_fields=data.get('missingFields'),
            warnings=data.get('warnings'),
            requires_user_input=data.get('requiresUserInput', False),
            error_type=data.get('errorType'),
            error_message=data.get('errorMessage'),
            suggested_action=data.get('suggestedAction'),
            source_url=data.get('sourceUrl'),
            source_platform=data.get('sourcePlatform')
        )
