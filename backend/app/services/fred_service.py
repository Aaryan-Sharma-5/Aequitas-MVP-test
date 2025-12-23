"""Federal Reserve Economic Data (FRED) API client service."""

import requests
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from app.models.fred_models import (
    InterestRateData,
    InflationData,
    HousingMarketData,
    EconomicIndicators,
    MacroeconomicData,
    TimeSeriesDataPoint
)


class FREDCache:
    """Simple in-memory cache with TTL support for FRED data."""

    def __init__(self):
        self._cache: Dict[str, tuple] = {}
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

    def set(self, key: str, value: dict, ttl_seconds: int = 3600):
        """Store value with TTL (default 1 hour for economic data)."""
        if len(self._cache) >= self._max_size:
            # Simple LRU: remove oldest entry
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]

        expiry = datetime.now() + timedelta(seconds=ttl_seconds)
        self._cache[key] = (value, expiry)

    def clear(self):
        """Clear all cached entries."""
        self._cache.clear()


class FREDService:
    """Service for interacting with Federal Reserve Economic Data (FRED) API."""

    # FRED API Series IDs for key economic indicators
    SERIES_IDS = {
        # Interest Rates
        'FEDFUNDS': 'federal_funds_rate',  # Federal Funds Effective Rate
        'DPRIME': 'prime_rate',  # Bank Prime Loan Rate
        'MORTGAGE30US': 'mortgage_30yr',  # 30-Year Fixed Rate Mortgage Average
        'MORTGAGE15US': 'mortgage_15yr',  # 15-Year Fixed Rate Mortgage Average
        'DGS10': 'treasury_10yr',  # 10-Year Treasury Constant Maturity Rate
        'DGS2': 'treasury_2yr',  # 2-Year Treasury Constant Maturity Rate

        # Inflation
        'CPIAUCSL': 'cpi_all_items',  # Consumer Price Index for All Urban Consumers
        'CPILFESL': 'core_cpi',  # CPI Less Food and Energy
        'PCEPI': 'pce_inflation',  # Personal Consumption Expenditures Price Index

        # Housing Market
        'HOUST': 'housing_starts',  # Housing Starts
        'PERMIT': 'building_permits',  # New Private Housing Permits
        'EXHOSLUSM495S': 'home_sales_existing',  # Existing Home Sales
        'HSN1F': 'home_sales_new',  # New One Family Houses Sold
        'CSUSHPISA': 'case_shiller_index',  # S&P/Case-Shiller U.S. National Home Price Index

        # Economic Indicators
        'GDPC1': 'gdp_real',  # Real Gross Domestic Product
        'UNRATE': 'unemployment_rate',  # Unemployment Rate
        'CIVPART': 'labor_force_participation',  # Labor Force Participation Rate
        'UMCSENT': 'consumer_sentiment',  # University of Michigan Consumer Sentiment
    }

    def __init__(self, api_key: str, base_url: str = 'https://api.stlouisfed.org/fred',
                 cache_ttl: int = 3600):
        """
        Initialize FRED API client.

        Args:
            api_key: FRED API key (required - get from https://fred.stlouisfed.org/docs/api/api_key.html)
            base_url: Base URL for FRED API
            cache_ttl: Cache time-to-live in seconds (default 1 hour)
        """
        if not api_key:
            raise ValueError("FRED API key is required. Get one at https://fred.stlouisfed.org/docs/api/api_key.html")

        self.api_key = api_key
        self.base_url = base_url
        self.cache_ttl = cache_ttl
        self.cache = FREDCache()

    def get_macroeconomic_snapshot(self) -> Optional[MacroeconomicData]:
        """
        Fetch a comprehensive snapshot of current macroeconomic conditions.

        Returns:
            MacroeconomicData object with all key indicators or None if error
        """
        # Check cache
        cache_key = "fred:macro_snapshot"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return self._dict_to_macro_data(cached_data)

        try:
            # Fetch all series data
            series_data = {}
            for series_id, field_name in self.SERIES_IDS.items():
                value = self._get_latest_observation(series_id)
                if value is not None:
                    series_data[field_name] = value

            if not series_data:
                return None

            # Calculate year-over-year CPI change
            cpi_yoy = self._calculate_yoy_change('CPIAUCSL')

            # Calculate GDP growth rate
            gdp_growth = self._calculate_yoy_change('GDPC1')

            # Build structured data objects
            interest_rates = InterestRateData(
                federal_funds_rate=series_data.get('federal_funds_rate', 0.0),
                prime_rate=series_data.get('prime_rate', 0.0),
                mortgage_30yr=series_data.get('mortgage_30yr', 0.0),
                mortgage_15yr=series_data.get('mortgage_15yr', 0.0),
                treasury_10yr=series_data.get('treasury_10yr', 0.0),
                treasury_2yr=series_data.get('treasury_2yr', 0.0)
            )

            inflation = InflationData(
                cpi_all_items=series_data.get('cpi_all_items', 0.0),
                cpi_yoy_change=cpi_yoy or 0.0,
                core_cpi=series_data.get('core_cpi', 0.0),
                pce_inflation=series_data.get('pce_inflation', 0.0)
            )

            housing_market = HousingMarketData(
                housing_starts=int(series_data.get('housing_starts', 0)),
                building_permits=int(series_data.get('building_permits', 0)),
                home_sales_existing=int(series_data.get('home_sales_existing', 0)),
                home_sales_new=int(series_data.get('home_sales_new', 0)),
                case_shiller_index=series_data.get('case_shiller_index', 0.0)
            )

            economic_indicators = EconomicIndicators(
                gdp_real=series_data.get('gdp_real', 0.0),
                gdp_growth_rate=gdp_growth or 0.0,
                unemployment_rate=series_data.get('unemployment_rate', 0.0),
                labor_force_participation=series_data.get('labor_force_participation', 0.0),
                consumer_sentiment=series_data.get('consumer_sentiment', 0.0)
            )

            macro_data = MacroeconomicData(
                interest_rates=interest_rates,
                inflation=inflation,
                housing_market=housing_market,
                economic_indicators=economic_indicators,
                last_updated=datetime.now().isoformat(),
                data_notes="Data sourced from Federal Reserve Economic Data (FRED)"
            )

            # Cache the result
            self.cache.set(cache_key, self._macro_data_to_dict(macro_data), self.cache_ttl)

            return macro_data

        except Exception as e:
            print(f"Error fetching FRED macroeconomic data: {str(e)}")
            return None

    def get_time_series(self, series_id: str, start_date: Optional[str] = None,
                       end_date: Optional[str] = None, limit: int = 100) -> Optional[List[TimeSeriesDataPoint]]:
        """
        Fetch historical time series data for a specific FRED series.

        Args:
            series_id: FRED series ID (e.g., 'MORTGAGE30US')
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)
            limit: Maximum number of observations to return

        Returns:
            List of TimeSeriesDataPoint objects or None if error
        """
        cache_key = f"fred:series:{series_id}:{start_date}:{end_date}:{limit}"
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return [TimeSeriesDataPoint(**point) for point in cached_data]

        try:
            params = {
                'series_id': series_id,
                'api_key': self.api_key,
                'file_type': 'json',
                'limit': limit,
                'sort_order': 'desc'  # Most recent first
            }

            if start_date:
                params['observation_start'] = start_date
            if end_date:
                params['observation_end'] = end_date

            url = f"{self.base_url}/series/observations"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            observations = data.get('observations', [])

            time_series = []
            for obs in observations:
                # FRED returns '.' for missing values
                if obs['value'] != '.':
                    time_series.append(TimeSeriesDataPoint(
                        date=obs['date'],
                        value=float(obs['value'])
                    ))

            # Reverse to chronological order (oldest to newest)
            time_series.reverse()

            # Cache the result
            self.cache.set(cache_key, [point.to_dict() for point in time_series], self.cache_ttl)

            return time_series

        except Exception as e:
            print(f"Error fetching FRED time series for {series_id}: {str(e)}")
            return None

    def get_mortgage_rates_history(self, months: int = 12) -> Optional[List[TimeSeriesDataPoint]]:
        """
        Get historical 30-year mortgage rates.

        Args:
            months: Number of months of history to fetch (default 12)

        Returns:
            List of TimeSeriesDataPoint objects with mortgage rate history
        """
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=months * 30)).strftime('%Y-%m-%d')

        return self.get_time_series(
            series_id='MORTGAGE30US',
            start_date=start_date,
            end_date=end_date,
            limit=months * 5  # Weekly data, ~4-5 observations per month
        )

    def _get_latest_observation(self, series_id: str) -> Optional[float]:
        """
        Get the most recent observation for a FRED series.

        Args:
            series_id: FRED series ID

        Returns:
            Latest value as float or None if error
        """
        try:
            params = {
                'series_id': series_id,
                'api_key': self.api_key,
                'file_type': 'json',
                'limit': 1,
                'sort_order': 'desc'
            }

            url = f"{self.base_url}/series/observations"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            observations = data.get('observations', [])

            if observations and observations[0]['value'] != '.':
                return float(observations[0]['value'])

            return None

        except Exception as e:
            print(f"Error fetching latest observation for {series_id}: {str(e)}")
            return None

    def _calculate_yoy_change(self, series_id: str) -> Optional[float]:
        """
        Calculate year-over-year percentage change for a series.

        Args:
            series_id: FRED series ID

        Returns:
            Year-over-year percentage change or None if error
        """
        try:
            # Get current and year-ago values
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=400)).strftime('%Y-%m-%d')

            params = {
                'series_id': series_id,
                'api_key': self.api_key,
                'file_type': 'json',
                'observation_start': start_date,
                'observation_end': end_date,
                'sort_order': 'desc'
            }

            url = f"{self.base_url}/series/observations"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            observations = data.get('observations', [])

            # Filter out missing values
            valid_obs = [obs for obs in observations if obs['value'] != '.']

            if len(valid_obs) < 2:
                return None

            # Most recent value
            current_value = float(valid_obs[0]['value'])

            # Find value from approximately 1 year ago
            # Look for observation closest to 365 days ago
            target_date = datetime.now() - timedelta(days=365)
            year_ago_value = None

            for obs in valid_obs[1:]:
                obs_date = datetime.strptime(obs['date'], '%Y-%m-%d')
                if obs_date <= target_date:
                    year_ago_value = float(obs['value'])
                    break

            if year_ago_value and year_ago_value != 0:
                yoy_change = ((current_value - year_ago_value) / year_ago_value) * 100
                return round(yoy_change, 2)

            return None

        except Exception as e:
            print(f"Error calculating YoY change for {series_id}: {str(e)}")
            return None

    def _macro_data_to_dict(self, data: MacroeconomicData) -> dict:
        """Convert MacroeconomicData to dictionary for caching."""
        return data.to_dict()

    def _dict_to_macro_data(self, data: dict) -> MacroeconomicData:
        """Convert dictionary back to MacroeconomicData object."""
        return MacroeconomicData(
            interest_rates=InterestRateData(**{
                k.replace(k[0], k[0].lower()).replace('Rate', '_rate').replace('Year', '_year').replace('Funds', '_funds')
                if k[0].isupper() else k: v
                for k, v in data['interestRates'].items()
            }) if isinstance(data.get('interestRates'), dict) else InterestRateData(
                federal_funds_rate=data['interestRates'].get('federalFundsRate', 0),
                prime_rate=data['interestRates'].get('primeRate', 0),
                mortgage_30yr=data['interestRates'].get('mortgage30Year', 0),
                mortgage_15yr=data['interestRates'].get('mortgage15Year', 0),
                treasury_10yr=data['interestRates'].get('treasury10Year', 0),
                treasury_2yr=data['interestRates'].get('treasury2Year', 0)
            ),
            inflation=InflationData(
                cpi_all_items=data['inflation'].get('cpiAllItems', 0),
                cpi_yoy_change=data['inflation'].get('cpiYoyChange', 0),
                core_cpi=data['inflation'].get('coreCpi', 0),
                pce_inflation=data['inflation'].get('pceInflation', 0)
            ),
            housing_market=HousingMarketData(
                housing_starts=data['housingMarket'].get('housingStarts', 0),
                building_permits=data['housingMarket'].get('buildingPermits', 0),
                home_sales_existing=data['housingMarket'].get('existingHomeSales', 0),
                home_sales_new=data['housingMarket'].get('newHomeSales', 0),
                case_shiller_index=data['housingMarket'].get('caseShillerIndex', 0)
            ),
            economic_indicators=EconomicIndicators(
                gdp_real=data['economicIndicators'].get('realGdp', 0),
                gdp_growth_rate=data['economicIndicators'].get('gdpGrowthRate', 0),
                unemployment_rate=data['economicIndicators'].get('unemploymentRate', 0),
                labor_force_participation=data['economicIndicators'].get('laborForceParticipation', 0),
                consumer_sentiment=data['economicIndicators'].get('consumerSentiment', 0)
            ),
            last_updated=data['lastUpdated'],
            data_notes=data.get('dataNotes')
        )
