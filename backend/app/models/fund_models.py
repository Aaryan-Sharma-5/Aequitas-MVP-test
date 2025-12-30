"""
Fund data models for Aequitas MVP
Type-safe data structures for fund management
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date


@dataclass
class Fund:
    """Fund basic information"""
    fund_name: str
    fund_size: float
    vintage_year: int
    id: Optional[int] = None
    status: str = 'active'
    investment_period_start: Optional[date] = None
    investment_period_end: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'fundName': self.fund_name,
            'fundSize': self.fund_size,
            'vintageYear': self.vintage_year,
            'status': self.status,
            'investmentPeriodStart': self.investment_period_start.isoformat() if self.investment_period_start else None,
            'investmentPeriodEnd': self.investment_period_end.isoformat() if self.investment_period_end else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def from_dict(data):
        """Create Fund from dictionary"""
        return Fund(
            id=data.get('id'),
            fund_name=data.get('fundName', ''),
            fund_size=data.get('fundSize', 0),
            vintage_year=data.get('vintageYear', 0),
            status=data.get('status', 'active'),
            investment_period_start=datetime.fromisoformat(data['investmentPeriodStart']).date() if data.get('investmentPeriodStart') else None,
            investment_period_end=datetime.fromisoformat(data['investmentPeriodEnd']).date() if data.get('investmentPeriodEnd') else None,
            created_at=datetime.fromisoformat(data['createdAt']) if data.get('createdAt') else None,
            updated_at=datetime.fromisoformat(data['updatedAt']) if data.get('updatedAt') else None
        )


@dataclass
class FundMetrics:
    """Fund performance metrics snapshot"""
    fund_id: int
    as_of_date: date
    deployed_capital: float
    remaining_capital: float
    net_irr: float
    tvpi: float
    dpi: float
    total_value: float
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'fundId': self.fund_id,
            'asOfDate': self.as_of_date.isoformat() if self.as_of_date else None,
            'deployedCapital': self.deployed_capital,
            'remainingCapital': self.remaining_capital,
            'netIrr': self.net_irr,
            'tvpi': self.tvpi,
            'dpi': self.dpi,
            'totalValue': self.total_value,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def from_dict(data):
        """Create FundMetrics from dictionary"""
        return FundMetrics(
            id=data.get('id'),
            fund_id=data.get('fundId', 0),
            as_of_date=datetime.fromisoformat(data['asOfDate']).date() if data.get('asOfDate') else date.today(),
            deployed_capital=data.get('deployedCapital', 0),
            remaining_capital=data.get('remainingCapital', 0),
            net_irr=data.get('netIrr', 0),
            tvpi=data.get('tvpi', 0),
            dpi=data.get('dpi', 0),
            total_value=data.get('totalValue', 0),
            created_at=datetime.fromisoformat(data['createdAt']) if data.get('createdAt') else None
        )


@dataclass
class QuarterlyPerformance:
    """Quarterly IRR performance data"""
    fund_id: int
    year: int
    quarter: int
    irr: float
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'fundId': self.fund_id,
            'year': self.year,
            'quarter': self.quarter,
            'quarterLabel': f'Q{self.quarter} {self.year}',
            'irr': self.irr,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def from_dict(data):
        """Create QuarterlyPerformance from dictionary"""
        return QuarterlyPerformance(
            id=data.get('id'),
            fund_id=data.get('fundId', 0),
            year=data.get('year', 0),
            quarter=data.get('quarter', 0),
            irr=data.get('irr', 0),
            created_at=datetime.fromisoformat(data['createdAt']) if data.get('createdAt') else None
        )


@dataclass
class InvestmentStrategy:
    """Investment strategy breakdown"""
    fund_id: int
    strategy_name: str
    deployed_capital: float
    current_value: float
    allocation_percent: float
    irr: float
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'fundId': self.fund_id,
            'strategyName': self.strategy_name,
            'deployedCapital': self.deployed_capital,
            'currentValue': self.current_value,
            'allocationPercent': self.allocation_percent,
            'irr': self.irr,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def from_dict(data):
        """Create InvestmentStrategy from dictionary"""
        return InvestmentStrategy(
            id=data.get('id'),
            fund_id=data.get('fundId', 0),
            strategy_name=data.get('strategyName', ''),
            deployed_capital=data.get('deployedCapital', 0),
            current_value=data.get('currentValue', 0),
            allocation_percent=data.get('allocationPercent', 0),
            irr=data.get('irr', 0),
            created_at=datetime.fromisoformat(data['createdAt']) if data.get('createdAt') else None,
            updated_at=datetime.fromisoformat(data['updatedAt']) if data.get('updatedAt') else None
        )


@dataclass
class CashFlow:
    """Quarterly cash flow data"""
    fund_id: int
    year: int
    quarter: int
    capital_calls: float
    distributions: float
    net_cash_flow: float
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'fundId': self.fund_id,
            'year': self.year,
            'quarter': self.quarter,
            'quarterLabel': f'Q{self.quarter} {self.year}',
            'capitalCalls': self.capital_calls,
            'distributions': self.distributions,
            'netCashFlow': self.net_cash_flow,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def from_dict(data):
        """Create CashFlow from dictionary"""
        return CashFlow(
            id=data.get('id'),
            fund_id=data.get('fundId', 0),
            year=data.get('year', 0),
            quarter=data.get('quarter', 0),
            capital_calls=data.get('capitalCalls', 0),
            distributions=data.get('distributions', 0),
            net_cash_flow=data.get('netCashFlow', 0),
            created_at=datetime.fromisoformat(data['createdAt']) if data.get('createdAt') else None
        )


@dataclass
class FundActivity:
    """Fund activity/transaction data"""
    fund_id: int
    activity_date: date
    description: str
    amount: float
    status: str
    activity_type: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'fundId': self.fund_id,
            'activityDate': self.activity_date.isoformat() if self.activity_date else None,
            'description': self.description,
            'amount': self.amount,
            'status': self.status,
            'activityType': self.activity_type,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def from_dict(data):
        """Create FundActivity from dictionary"""
        return FundActivity(
            id=data.get('id'),
            fund_id=data.get('fundId', 0),
            activity_date=datetime.fromisoformat(data['activityDate']).date() if data.get('activityDate') else date.today(),
            description=data.get('description', ''),
            amount=data.get('amount', 0),
            status=data.get('status', ''),
            activity_type=data.get('activityType', ''),
            created_at=datetime.fromisoformat(data['createdAt']) if data.get('createdAt') else None
        )


@dataclass
class BenchmarkComparison:
    """Benchmark comparison data"""
    fund_id: int
    metric_name: str
    fund_value: float
    industry_benchmark: float
    as_of_date: date
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        outperformance = self.fund_value - self.industry_benchmark
        return {
            'id': self.id,
            'fundId': self.fund_id,
            'metricName': self.metric_name,
            'fundValue': self.fund_value,
            'industryBenchmark': self.industry_benchmark,
            'outperformance': outperformance,
            'asOfDate': self.as_of_date.isoformat() if self.as_of_date else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def from_dict(data):
        """Create BenchmarkComparison from dictionary"""
        return BenchmarkComparison(
            id=data.get('id'),
            fund_id=data.get('fundId', 0),
            metric_name=data.get('metricName', ''),
            fund_value=data.get('fundValue', 0),
            industry_benchmark=data.get('industryBenchmark', 0),
            as_of_date=datetime.fromisoformat(data['asOfDate']).date() if data.get('asOfDate') else date.today(),
            created_at=datetime.fromisoformat(data['createdAt']) if data.get('createdAt') else None
        )


@dataclass
class CashFlowSummary:
    """Summary of cash flows across all quarters"""
    total_capital_calls: float
    total_distributions: float
    cumulative_net_cash: float

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'totalCapitalCalls': self.total_capital_calls,
            'totalDistributions': self.total_distributions,
            'cumulativeNetCash': self.cumulative_net_cash
        }
