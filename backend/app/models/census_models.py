"""Data models for US Census Bureau API responses."""

from dataclasses import dataclass, asdict
from typing import Dict, Optional
from datetime import datetime


@dataclass
class PopulationData:
    """Population and household statistics."""
    total_population: int
    total_households: int
    avg_household_size: float


@dataclass
class IncomeData:
    """Income statistics and AMI calculations."""
    median_household_income: int
    ami_30_percent: int
    ami_50_percent: int
    ami_60_percent: int
    ami_80_percent: int
    income_distribution: Dict[str, int]


@dataclass
class HousingData:
    """Housing market characteristics."""
    median_home_value: int
    median_gross_rent: int
    total_housing_units: int
    occupied_units: int
    vacant_units: int
    owner_occupied: int
    renter_occupied: int
    occupancy_rate: float


@dataclass
class DemographicData:
    """Complete demographic profile for a geographic area."""
    zipcode: str
    population: PopulationData
    income: IncomeData
    housing: HousingData
    unemployment_rate: float
    data_year: str
    last_updated: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'zipcode': self.zipcode,
            'population': asdict(self.population),
            'income': asdict(self.income),
            'housing': asdict(self.housing),
            'unemploymentRate': self.unemployment_rate,
            'dataYear': self.data_year,
            'lastUpdated': self.last_updated
        }
