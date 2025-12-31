"""
Capital Appreciation Service
Projects future property values and calculates capital gains

Academic Research Basis:
- D1 capital gains: 0.99-5.50% annually (US)
- D10 capital gains: -0.10-1.95% annually (US)
- D1-D10 spread: 109-355 basis points
- Low-rent properties appreciate faster despite lower initial prices
"""

from typing import Dict, Optional
from datetime import datetime
from app.database import db, RiskBenchmarkData, DealModel


class CapitalAppreciationService:
    """
    Service for projecting property value appreciation and calculating capital gains
    """

    @staticmethod
    def project_future_value(
        current_value: float,
        rent_decile: int,
        years: int = 10,
        geography: str = 'US'
    ) -> Dict:
        """
        Project future property value based on rent decile

        Args:
            current_value: Current property value
            rent_decile: Property's rent tier (1-10)
            years: Projection horizon (default 10 years)
            geography: Geographic market

        Returns:
            Dictionary with projections:
                {
                    'current_value': 1000000,
                    'projected_value_yr1': 1045000,
                    'projected_value_yr5': 1246182,
                    'projected_value_yr10': 1552969,
                    'annualized_appreciation_rate': 4.5,
                    'total_appreciation_pct': 55.3,
                    'appreciation_range_min': 3.2,
                    'appreciation_range_max': 5.8
                }
        """

        # Get benchmark appreciation rates for this decile
        benchmark = RiskBenchmarkData.query.filter_by(
            rent_decile=rent_decile,
            geography=geography
        ).first()

        if benchmark:
            # Use midpoint of benchmark range
            capital_gain_min = benchmark.capital_gain_min or 0.0
            capital_gain_max = benchmark.capital_gain_max or 0.0
            annual_rate = (capital_gain_min + capital_gain_max) / 2
        else:
            # Fallback estimates based on research
            annual_rate = CapitalAppreciationService._get_default_appreciation_rate(rent_decile)
            capital_gain_min = annual_rate - 1.0
            capital_gain_max = annual_rate + 1.0

        # Convert percentage to decimal
        annual_rate_decimal = annual_rate / 100

        # Project values at different horizons
        projected_yr1 = current_value * (1 + annual_rate_decimal) ** 1
        projected_yr5 = current_value * (1 + annual_rate_decimal) ** 5
        projected_yr10 = current_value * (1 + annual_rate_decimal) ** 10
        projected_custom = current_value * (1 + annual_rate_decimal) ** years if years != 10 else projected_yr10

        # Calculate total appreciation
        total_appreciation_pct = ((projected_custom - current_value) / current_value) * 100

        return {
            'current_value': round(current_value, 2),
            'projected_value_yr1': round(projected_yr1, 2),
            'projected_value_yr5': round(projected_yr5, 2),
            'projected_value_yr10': round(projected_yr10, 2),
            'projected_value_custom': round(projected_custom, 2) if years != 10 else None,
            'years_projected': years,
            'annualized_appreciation_rate': round(annual_rate, 2),
            'total_appreciation_pct': round(total_appreciation_pct, 2),
            'appreciation_range_min': round(capital_gain_min, 2),
            'appreciation_range_max': round(capital_gain_max, 2)
        }

    @staticmethod
    def _get_default_appreciation_rate(rent_decile: int) -> float:
        """
        Get default appreciation rate when benchmark unavailable

        Based on US research findings

        Args:
            rent_decile: 1-10

        Returns:
            Annual appreciation rate as percentage
        """

        # Appreciation rates decrease as rent increases (counterintuitive but research-proven)
        # D1: 3.25% average, D10: 0.93% average
        appreciation_rates = {
            1: 3.25,   # (0.99 + 5.50) / 2
            2: 3.04,   # (0.92 + 5.15) / 2
            3: 2.66,   # (0.71 + 4.60) / 2
            4: 2.34,   # (0.60 + 4.07) / 2
            5: 2.11,   # (0.48 + 3.74) / 2
            6: 1.79,   # (0.39 + 3.18) / 2
            7: 1.69,   # (0.46 + 2.91) / 2
            8: 1.48,   # (0.40 + 2.55) / 2
            9: 1.23,   # (0.32 + 2.14) / 2
            10: 0.93   # (-0.10 + 1.95) / 2
        }

        return appreciation_rates.get(rent_decile, 2.0)

    @staticmethod
    def project_noi_growth(
        current_noi: float,
        rent_decile: int,
        property_age: int,
        years: int = 10
    ) -> Dict:
        """
        Project Net Operating Income (NOI) growth

        Research findings:
        - Older properties have higher NOI growth (from low base)
        - Low-rent properties have more stable NOI growth
        - Model explains only ~7% of variance (high uncertainty)

        Args:
            current_noi: Current annual NOI
            rent_decile: Property's rent tier
            property_age: Age of property in years
            years: Projection horizon

        Returns:
            NOI growth projections and rates
        """

        # Base NOI growth rate (2% national average)
        base_growth = 2.0

        # Age effect: Older properties grow faster (mean reversion)
        # Properties >50 years: +0.5%, 30-50 years: +0.2%, <30 years: 0%
        if property_age > 50:
            age_adjustment = 0.5
        elif property_age > 30:
            age_adjustment = 0.2
        else:
            age_adjustment = 0.0

        # Rent tier effect: Low-rent more stable but slightly higher growth
        # D1-D3: +0.3%, D4-D7: 0%, D8-D10: -0.2%
        if rent_decile <= 3:
            tier_adjustment = 0.3
        elif rent_decile <= 7:
            tier_adjustment = 0.0
        else:
            tier_adjustment = -0.2

        # Combined annual growth rate
        annual_growth_rate = base_growth + age_adjustment + tier_adjustment

        # Project NOI
        growth_decimal = annual_growth_rate / 100
        projected_noi_yr1 = current_noi * (1 + growth_decimal) ** 1
        projected_noi_yr5 = current_noi * (1 + growth_decimal) ** 5
        projected_noi_yr10 = current_noi * (1 + growth_decimal) ** 10
        projected_noi_custom = current_noi * (1 + growth_decimal) ** years

        return {
            'current_noi': round(current_noi, 2),
            'projected_noi_yr1': round(projected_noi_yr1, 2),
            'projected_noi_yr5': round(projected_noi_yr5, 2),
            'projected_noi_yr10': round(projected_noi_yr10, 2),
            'projected_noi_custom': round(projected_noi_custom, 2) if years != 10 else None,
            'annual_growth_rate': round(annual_growth_rate, 2),
            'base_growth': base_growth,
            'age_adjustment': age_adjustment,
            'tier_adjustment': tier_adjustment,
            'years_projected': years
        }

    @staticmethod
    def calculate_for_deal(
        deal_id: int,
        rent_decile: int,
        holding_period: int = 10
    ) -> Dict:
        """
        Calculate complete capital appreciation analysis for a deal

        Args:
            deal_id: Deal ID to analyze
            rent_decile: Property's rent tier
            holding_period: Years to hold property

        Returns:
            Complete appreciation analysis
        """

        # Fetch deal from database
        deal = DealModel.query.get(deal_id)
        if not deal:
            raise ValueError(f"Deal {deal_id} not found")

        # Current property value
        current_value = deal.purchase_price or 0.0
        if current_value <= 0:
            raise ValueError("Property value must be positive")

        # Property age for NOI growth
        current_year = datetime.now().year
        year_built = deal.year_built or deal.construction_year or current_year - 30
        property_age = current_year - year_built

        # Project property value
        value_projection = CapitalAppreciationService.project_future_value(
            current_value=current_value,
            rent_decile=rent_decile,
            years=holding_period,
            geography='US'
        )

        # Calculate current NOI (simplified)
        monthly_rent = deal.monthly_rent or 0.0
        vacancy_rate = deal.vacancy_rate or 0.05
        num_units = deal.number_of_units or 1

        annual_gross_income = monthly_rent * 12 * num_units
        annual_effective_income = annual_gross_income * (1 - vacancy_rate)

        # Estimate operating expenses (use 40% of EGI as rough estimate)
        operating_expense_ratio = 0.40
        annual_operating_expenses = annual_effective_income * operating_expense_ratio
        current_noi = annual_effective_income - annual_operating_expenses

        # Project NOI growth
        noi_projection = CapitalAppreciationService.project_noi_growth(
            current_noi=current_noi,
            rent_decile=rent_decile,
            property_age=property_age,
            years=holding_period
        )

        # Calculate capital gain yield (annualized)
        total_gain = value_projection['projected_value_custom'] or value_projection['projected_value_yr10']
        capital_gain_yield_annual = value_projection['annualized_appreciation_rate']

        return {
            'value_projection': value_projection,
            'noi_projection': noi_projection,
            'capital_gain_yield_annual': capital_gain_yield_annual,
            'property_age': property_age,
            'holding_period': holding_period
        }

    @staticmethod
    def apply_aging_adjustment(
        base_appreciation: float,
        property_age: int,
        years_to_project: int
    ) -> float:
        """
        Apply aging depreciation adjustment to appreciation rate

        Older properties depreciate faster, reducing appreciation

        Args:
            base_appreciation: Base appreciation rate (%)
            property_age: Current age of property
            years_to_project: How many years to project

        Returns:
            Adjusted appreciation rate
        """

        # Age depreciation factor
        # Properties lose 0.05% appreciation per decade of age
        age_decades = property_age / 10
        age_penalty = age_decades * 0.05

        # Future aging during holding period
        future_age_decades = (property_age + years_to_project) / 10
        future_age_penalty = (future_age_decades - age_decades) * 0.05

        # Total adjustment
        total_adjustment = (age_penalty + future_age_penalty) / 2

        adjusted_rate = base_appreciation - total_adjustment

        return round(adjusted_rate, 2)

    @staticmethod
    def compare_to_benchmark(
        calculated_capital_gain: float,
        rent_decile: int,
        geography: str = 'US'
    ) -> Dict:
        """
        Compare calculated capital gain to benchmark ranges

        Args:
            calculated_capital_gain: Annualized appreciation rate
            rent_decile: Property's rent tier
            geography: Geographic market

        Returns:
            Comparison results
        """

        # Get benchmark data
        benchmark = RiskBenchmarkData.query.filter_by(
            rent_decile=rent_decile,
            geography=geography
        ).first()

        if not benchmark:
            return {
                'benchmark_min': None,
                'benchmark_max': None,
                'calculated': calculated_capital_gain,
                'position': 'Unknown',
                'percentile_in_range': None
            }

        benchmark_min = benchmark.capital_gain_min
        benchmark_max = benchmark.capital_gain_max

        # Determine position
        if calculated_capital_gain < benchmark_min:
            position = 'Below'
            percentile = 0.0
        elif calculated_capital_gain > benchmark_max:
            position = 'Above'
            percentile = 100.0
        else:
            position = 'Within'
            range_size = benchmark_max - benchmark_min
            if range_size > 0:
                percentile = ((calculated_capital_gain - benchmark_min) / range_size) * 100
            else:
                percentile = 50.0

        return {
            'benchmark_min': benchmark_min,
            'benchmark_max': benchmark_max,
            'calculated': calculated_capital_gain,
            'position': position,
            'percentile_in_range': round(percentile, 1)
        }

    @staticmethod
    def calculate_exit_value(
        current_value: float,
        noi_at_exit: float,
        exit_cap_rate: float
    ) -> Dict:
        """
        Calculate property value at exit using NOI and cap rate

        Exit Value = NOI / Cap Rate

        Args:
            current_value: Current property value
            noi_at_exit: Projected NOI at time of sale
            exit_cap_rate: Expected cap rate at exit (as decimal, e.g., 0.06)

        Returns:
            Exit value analysis
        """

        if exit_cap_rate <= 0:
            raise ValueError("Exit cap rate must be positive")

        exit_value = noi_at_exit / exit_cap_rate

        # Calculate total appreciation
        total_appreciation = exit_value - current_value
        appreciation_pct = (total_appreciation / current_value) * 100

        return {
            'current_value': round(current_value, 2),
            'noi_at_exit': round(noi_at_exit, 2),
            'exit_cap_rate': round(exit_cap_rate * 100, 2),
            'exit_value': round(exit_value, 2),
            'total_appreciation': round(total_appreciation, 2),
            'appreciation_pct': round(appreciation_pct, 2)
        }
