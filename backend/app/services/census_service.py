"""US Census Bureau API client service."""

import requests
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from app.models.census_models import (
    PopulationData,
    IncomeData,
    HousingData,
    DemographicData
)


class CensusCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self):
        self._cache: Dict[str, tuple] = {}
        self._max_size = 1000

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


class CensusService:
    """Service for interacting with US Census Bureau API."""

    # ACS 5-Year Census Variables
    POPULATION_VARS = {
        'B01003_001E': 'total_population',
        'B11001_001E': 'total_households',
        'B25010_001E': 'avg_household_size',
    }

    INCOME_VARS = {
        'B19013_001E': 'median_household_income',
        'B19001_002E': 'income_under_10k',
        'B19001_003E': 'income_10k_15k',
        'B19001_004E': 'income_15k_20k',
        'B19001_005E': 'income_20k_25k',
        'B19001_006E': 'income_25k_30k',
        'B19001_007E': 'income_30k_35k',
        'B19001_008E': 'income_35k_40k',
        'B19001_009E': 'income_40k_45k',
        'B19001_010E': 'income_45k_50k',
        'B19001_011E': 'income_50k_60k',
        'B19001_012E': 'income_60k_75k',
        'B19001_013E': 'income_75k_100k',
        'B19001_014E': 'income_100k_125k',
        'B19001_015E': 'income_125k_150k',
        'B19001_016E': 'income_150k_200k',
        'B19001_017E': 'income_200k_plus',
    }

    HOUSING_VARS = {
        'B25077_001E': 'median_home_value',
        'B25064_001E': 'median_gross_rent',
        'B25001_001E': 'total_housing_units',
        'B25002_002E': 'occupied_units',
        'B25002_003E': 'vacant_units',
        'B25003_002E': 'owner_occupied',
        'B25003_003E': 'renter_occupied',
    }

    EMPLOYMENT_VARS = {
        'B23025_005E': 'unemployment_count',
        'B23025_003E': 'labor_force',
    }

    def __init__(self, api_key: str = '', base_url: str = 'https://api.census.gov/data',
                 api_year: str = '2022', cache_ttl: int = 86400):
        """
        Initialize Census API client.

        Args:
            api_key: Census API key (optional, but recommended for higher rate limits)
            base_url: Base URL for Census API
            api_year: Year of ACS 5-Year data to use
            cache_ttl: Cache time-to-live in seconds (default 24 hours)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.api_year = api_year
        self.cache_ttl = cache_ttl
        self.cache = CensusCache()

        # Construct full API endpoint URL
        self.endpoint = f"{base_url}/{api_year}/acs/acs5"

    def get_demographics_by_zipcode(self, zipcode: str) -> Optional[DemographicData]:
        """
        Fetch comprehensive demographic data for a ZIP code.

        Args:
            zipcode: 5-digit ZIP code

        Returns:
            DemographicData object or None if error
        """
        # Validate ZIP code format
        if not zipcode or len(zipcode) != 5 or not zipcode.isdigit():
            raise ValueError(f"Invalid ZIP code format: {zipcode}")

        # Check cache
        cache_key = f"census:{zipcode}:{self.api_year}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return self._dict_to_demographic_data(cached_data)

        try:
            # Fetch all variables in one request
            all_vars = {**self.POPULATION_VARS, **self.INCOME_VARS,
                       **self.HOUSING_VARS, **self.EMPLOYMENT_VARS}

            raw_data = self._fetch_census_data(
                variables=list(all_vars.keys()),
                geography=f"zip code tabulation area:{zipcode}"
            )

            if not raw_data:
                return None

            # Parse and structure the data
            demographic_data = self._parse_demographic_data(zipcode, raw_data, all_vars)

            # Cache the result
            self.cache.set(cache_key, self._demographic_data_to_dict(demographic_data),
                          self.cache_ttl)

            return demographic_data

        except Exception as e:
            print(f"Error fetching Census data for ZIP {zipcode}: {str(e)}")
            return None

    def _fetch_census_data(self, variables: List[str], geography: str) -> Optional[dict]:
        """
        Make request to Census API.

        Args:
            variables: List of Census variable codes
            geography: Geographic filter (e.g., "zip code tabulation area:95814")

        Returns:
            Raw Census API response data
        """
        # Build query parameters
        params = {
            'get': ','.join(variables),
            'for': geography,
        }

        if self.api_key:
            params['key'] = self.api_key

        try:
            response = requests.get(self.endpoint, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Census API returns [[headers], [values]]
            if len(data) < 2:
                return None

            headers = data[0]
            values = data[1]

            # Convert to dictionary
            return dict(zip(headers, values))

        except requests.exceptions.RequestException as e:
            print(f"Census API request failed: {str(e)}")
            return None
        except (ValueError, IndexError) as e:
            print(f"Failed to parse Census API response: {str(e)}")
            return None

    def _parse_demographic_data(self, zipcode: str, raw_data: dict,
                                var_mapping: dict) -> DemographicData:
        """Parse raw Census data into structured DemographicData object."""

        def safe_int(value, default=0):
            """Safely convert to int, handling null/-666666666 values."""
            try:
                if value is None or value == -666666666:
                    return default
                return int(value)
            except (ValueError, TypeError):
                return default

        def safe_float(value, default=0.0):
            """Safely convert to float, handling null/-666666666 values."""
            try:
                if value is None or value == -666666666:
                    return default
                return float(value)
            except (ValueError, TypeError):
                return default

        # Population data
        total_pop = safe_int(raw_data.get('B01003_001E'))
        total_households = safe_int(raw_data.get('B11001_001E'))
        avg_hh_size = safe_float(raw_data.get('B25010_001E'))

        population = PopulationData(
            total_population=total_pop,
            total_households=total_households,
            avg_household_size=avg_hh_size
        )

        # Income data
        median_income = safe_int(raw_data.get('B19013_001E'))

        # Calculate AMI thresholds
        ami_30 = int(median_income * 0.30)
        ami_50 = int(median_income * 0.50)
        ami_60 = int(median_income * 0.60)
        ami_80 = int(median_income * 0.80)

        # Income distribution
        income_dist = {
            'under_10k': safe_int(raw_data.get('B19001_002E')),
            '10k_15k': safe_int(raw_data.get('B19001_003E')),
            '15k_20k': safe_int(raw_data.get('B19001_004E')),
            '20k_25k': safe_int(raw_data.get('B19001_005E')),
            '25k_30k': safe_int(raw_data.get('B19001_006E')),
            '30k_35k': safe_int(raw_data.get('B19001_007E')),
            '35k_40k': safe_int(raw_data.get('B19001_008E')),
            '40k_45k': safe_int(raw_data.get('B19001_009E')),
            '45k_50k': safe_int(raw_data.get('B19001_010E')),
            '50k_60k': safe_int(raw_data.get('B19001_011E')),
            '60k_75k': safe_int(raw_data.get('B19001_012E')),
            '75k_100k': safe_int(raw_data.get('B19001_013E')),
            '100k_125k': safe_int(raw_data.get('B19001_014E')),
            '125k_150k': safe_int(raw_data.get('B19001_015E')),
            '150k_200k': safe_int(raw_data.get('B19001_016E')),
            '200k_plus': safe_int(raw_data.get('B19001_017E')),
        }

        income = IncomeData(
            median_household_income=median_income,
            ami_30_percent=ami_30,
            ami_50_percent=ami_50,
            ami_60_percent=ami_60,
            ami_80_percent=ami_80,
            income_distribution=income_dist
        )

        # Housing data
        median_home_val = safe_int(raw_data.get('B25077_001E'))
        median_rent = safe_int(raw_data.get('B25064_001E'))
        total_units = safe_int(raw_data.get('B25001_001E'))
        occupied = safe_int(raw_data.get('B25002_002E'))
        vacant = safe_int(raw_data.get('B25002_003E'))
        owner_occ = safe_int(raw_data.get('B25003_002E'))
        renter_occ = safe_int(raw_data.get('B25003_003E'))

        # Calculate occupancy rate
        occupancy_rate = (occupied / total_units * 100) if total_units > 0 else 0.0

        housing = HousingData(
            median_home_value=median_home_val,
            median_gross_rent=median_rent,
            total_housing_units=total_units,
            occupied_units=occupied,
            vacant_units=vacant,
            owner_occupied=owner_occ,
            renter_occupied=renter_occ,
            occupancy_rate=round(occupancy_rate, 2)
        )

        # Employment data
        unemployment_count = safe_int(raw_data.get('B23025_005E'))
        labor_force = safe_int(raw_data.get('B23025_003E'))
        unemployment_rate = (unemployment_count / labor_force * 100) if labor_force > 0 else 0.0

        # Create complete demographic data object
        return DemographicData(
            zipcode=zipcode,
            population=population,
            income=income,
            housing=housing,
            unemployment_rate=round(unemployment_rate, 2),
            data_year=f"{int(self.api_year)-4}-{self.api_year}",  # ACS 5-Year span
            last_updated=datetime.now().isoformat()
        )

    def _demographic_data_to_dict(self, data: DemographicData) -> dict:
        """Convert DemographicData to dictionary for caching."""
        return data.to_dict()

    def _dict_to_demographic_data(self, data: dict) -> DemographicData:
        """Convert dictionary back to DemographicData object."""
        return DemographicData(
            zipcode=data['zipcode'],
            population=PopulationData(**data['population']),
            income=IncomeData(**data['income']),
            housing=HousingData(**data['housing']),
            unemployment_rate=data['unemploymentRate'],
            data_year=data['dataYear'],
            last_updated=data['lastUpdated']
        )

    def calculate_ami_rent_limit(self, zipcode: str, ami_percent: int,
                                 bedrooms: int = 2) -> Optional[dict]:
        """
        Calculate AMI-based rent limits for a property.

        Args:
            zipcode: 5-digit ZIP code
            ami_percent: AMI percentage (30, 50, 60, or 80)
            bedrooms: Number of bedrooms (default 2)

        Returns:
            Dictionary with AMI calculations
        """
        demographics = self.get_demographics_by_zipcode(zipcode)
        if not demographics:
            return None

        # Get appropriate AMI threshold
        ami_thresholds = {
            30: demographics.income.ami_30_percent,
            50: demographics.income.ami_50_percent,
            60: demographics.income.ami_60_percent,
            80: demographics.income.ami_80_percent,
        }

        ami_income_limit = ami_thresholds.get(ami_percent)
        if not ami_income_limit:
            raise ValueError(f"Invalid AMI percent: {ami_percent}. Must be 30, 50, 60, or 80.")

        # Calculate max rent (typically 30% of monthly income)
        max_monthly_rent = int((ami_income_limit / 12) * 0.30)

        return {
            'zipcode': zipcode,
            'ami_percent': ami_percent,
            'ami_income_limit': ami_income_limit,
            'max_rent': max_monthly_rent,
            'area_median_income': demographics.income.median_household_income,
            'bedrooms': bedrooms
        }
