"""FRED (Federal Reserve Economic Data) API data models."""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class InterestRateData:
    """Interest rate and mortgage rate information."""

    federal_funds_rate: float  # Current federal funds effective rate
    prime_rate: float  # Bank prime loan rate
    mortgage_30yr: float  # 30-Year Fixed Rate Mortgage Average
    mortgage_15yr: float  # 15-Year Fixed Rate Mortgage Average
    treasury_10yr: float  # 10-Year Treasury Constant Maturity Rate
    treasury_2yr: float  # 2-Year Treasury Constant Maturity Rate

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            'federalFundsRate': self.federal_funds_rate,
            'primeRate': self.prime_rate,
            'mortgage30Year': self.mortgage_30yr,
            'mortgage15Year': self.mortgage_15yr,
            'treasury10Year': self.treasury_10yr,
            'treasury2Year': self.treasury_2yr
        }


@dataclass
class InflationData:
    """Consumer Price Index and inflation metrics."""

    cpi_all_items: float  # Consumer Price Index for All Urban Consumers
    cpi_yoy_change: float  # Year-over-year percentage change
    core_cpi: float  # CPI excluding food and energy
    pce_inflation: float  # Personal Consumption Expenditures inflation

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            'cpiAllItems': self.cpi_all_items,
            'cpiYoyChange': self.cpi_yoy_change,
            'coreCpi': self.core_cpi,
            'pceInflation': self.pce_inflation
        }


@dataclass
class HousingMarketData:
    """Housing market indicators."""

    housing_starts: int  # Housing starts (thousands of units)
    building_permits: int  # New private housing permits (thousands)
    home_sales_existing: int  # Existing home sales (thousands)
    home_sales_new: int  # New home sales (thousands)
    case_shiller_index: float  # S&P/Case-Shiller U.S. National Home Price Index

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            'housingStarts': self.housing_starts,
            'buildingPermits': self.building_permits,
            'existingHomeSales': self.home_sales_existing,
            'newHomeSales': self.home_sales_new,
            'caseShillerIndex': self.case_shiller_index
        }


@dataclass
class EconomicIndicators:
    """General economic health indicators."""

    gdp_real: float  # Real Gross Domestic Product (billions)
    gdp_growth_rate: float  # GDP growth rate (annual percentage)
    unemployment_rate: float  # Unemployment rate (percentage)
    labor_force_participation: float  # Labor force participation rate
    consumer_sentiment: float  # University of Michigan Consumer Sentiment Index

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            'realGdp': self.gdp_real,
            'gdpGrowthRate': self.gdp_growth_rate,
            'unemploymentRate': self.unemployment_rate,
            'laborForceParticipation': self.labor_force_participation,
            'consumerSentiment': self.consumer_sentiment
        }


@dataclass
class TimeSeriesDataPoint:
    """Single data point in a time series."""

    date: str  # ISO format date (YYYY-MM-DD)
    value: float  # The data value

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            'date': self.date,
            'value': self.value
        }


@dataclass
class MacroeconomicData:
    """Comprehensive macroeconomic data snapshot."""

    interest_rates: InterestRateData
    inflation: InflationData
    housing_market: HousingMarketData
    economic_indicators: EconomicIndicators
    last_updated: str  # ISO format timestamp
    data_notes: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            'interestRates': self.interest_rates.to_dict(),
            'inflation': self.inflation.to_dict(),
            'housingMarket': self.housing_market.to_dict(),
            'economicIndicators': self.economic_indicators.to_dict(),
            'lastUpdated': self.last_updated,
            'dataNotes': self.data_notes
        }
