"""
Total Return Service
Integrates net yield and capital appreciation to calculate total returns

Academic Research Basis:
- Total Return = Net Yield + Capital Gain Yield
- D1 total return: 4.53-11.19% (US)
- D10 total return: 2.56-7.04% (US)
- D1-D10 spread: 1.97-4.15 percentage points
- Low-rent properties deliver superior risk-adjusted returns
"""

from typing import Dict, Optional
from app.database import db, RiskBenchmarkData, DealModel
from app.services.yield_calculation_service import YieldCalculationService
from app.services.capital_appreciation_service import CapitalAppreciationService


class TotalReturnService:
    """
    Service for calculating total returns (levered and unlevered)
    """

    @staticmethod
    def calculate_unlevered_return(
        net_yield: float,
        capital_gain_yield: float
    ) -> float:
        """
        Calculate unlevered total return

        Total Return = Net Yield + Capital Gain Yield

        Args:
            net_yield: Annual net yield percentage
            capital_gain_yield: Annual capital appreciation percentage

        Returns:
            Total return percentage
        """
        total_return = net_yield + capital_gain_yield
        return round(total_return, 2)

    @staticmethod
    def calculate_levered_return(
        unlevered_return: float,
        cost_of_debt: float,
        ltv: float
    ) -> float:
        """
        Calculate levered return using leverage multiplier

        Levered Return = Unlevered Return + (Unlevered Return - Cost of Debt) × (LTV / (1 - LTV))

        Args:
            unlevered_return: Unlevered total return percentage
            cost_of_debt: Interest rate on debt (percentage)
            ltv: Loan-to-value ratio (as decimal, e.g., 0.75 for 75%)

        Returns:
            Levered total return percentage
        """

        if ltv >= 1.0:
            raise ValueError("LTV must be less than 100%")

        if ltv <= 0:
            # No leverage
            return unlevered_return

        # Calculate leverage multiplier
        spread = unlevered_return - cost_of_debt
        leverage_multiplier = ltv / (1 - ltv)
        leverage_effect = spread * leverage_multiplier

        levered_return = unlevered_return + leverage_effect

        return round(levered_return, 2)

    @staticmethod
    def calculate_for_deal(
        deal_id: int,
        rent_decile: int,
        holding_period: int = 10
    ) -> Dict:
        """
        Calculate complete total return analysis for a deal

        Args:
            deal_id: Deal ID to analyze
            rent_decile: Property's rent tier (1-10)
            holding_period: Years to hold property

        Returns:
            Complete return analysis:
                {
                    'net_yield': 4.5,
                    'capital_gain_yield': 3.2,
                    'total_return_unlevered': 7.7,
                    'cost_of_debt': 6.5,
                    'ltv': 0.75,
                    'total_return_levered': 11.2,
                    'leverage_effect': 3.5,
                    'benchmark_comparison': {...}
                }
        """

        # Fetch deal
        deal = DealModel.query.get(deal_id)
        if not deal:
            raise ValueError(f"Deal {deal_id} not found")

        # Calculate yields
        yield_analysis = YieldCalculationService.calculate_yields_for_deal(
            deal_id=deal_id,
            rent_decile=rent_decile
        )

        net_yield = yield_analysis['net_yield']

        # Calculate capital appreciation
        appreciation_analysis = CapitalAppreciationService.calculate_for_deal(
            deal_id=deal_id,
            rent_decile=rent_decile,
            holding_period=holding_period
        )

        capital_gain_yield = appreciation_analysis['capital_gain_yield_annual']

        # Calculate unlevered return
        total_return_unlevered = TotalReturnService.calculate_unlevered_return(
            net_yield=net_yield,
            capital_gain_yield=capital_gain_yield
        )

        # Get financing terms
        cost_of_debt = deal.loan_interest_rate or 6.5  # Default to 6.5%
        down_payment_pct = deal.down_payment_percent or 25.0
        ltv = 1.0 - (down_payment_pct / 100)

        # Calculate levered return
        total_return_levered = TotalReturnService.calculate_levered_return(
            unlevered_return=total_return_unlevered,
            cost_of_debt=cost_of_debt,
            ltv=ltv
        )

        leverage_effect = total_return_levered - total_return_unlevered

        # Compare to benchmarks
        benchmark_comparison = TotalReturnService.compare_to_benchmark(
            total_return_unlevered=total_return_unlevered,
            rent_decile=rent_decile,
            geography='US'
        )

        return {
            'net_yield': net_yield,
            'capital_gain_yield': capital_gain_yield,
            'total_return_unlevered': total_return_unlevered,
            'cost_of_debt': cost_of_debt,
            'ltv': round(ltv, 3),
            'total_return_levered': total_return_levered,
            'leverage_effect': round(leverage_effect, 2),
            'holding_period': holding_period,
            'benchmark_comparison': benchmark_comparison,
            'components': {
                'yield_analysis': yield_analysis,
                'appreciation_analysis': appreciation_analysis
            }
        }

    @staticmethod
    def compare_to_benchmark(
        total_return_unlevered: float,
        rent_decile: int,
        geography: str = 'US'
    ) -> Dict:
        """
        Compare calculated total return to benchmark ranges

        Args:
            total_return_unlevered: Calculated total return
            rent_decile: Property's rent tier
            geography: Geographic market

        Returns:
            Comparison results with position and percentile
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
                'calculated': total_return_unlevered,
                'position': 'Unknown',
                'percentile_in_range': None,
                'interpretation': 'No benchmark data available'
            }

        benchmark_min = benchmark.total_return_min
        benchmark_max = benchmark.total_return_max

        # Determine position
        if total_return_unlevered < benchmark_min:
            position = 'Below'
            percentile = 0.0
            interpretation = f"Below benchmark range. Expected {benchmark_min:.1f}-{benchmark_max:.1f}%"
        elif total_return_unlevered > benchmark_max:
            position = 'Above'
            percentile = 100.0
            interpretation = f"Above benchmark range. Exceeds research findings of {benchmark_max:.1f}%"
        else:
            position = 'Within'
            range_size = benchmark_max - benchmark_min
            if range_size > 0:
                percentile = ((total_return_unlevered - benchmark_min) / range_size) * 100
            else:
                percentile = 50.0
            interpretation = f"Within benchmark range of {benchmark_min:.1f}-{benchmark_max:.1f}%"

        return {
            'benchmark_min': benchmark_min,
            'benchmark_max': benchmark_max,
            'calculated': total_return_unlevered,
            'position': position,
            'percentile_in_range': round(percentile, 1),
            'interpretation': interpretation
        }

    @staticmethod
    def calculate_equity_multiple(
        initial_equity: float,
        total_cash_flows: float,
        exit_proceeds: float
    ) -> float:
        """
        Calculate equity multiple

        Equity Multiple = (Total Cash Flows + Exit Proceeds) / Initial Equity

        Args:
            initial_equity: Initial equity invested
            total_cash_flows: Sum of all annual cash flows
            exit_proceeds: Net proceeds from sale

        Returns:
            Equity multiple (e.g., 2.5x)
        """

        if initial_equity <= 0:
            raise ValueError("Initial equity must be positive")

        equity_multiple = (total_cash_flows + exit_proceeds) / initial_equity

        return round(equity_multiple, 2)

    @staticmethod
    def calculate_cash_on_cash_return(
        annual_cash_flow: float,
        initial_equity: float
    ) -> float:
        """
        Calculate cash-on-cash return

        CoC = Annual Cash Flow / Initial Equity

        Args:
            annual_cash_flow: Annual pre-tax cash flow
            initial_equity: Initial equity invested

        Returns:
            Cash-on-cash return as percentage
        """

        if initial_equity <= 0:
            raise ValueError("Initial equity must be positive")

        coc_return = (annual_cash_flow / initial_equity) * 100

        return round(coc_return, 2)

    @staticmethod
    def sensitivity_analysis(
        deal_id: int,
        rent_decile: int,
        scenarios: Dict
    ) -> Dict:
        """
        Run sensitivity analysis on total returns

        Args:
            deal_id: Deal to analyze
            rent_decile: Property's rent tier
            scenarios: Dictionary of scenarios to test:
                {
                    'base': {'yield_adjustment': 0, 'appreciation_adjustment': 0},
                    'optimistic': {'yield_adjustment': 0.5, 'appreciation_adjustment': 1.0},
                    'pessimistic': {'yield_adjustment': -0.5, 'appreciation_adjustment': -1.0}
                }

        Returns:
            Results for each scenario
        """

        results = {}

        for scenario_name, adjustments in scenarios.items():
            # Calculate base returns
            base_returns = TotalReturnService.calculate_for_deal(
                deal_id=deal_id,
                rent_decile=rent_decile
            )

            # Apply adjustments
            adjusted_net_yield = base_returns['net_yield'] + adjustments.get('yield_adjustment', 0)
            adjusted_capital_gain = base_returns['capital_gain_yield'] + adjustments.get('appreciation_adjustment', 0)

            # Recalculate total return
            adjusted_unlevered = TotalReturnService.calculate_unlevered_return(
                net_yield=adjusted_net_yield,
                capital_gain_yield=adjusted_capital_gain
            )

            adjusted_levered = TotalReturnService.calculate_levered_return(
                unlevered_return=adjusted_unlevered,
                cost_of_debt=base_returns['cost_of_debt'],
                ltv=base_returns['ltv']
            )

            results[scenario_name] = {
                'net_yield': adjusted_net_yield,
                'capital_gain_yield': adjusted_capital_gain,
                'total_return_unlevered': adjusted_unlevered,
                'total_return_levered': adjusted_levered
            }

        return results

    @staticmethod
    def validate_returns(
        total_return_unlevered: float,
        total_return_levered: float,
        rent_decile: int
    ) -> Dict:
        """
        Validate return calculations against reasonable bounds

        Args:
            total_return_unlevered: Unlevered return
            total_return_levered: Levered return
            rent_decile: Property's rent tier

        Returns:
            Validation results with warnings
        """

        warnings = []

        # Check unlevered return reasonableness
        if total_return_unlevered < 0:
            warnings.append("Negative unlevered return - property destroys value")
        elif total_return_unlevered < 3.0:
            warnings.append("Very low unlevered return (<3%) - below risk-free rate")
        elif total_return_unlevered > 20.0:
            warnings.append("Unusually high unlevered return (>20%) - verify assumptions")

        # Check leverage effect
        if total_return_levered < total_return_unlevered - 5.0:
            warnings.append("Negative leverage - debt cost exceeds property returns")

        # Check alignment with research (low-rent should outperform)
        if rent_decile <= 3 and total_return_unlevered < 5.0:
            warnings.append(f"Low return for D{rent_decile} property. Research shows D1-D3 average 8-11%")
        elif rent_decile >= 8 and total_return_unlevered > 10.0:
            warnings.append(f"High return for D{rent_decile} property. Research shows D8-D10 average 3-7%")

        return {
            'is_valid': len(warnings) == 0,
            'warnings': warnings,
            'total_return_unlevered': total_return_unlevered,
            'total_return_levered': total_return_levered
        }
