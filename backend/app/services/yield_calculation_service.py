"""
Yield Calculation Service
Calculates gross and net yields with detailed cost decomposition

Academic Research Basis:
- Gross yield spreads are large (2.1-2.7 pp between D1 and D10)
- Cost components follow different patterns across rent distribution
- D1 net yield: 3.55-5.70%, D10 net yield: 2.66-5.09%
- After costs, D1-D10 spread remains: 89-113 basis points
"""

from typing import Dict, Optional
from app.database import db, RiskBenchmarkData, DealModel


class YieldCalculationService:
    """
    Service for calculating property yields and cost components
    """

    @staticmethod
    def calculate_gross_yield(annual_rent: float, property_value: float) -> float:
        """
        Calculate gross yield (annual rent / property value)

        Args:
            annual_rent: Total annual rental income
            property_value: Property purchase or market value

        Returns:
            Gross yield as percentage (e.g., 5.5 for 5.5%)
        """
        if property_value <= 0:
            raise ValueError("Property value must be positive")

        gross_yield = (annual_rent / property_value) * 100
        return round(gross_yield, 2)

    @staticmethod
    def calculate_cost_components(
        rent_decile: int,
        num_units: int = 1,
        property_value: Optional[float] = None,
        annual_rent: Optional[float] = None,
        geography: str = 'US'
    ) -> Dict:
        """
        Calculate all operating cost components as percentages

        Args:
            rent_decile: Property's rent tier (1-10)
            num_units: Number of units in property
            property_value: Property value (for tax calculations)
            annual_rent: Annual rental income (for percentage calculations)
            geography: Geographic market ('US', 'Belgium', 'Netherlands')

        Returns:
            Dictionary with all cost components as percentages:
                {
                    'maintenance_cost_pct': 1.5,
                    'property_tax_pct': 1.2,
                    'turnover_cost_pct': 2.5,
                    'default_cost_pct': 0.9,
                    'management_cost_pct': 6.0,
                    'total_cost_pct': 12.1
                }
        """

        # Get benchmark costs for this decile
        benchmark = RiskBenchmarkData.query.filter_by(
            rent_decile=rent_decile,
            geography=geography
        ).first()

        if not benchmark:
            # Fallback to default cost estimates if no benchmark data
            costs = YieldCalculationService._get_default_costs(rent_decile, num_units)
        else:
            costs = {
                'maintenance_cost_pct': benchmark.maintenance_cost_pct or 0.0,
                'turnover_cost_pct': benchmark.turnover_cost_pct or 0.0,
                'default_cost_pct': benchmark.default_cost_pct or 0.0,
            }

        # Property tax (estimate based on property value and location)
        # US average is ~1.1% of property value annually
        # Higher-value properties often in areas with higher rates
        if property_value and annual_rent:
            # Property tax as % of rent varies inversely with rent level
            # Low-rent properties have higher tax burden relative to rent
            tax_rate = 0.011  # 1.1% of property value
            property_tax_annual = property_value * tax_rate
            costs['property_tax_pct'] = (property_tax_annual / annual_rent) * 100
        else:
            # Estimate: higher for low-rent properties
            costs['property_tax_pct'] = 1.5 if rent_decile <= 5 else 1.0

        # Management costs (scale economies)
        costs['management_cost_pct'] = YieldCalculationService._calculate_management_cost(num_units)

        # Calculate total
        costs['total_cost_pct'] = sum([
            costs['maintenance_cost_pct'],
            costs['property_tax_pct'],
            costs['turnover_cost_pct'],
            costs['default_cost_pct'],
            costs['management_cost_pct']
        ])

        # Round all values
        return {k: round(v, 2) for k, v in costs.items()}

    @staticmethod
    def _calculate_management_cost(num_units: int) -> float:
        """
        Calculate management cost percentage based on portfolio size

        Research findings:
        - Single property: 6-7%
        - 2-9 properties: 5%
        - 10+ properties: 4%

        Args:
            num_units: Number of units

        Returns:
            Management cost as percentage of rent
        """
        if num_units >= 10:
            return 4.0
        elif num_units >= 2:
            return 5.0
        else:
            return 6.5

    @staticmethod
    def _get_default_costs(rent_decile: int, num_units: int) -> Dict:
        """
        Get default cost estimates when benchmark data unavailable

        These are based on research averages for US market

        Args:
            rent_decile: 1-10
            num_units: Number of units

        Returns:
            Dictionary with cost component estimates
        """

        # Maintenance costs decrease with rent level
        # D1: 1.5%, D10: 0.6%
        maintenance_range = [1.5, 1.4, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 0.6]
        maintenance_pct = maintenance_range[rent_decile - 1]

        # Turnover costs relatively stable
        # D1: 2.5%, D10: 1.8%
        turnover_range = [2.5, 2.4, 2.3, 2.2, 2.1, 2.0, 1.9, 1.8, 1.8, 1.8]
        turnover_pct = turnover_range[rent_decile - 1]

        # Default costs slightly higher for low-rent
        # D1: 0.9%, D10: 0.5%
        default_range = [0.9, 0.9, 0.8, 0.8, 0.7, 0.7, 0.6, 0.6, 0.5, 0.5]
        default_pct = default_range[rent_decile - 1]

        return {
            'maintenance_cost_pct': maintenance_pct,
            'turnover_cost_pct': turnover_pct,
            'default_cost_pct': default_pct
        }

    @staticmethod
    def calculate_net_yield(gross_yield: float, cost_components: Dict) -> float:
        """
        Calculate net yield (gross yield minus all costs)

        Args:
            gross_yield: Gross yield percentage
            cost_components: Dictionary with total_cost_pct

        Returns:
            Net yield as percentage
        """
        total_costs = cost_components.get('total_cost_pct', 0.0)
        net_yield = gross_yield - total_costs

        return round(net_yield, 2)

    @staticmethod
    def calculate_yields_for_deal(deal_id: int, rent_decile: int) -> Dict:
        """
        Calculate complete yield analysis for a deal

        Args:
            deal_id: Deal ID to analyze
            rent_decile: Property's rent tier classification

        Returns:
            Complete yield breakdown:
                {
                    'gross_yield': 7.2,
                    'cost_components': {...},
                    'net_yield': 4.5,
                    'annual_rent': 86400,
                    'property_value': 1200000
                }
        """

        # Fetch deal from database
        deal = DealModel.query.get(deal_id)
        if not deal:
            raise ValueError(f"Deal {deal_id} not found")

        # Calculate annual rent
        monthly_rent = deal.monthly_rent or 0.0
        other_monthly_income = deal.other_monthly_income or 0.0
        vacancy_rate = deal.vacancy_rate or 0.05
        num_units = deal.number_of_units or 1

        # Total monthly income per unit
        monthly_income_per_unit = monthly_rent + other_monthly_income

        # Total annual income (accounting for vacancy)
        annual_gross_rent = monthly_income_per_unit * 12 * num_units
        annual_effective_rent = annual_gross_rent * (1 - vacancy_rate)

        # Property value
        property_value = deal.purchase_price or 0.0

        if property_value <= 0:
            raise ValueError("Property value (purchase_price) must be positive")

        # Calculate gross yield
        gross_yield = YieldCalculationService.calculate_gross_yield(
            annual_effective_rent,
            property_value
        )

        # Calculate cost components
        cost_components = YieldCalculationService.calculate_cost_components(
            rent_decile=rent_decile,
            num_units=num_units,
            property_value=property_value,
            annual_rent=annual_effective_rent,
            geography='US'
        )

        # Calculate net yield
        net_yield = YieldCalculationService.calculate_net_yield(
            gross_yield,
            cost_components
        )

        return {
            'gross_yield': gross_yield,
            'cost_components': cost_components,
            'net_yield': net_yield,
            'annual_rent': round(annual_effective_rent, 2),
            'property_value': property_value,
            'num_units': num_units,
            'vacancy_adjusted': True
        }

    @staticmethod
    def validate_yield(yield_value: float, yield_type: str = 'net') -> Dict:
        """
        Validate yield calculation against reasonable bounds

        Args:
            yield_value: Calculated yield percentage
            yield_type: 'gross' or 'net'

        Returns:
            Validation result with warnings
        """
        warnings = []

        if yield_type == 'gross':
            # Gross yields typically 4-10% for residential
            if yield_value < 2.0:
                warnings.append("Unusually low gross yield (<2%). Check rent or property value.")
            elif yield_value > 15.0:
                warnings.append("Unusually high gross yield (>15%). Verify property value is correct.")
        else:  # net
            # Net yields typically 2-8% after costs
            if yield_value < 0.0:
                warnings.append("Negative net yield - property loses money. Review cost assumptions.")
            elif yield_value < 1.0:
                warnings.append("Very low net yield (<1%). Property may not be financially viable.")
            elif yield_value > 12.0:
                warnings.append("Unusually high net yield (>12%). Verify calculations.")

        return {
            'is_valid': len(warnings) == 0,
            'yield_value': yield_value,
            'warnings': warnings
        }

    @staticmethod
    def compare_to_benchmark(
        calculated_net_yield: float,
        rent_decile: int,
        geography: str = 'US'
    ) -> Dict:
        """
        Compare calculated net yield to benchmark ranges

        Args:
            calculated_net_yield: The calculated net yield
            rent_decile: Property's rent tier
            geography: Geographic market

        Returns:
            Comparison results:
                {
                    'benchmark_min': 3.55,
                    'benchmark_max': 5.70,
                    'calculated': 4.2,
                    'position': 'Within',  # 'Below', 'Within', 'Above'
                    'percentile_in_range': 52.0
                }
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
                'calculated': calculated_net_yield,
                'position': 'Unknown',
                'percentile_in_range': None
            }

        benchmark_min = benchmark.net_yield_min
        benchmark_max = benchmark.net_yield_max

        # Determine position
        if calculated_net_yield < benchmark_min:
            position = 'Below'
            percentile = 0.0
        elif calculated_net_yield > benchmark_max:
            position = 'Above'
            percentile = 100.0
        else:
            position = 'Within'
            # Calculate percentile within range
            range_size = benchmark_max - benchmark_min
            if range_size > 0:
                percentile = ((calculated_net_yield - benchmark_min) / range_size) * 100
            else:
                percentile = 50.0

        return {
            'benchmark_min': benchmark_min,
            'benchmark_max': benchmark_max,
            'calculated': calculated_net_yield,
            'position': position,
            'percentile_in_range': round(percentile, 1)
        }
