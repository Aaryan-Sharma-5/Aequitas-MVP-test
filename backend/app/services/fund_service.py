"""
Fund service layer for fund data operations
Handles business logic for fund management
"""
from typing import List, Optional, Dict
from app.database import (
    db,
    FundModel,
    FundMetricsModel,
    QuarterlyPerformanceModel,
    InvestmentStrategyModel,
    CashFlowModel,
    FundActivityModel,
    BenchmarkDataModel
)
from app.models.fund_models import (
    Fund,
    FundMetrics,
    QuarterlyPerformance,
    InvestmentStrategy,
    CashFlow,
    FundActivity,
    BenchmarkComparison,
    CashFlowSummary
)


class FundService:
    """Service class for managing investment funds"""

    @staticmethod
    def get_fund(fund_id: int) -> Optional[Fund]:
        """
        Get a fund by ID

        Args:
            fund_id: ID of the fund to retrieve

        Returns:
            Fund object if found, None otherwise
        """
        fund_model = FundModel.query.get(fund_id)
        if not fund_model:
            return None

        return Fund.from_dict(fund_model.to_dict())

    @staticmethod
    def get_fund_overview(fund_id: int) -> Optional[Dict]:
        """
        Get complete fund overview with all related data
        This is the main method that aggregates all fund data for the frontend

        Args:
            fund_id: ID of the fund

        Returns:
            Dictionary containing all fund data, or None if fund not found
        """
        # Get fund basic info
        fund = FundService.get_fund(fund_id)
        if not fund:
            return None

        # Get latest metrics
        metrics = FundService.get_fund_metrics(fund_id)

        # Get quarterly performance (last 8 quarters)
        quarterly_performance = FundService.get_quarterly_performance(fund_id, limit=8)

        # Get investment strategies
        strategies = FundService.get_investment_strategies(fund_id)

        # Get cash flows with summary (last 8 quarters)
        cash_flow_data = FundService.get_cash_flows(fund_id, limit=8)

        # Get benchmarks
        benchmarks = FundService.get_benchmark_comparisons(fund_id)

        # Get recent activities (last 10)
        recent_activities = FundService.get_fund_activities(fund_id, limit=10)

        # Aggregate everything into one response
        return {
            'fund': fund.to_dict(),
            'metrics': metrics.to_dict() if metrics else None,
            'quarterlyPerformance': [qp.to_dict() for qp in quarterly_performance],
            'strategies': [s.to_dict() for s in strategies],
            'cashFlows': cash_flow_data['cashFlows'],
            'cashFlowSummary': cash_flow_data['summary'],
            'benchmarks': [b.to_dict() for b in benchmarks],
            'recentActivities': [a.to_dict() for a in recent_activities]
        }

    @staticmethod
    def get_fund_metrics(fund_id: int) -> Optional[FundMetrics]:
        """
        Get latest fund metrics

        Args:
            fund_id: ID of the fund

        Returns:
            FundMetrics object with latest metrics, or None if not found
        """
        # Get most recent metrics by as_of_date
        metrics_model = FundMetricsModel.query.filter_by(fund_id=fund_id).order_by(
            FundMetricsModel.as_of_date.desc()
        ).first()

        if not metrics_model:
            return None

        return FundMetrics.from_dict(metrics_model.to_dict())

    @staticmethod
    def get_quarterly_performance(fund_id: int, limit: int = 8) -> List[QuarterlyPerformance]:
        """
        Get quarterly IRR performance

        Args:
            fund_id: ID of the fund
            limit: Maximum number of quarters to return (default 8)

        Returns:
            List of QuarterlyPerformance objects
        """
        # Get most recent quarters, ordered by year and quarter descending
        perf_models = QuarterlyPerformanceModel.query.filter_by(fund_id=fund_id).order_by(
            QuarterlyPerformanceModel.year.asc(),
            QuarterlyPerformanceModel.quarter.asc()
        ).limit(limit).all()

        return [QuarterlyPerformance.from_dict(pm.to_dict()) for pm in perf_models]

    @staticmethod
    def get_investment_strategies(fund_id: int) -> List[InvestmentStrategy]:
        """
        Get investment strategies for a fund

        Args:
            fund_id: ID of the fund

        Returns:
            List of InvestmentStrategy objects
        """
        strategy_models = InvestmentStrategyModel.query.filter_by(fund_id=fund_id).order_by(
            InvestmentStrategyModel.deployed_capital.desc()
        ).all()

        strategies = [InvestmentStrategy.from_dict(sm.to_dict()) for sm in strategy_models]

        # Calculate percent of total for each strategy
        total_deployed = sum(s.deployed_capital for s in strategies)
        for strategy in strategies:
            # Add percentOfTotal to the dict representation
            strategy_dict = strategy.to_dict()
            strategy_dict['percentOfTotal'] = (strategy.deployed_capital / total_deployed * 100) if total_deployed > 0 else 0

        return strategies

    @staticmethod
    def get_cash_flows(fund_id: int, limit: int = 8) -> Dict:
        """
        Get quarterly cash flows with summary

        Args:
            fund_id: ID of the fund
            limit: Maximum number of quarters to return (default 8)

        Returns:
            Dictionary with 'cashFlows' list and 'summary' dict
        """
        # Get most recent quarters
        cash_flow_models = CashFlowModel.query.filter_by(fund_id=fund_id).order_by(
            CashFlowModel.year.asc(),
            CashFlowModel.quarter.asc()
        ).limit(limit).all()

        cash_flows = [CashFlow.from_dict(cf.to_dict()) for cf in cash_flow_models]

        # Calculate summary
        total_capital_calls = sum(cf.capital_calls for cf in cash_flows)
        total_distributions = sum(cf.distributions for cf in cash_flows)
        cumulative_net_cash = total_distributions - total_capital_calls

        summary = CashFlowSummary(
            total_capital_calls=total_capital_calls,
            total_distributions=total_distributions,
            cumulative_net_cash=cumulative_net_cash
        )

        return {
            'cashFlows': [cf.to_dict() for cf in cash_flows],
            'summary': summary.to_dict()
        }

    @staticmethod
    def get_fund_activities(fund_id: int, limit: int = 10, status: Optional[str] = None) -> List[FundActivity]:
        """
        Get recent fund activities

        Args:
            fund_id: ID of the fund
            limit: Maximum number of activities to return (default 10)
            status: Optional status filter ('Completed', 'In Progress', 'Scheduled')

        Returns:
            List of FundActivity objects
        """
        query = FundActivityModel.query.filter_by(fund_id=fund_id)

        # Apply status filter if provided
        if status:
            query = query.filter(FundActivityModel.status == status)

        # Order by activity date descending (most recent first)
        query = query.order_by(FundActivityModel.activity_date.desc())

        # Limit results
        query = query.limit(limit)

        activity_models = query.all()
        return [FundActivity.from_dict(am.to_dict()) for am in activity_models]

    @staticmethod
    def get_benchmark_comparisons(fund_id: int) -> List[BenchmarkComparison]:
        """
        Get benchmark comparisons for a fund

        Args:
            fund_id: ID of the fund

        Returns:
            List of BenchmarkComparison objects
        """
        # Get most recent benchmarks
        benchmark_models = BenchmarkDataModel.query.filter_by(fund_id=fund_id).order_by(
            BenchmarkDataModel.as_of_date.desc()
        ).all()

        return [BenchmarkComparison.from_dict(bm.to_dict()) for bm in benchmark_models]

    @staticmethod
    def create_fund(fund_data: dict) -> Fund:
        """
        Create a new fund (for future use)

        Args:
            fund_data: Dictionary containing fund information

        Returns:
            Created Fund object

        Raises:
            ValueError: If required fields are missing
        """
        # Validate required fields
        if not fund_data.get('fundName'):
            raise ValueError('Fund name is required')
        if not fund_data.get('fundSize'):
            raise ValueError('Fund size is required')

        # Create FundModel from dictionary
        fund_model = FundModel.from_dict(fund_data)

        # Save to database
        db.session.add(fund_model)
        db.session.commit()

        # Convert to Fund dataclass and return
        return Fund.from_dict(fund_model.to_dict())
