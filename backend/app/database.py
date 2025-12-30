"""
Database configuration and models for Aequitas MVP
"""
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Date, ForeignKey
from sqlalchemy.sql import func

db = SQLAlchemy()


class DealModel(db.Model):
    """
    SQLAlchemy model for real estate deals
    Stores all property information, financial details, and calculated metrics
    """
    __tablename__ = 'deals'

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Basic Deal Information
    deal_name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    status = Column(String(50), default='potential', nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Property Information
    property_address = Column(String(500))
    latitude = Column(Float)
    longitude = Column(Float)

    # Purchase Details
    purchase_price = Column(Float)
    down_payment_percent = Column(Float)
    loan_interest_rate = Column(Float)
    loan_term_years = Column(Integer)
    closing_costs = Column(Float)

    # Income
    monthly_rent = Column(Float)
    other_monthly_income = Column(Float)
    vacancy_rate = Column(Float)
    annual_rent_increase = Column(Float)

    # Expenses
    property_tax_annual = Column(Float)
    insurance_annual = Column(Float)
    hoa_monthly = Column(Float)
    maintenance_percent = Column(Float)
    property_management_percent = Column(Float)
    utilities_monthly = Column(Float)
    other_expenses_monthly = Column(Float)

    # Property Details
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    square_footage = Column(Integer)
    property_type = Column(String(100))
    year_built = Column(Integer)

    # Market Data Snapshots (JSON stored as text)
    rentcast_data = Column(Text)
    fred_data = Column(Text)

    # Calculated Metrics (cached for performance)
    monthly_payment = Column(Float)
    total_monthly_income = Column(Float)
    total_monthly_expenses = Column(Float)
    monthly_cash_flow = Column(Float)
    cash_on_cash_return = Column(Float)
    cap_rate = Column(Float)
    roi = Column(Float)
    npv = Column(Float)
    irr = Column(Float)

    def __repr__(self):
        return f'<Deal {self.id}: {self.deal_name} ({self.status})>'

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'dealName': self.deal_name,
            'location': self.location,
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,

            # Property Information
            'propertyAddress': self.property_address,
            'latitude': self.latitude,
            'longitude': self.longitude,

            # Purchase Details
            'purchasePrice': self.purchase_price,
            'downPaymentPercent': self.down_payment_percent,
            'loanInterestRate': self.loan_interest_rate,
            'loanTermYears': self.loan_term_years,
            'closingCosts': self.closing_costs,

            # Income
            'monthlyRent': self.monthly_rent,
            'otherMonthlyIncome': self.other_monthly_income,
            'vacancyRate': self.vacancy_rate,
            'annualRentIncrease': self.annual_rent_increase,

            # Expenses
            'propertyTaxAnnual': self.property_tax_annual,
            'insuranceAnnual': self.insurance_annual,
            'hoaMonthly': self.hoa_monthly,
            'maintenancePercent': self.maintenance_percent,
            'propertyManagementPercent': self.property_management_percent,
            'utilitiesMonthly': self.utilities_monthly,
            'otherExpensesMonthly': self.other_expenses_monthly,

            # Property Details
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'squareFootage': self.square_footage,
            'propertyType': self.property_type,
            'yearBuilt': self.year_built,

            # Market Data
            'rentcastData': self.rentcast_data,
            'fredData': self.fred_data,

            # Calculated Metrics
            'monthlyPayment': self.monthly_payment,
            'totalMonthlyIncome': self.total_monthly_income,
            'totalMonthlyExpenses': self.total_monthly_expenses,
            'monthlyCashFlow': self.monthly_cash_flow,
            'cashOnCashReturn': self.cash_on_cash_return,
            'capRate': self.cap_rate,
            'roi': self.roi,
            'npv': self.npv,
            'irr': self.irr
        }

    @staticmethod
    def from_dict(data):
        """Create a DealModel instance from a dictionary"""
        return DealModel(
            deal_name=data.get('dealName'),
            location=data.get('location'),
            status=data.get('status', 'potential'),

            # Property Information
            property_address=data.get('propertyAddress'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),

            # Purchase Details
            purchase_price=data.get('purchasePrice'),
            down_payment_percent=data.get('downPaymentPercent'),
            loan_interest_rate=data.get('loanInterestRate'),
            loan_term_years=data.get('loanTermYears'),
            closing_costs=data.get('closingCosts'),

            # Income
            monthly_rent=data.get('monthlyRent'),
            other_monthly_income=data.get('otherMonthlyIncome'),
            vacancy_rate=data.get('vacancyRate'),
            annual_rent_increase=data.get('annualRentIncrease'),

            # Expenses
            property_tax_annual=data.get('propertyTaxAnnual'),
            insurance_annual=data.get('insuranceAnnual'),
            hoa_monthly=data.get('hoaMonthly'),
            maintenance_percent=data.get('maintenancePercent'),
            property_management_percent=data.get('propertyManagementPercent'),
            utilities_monthly=data.get('utilitiesMonthly'),
            other_expenses_monthly=data.get('otherExpensesMonthly'),

            # Property Details
            bedrooms=data.get('bedrooms'),
            bathrooms=data.get('bathrooms'),
            square_footage=data.get('squareFootage'),
            property_type=data.get('propertyType'),
            year_built=data.get('yearBuilt'),

            # Market Data
            rentcast_data=data.get('rentcastData'),
            fred_data=data.get('fredData'),

            # Calculated Metrics
            monthly_payment=data.get('monthlyPayment'),
            total_monthly_income=data.get('totalMonthlyIncome'),
            total_monthly_expenses=data.get('totalMonthlyExpenses'),
            monthly_cash_flow=data.get('monthlyCashFlow'),
            cash_on_cash_return=data.get('cashOnCashReturn'),
            cap_rate=data.get('capRate'),
            roi=data.get('roi'),
            npv=data.get('npv'),
            irr=data.get('irr')
        )

    def update_from_dict(self, data):
        """Update model fields from a dictionary"""
        # Basic Deal Information
        if 'dealName' in data:
            self.deal_name = data['dealName']
        if 'location' in data:
            self.location = data['location']
        if 'status' in data:
            self.status = data['status']

        # Property Information
        if 'propertyAddress' in data:
            self.property_address = data['propertyAddress']
        if 'latitude' in data:
            self.latitude = data['latitude']
        if 'longitude' in data:
            self.longitude = data['longitude']

        # Purchase Details
        if 'purchasePrice' in data:
            self.purchase_price = data['purchasePrice']
        if 'downPaymentPercent' in data:
            self.down_payment_percent = data['downPaymentPercent']
        if 'loanInterestRate' in data:
            self.loan_interest_rate = data['loanInterestRate']
        if 'loanTermYears' in data:
            self.loan_term_years = data['loanTermYears']
        if 'closingCosts' in data:
            self.closing_costs = data['closingCosts']

        # Income
        if 'monthlyRent' in data:
            self.monthly_rent = data['monthlyRent']
        if 'otherMonthlyIncome' in data:
            self.other_monthly_income = data['otherMonthlyIncome']
        if 'vacancyRate' in data:
            self.vacancy_rate = data['vacancyRate']
        if 'annualRentIncrease' in data:
            self.annual_rent_increase = data['annualRentIncrease']

        # Expenses
        if 'propertyTaxAnnual' in data:
            self.property_tax_annual = data['propertyTaxAnnual']
        if 'insuranceAnnual' in data:
            self.insurance_annual = data['insuranceAnnual']
        if 'hoaMonthly' in data:
            self.hoa_monthly = data['hoaMonthly']
        if 'maintenancePercent' in data:
            self.maintenance_percent = data['maintenancePercent']
        if 'propertyManagementPercent' in data:
            self.property_management_percent = data['propertyManagementPercent']
        if 'utilitiesMonthly' in data:
            self.utilities_monthly = data['utilitiesMonthly']
        if 'otherExpensesMonthly' in data:
            self.other_expenses_monthly = data['otherExpensesMonthly']

        # Property Details
        if 'bedrooms' in data:
            self.bedrooms = data['bedrooms']
        if 'bathrooms' in data:
            self.bathrooms = data['bathrooms']
        if 'squareFootage' in data:
            self.square_footage = data['squareFootage']
        if 'propertyType' in data:
            self.property_type = data['propertyType']
        if 'yearBuilt' in data:
            self.year_built = data['yearBuilt']

        # Market Data
        if 'rentcastData' in data:
            self.rentcast_data = data['rentcastData']
        if 'fredData' in data:
            self.fred_data = data['fredData']

        # Calculated Metrics
        if 'monthlyPayment' in data:
            self.monthly_payment = data['monthlyPayment']
        if 'totalMonthlyIncome' in data:
            self.total_monthly_income = data['totalMonthlyIncome']
        if 'totalMonthlyExpenses' in data:
            self.total_monthly_expenses = data['totalMonthlyExpenses']
        if 'monthlyCashFlow' in data:
            self.monthly_cash_flow = data['monthlyCashFlow']
        if 'cashOnCashReturn' in data:
            self.cash_on_cash_return = data['cashOnCashReturn']
        if 'capRate' in data:
            self.cap_rate = data['capRate']
        if 'roi' in data:
            self.roi = data['roi']
        if 'npv' in data:
            self.npv = data['npv']
        if 'irr' in data:
            self.irr = data['irr']

        # Update timestamp
        self.updated_at = datetime.utcnow()


# ============================================================================
# FUND MODELS
# ============================================================================


class FundModel(db.Model):
    """
    SQLAlchemy model for investment funds
    Stores basic fund information and configuration
    """
    __tablename__ = 'funds'

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Basic Fund Information
    fund_name = Column(String(255), nullable=False)
    fund_size = Column(Float)  # Total committed capital
    status = Column(String(50), default='active', nullable=False)  # active, closed, liquidated
    vintage_year = Column(Integer)  # Year fund was established
    investment_period_start = Column(Date)
    investment_period_end = Column(Date)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f'<Fund {self.id}: {self.fund_name} ({self.status})>'

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'fundName': self.fund_name,
            'fundSize': self.fund_size,
            'status': self.status,
            'vintageYear': self.vintage_year,
            'investmentPeriodStart': self.investment_period_start.isoformat() if self.investment_period_start else None,
            'investmentPeriodEnd': self.investment_period_end.isoformat() if self.investment_period_end else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def from_dict(data):
        """Create a FundModel instance from a dictionary"""
        from datetime import datetime as dt
        return FundModel(
            fund_name=data.get('fundName'),
            fund_size=data.get('fundSize'),
            status=data.get('status', 'active'),
            vintage_year=data.get('vintageYear'),
            investment_period_start=dt.fromisoformat(data['investmentPeriodStart']) if data.get('investmentPeriodStart') else None,
            investment_period_end=dt.fromisoformat(data['investmentPeriodEnd']) if data.get('investmentPeriodEnd') else None
        )

    def update_from_dict(self, data):
        """Update model fields from a dictionary"""
        from datetime import datetime as dt

        if 'fundName' in data:
            self.fund_name = data['fundName']
        if 'fundSize' in data:
            self.fund_size = data['fundSize']
        if 'status' in data:
            self.status = data['status']
        if 'vintageYear' in data:
            self.vintage_year = data['vintageYear']
        if 'investmentPeriodStart' in data:
            self.investment_period_start = dt.fromisoformat(data['investmentPeriodStart']) if data['investmentPeriodStart'] else None
        if 'investmentPeriodEnd' in data:
            self.investment_period_end = dt.fromisoformat(data['investmentPeriodEnd']) if data['investmentPeriodEnd'] else None

        self.updated_at = datetime.utcnow()


class FundMetricsModel(db.Model):
    """
    SQLAlchemy model for fund performance metrics
    Stores snapshot of fund metrics at a specific date
    """
    __tablename__ = 'fund_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False)
    as_of_date = Column(Date, nullable=False)
    deployed_capital = Column(Float)
    remaining_capital = Column(Float)
    net_irr = Column(Float)  # Net IRR percentage
    tvpi = Column(Float)  # Total Value to Paid-In multiple
    dpi = Column(Float)  # Distributions to Paid-In multiple
    total_value = Column(Float)  # NAV + Distributions
    created_at = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f'<FundMetrics {self.id}: Fund {self.fund_id} as of {self.as_of_date}>'

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
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
        """Create a FundMetricsModel instance from a dictionary"""
        from datetime import datetime as dt
        return FundMetricsModel(
            fund_id=data.get('fundId'),
            as_of_date=dt.fromisoformat(data['asOfDate']).date() if data.get('asOfDate') else None,
            deployed_capital=data.get('deployedCapital'),
            remaining_capital=data.get('remainingCapital'),
            net_irr=data.get('netIrr'),
            tvpi=data.get('tvpi'),
            dpi=data.get('dpi'),
            total_value=data.get('totalValue')
        )

    def update_from_dict(self, data):
        """Update model fields from a dictionary"""
        from datetime import datetime as dt

        if 'asOfDate' in data:
            self.as_of_date = dt.fromisoformat(data['asOfDate']).date() if data['asOfDate'] else None
        if 'deployedCapital' in data:
            self.deployed_capital = data['deployedCapital']
        if 'remainingCapital' in data:
            self.remaining_capital = data['remainingCapital']
        if 'netIrr' in data:
            self.net_irr = data['netIrr']
        if 'tvpi' in data:
            self.tvpi = data['tvpi']
        if 'dpi' in data:
            self.dpi = data['dpi']
        if 'totalValue' in data:
            self.total_value = data['totalValue']


class QuarterlyPerformanceModel(db.Model):
    """
    SQLAlchemy model for quarterly fund performance
    Stores IRR performance by quarter
    """
    __tablename__ = 'fund_quarterly_performance'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)  # 1, 2, 3, 4
    irr = Column(Float)  # IRR for that quarter
    created_at = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f'<QuarterlyPerformance {self.id}: Fund {self.fund_id} Q{self.quarter} {self.year}>'

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
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
        """Create a QuarterlyPerformanceModel instance from a dictionary"""
        return QuarterlyPerformanceModel(
            fund_id=data.get('fundId'),
            year=data.get('year'),
            quarter=data.get('quarter'),
            irr=data.get('irr')
        )

    def update_from_dict(self, data):
        """Update model fields from a dictionary"""
        if 'year' in data:
            self.year = data['year']
        if 'quarter' in data:
            self.quarter = data['quarter']
        if 'irr' in data:
            self.irr = data['irr']


class InvestmentStrategyModel(db.Model):
    """
    SQLAlchemy model for investment strategies
    Stores breakdown of fund investments by strategy
    """
    __tablename__ = 'investment_strategies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False)
    strategy_name = Column(String(100), nullable=False)  # e.g., "Acquisitions", "Development"
    deployed_capital = Column(Float)
    current_value = Column(Float)
    allocation_percent = Column(Float)  # Target allocation %
    irr = Column(Float)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f'<InvestmentStrategy {self.id}: {self.strategy_name} for Fund {self.fund_id}>'

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
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
        """Create an InvestmentStrategyModel instance from a dictionary"""
        return InvestmentStrategyModel(
            fund_id=data.get('fundId'),
            strategy_name=data.get('strategyName'),
            deployed_capital=data.get('deployedCapital'),
            current_value=data.get('currentValue'),
            allocation_percent=data.get('allocationPercent'),
            irr=data.get('irr')
        )

    def update_from_dict(self, data):
        """Update model fields from a dictionary"""
        if 'strategyName' in data:
            self.strategy_name = data['strategyName']
        if 'deployedCapital' in data:
            self.deployed_capital = data['deployedCapital']
        if 'currentValue' in data:
            self.current_value = data['currentValue']
        if 'allocationPercent' in data:
            self.allocation_percent = data['allocationPercent']
        if 'irr' in data:
            self.irr = data['irr']

        self.updated_at = datetime.utcnow()


class CashFlowModel(db.Model):
    """
    SQLAlchemy model for fund cash flows
    Stores quarterly capital calls and distributions
    """
    __tablename__ = 'fund_cash_flows'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)  # 1, 2, 3, 4
    capital_calls = Column(Float)  # Outflows (negative)
    distributions = Column(Float)  # Inflows (positive)
    net_cash_flow = Column(Float)  # Distributions - Capital Calls
    created_at = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f'<CashFlow {self.id}: Fund {self.fund_id} Q{self.quarter} {self.year}>'

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
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
        """Create a CashFlowModel instance from a dictionary"""
        return CashFlowModel(
            fund_id=data.get('fundId'),
            year=data.get('year'),
            quarter=data.get('quarter'),
            capital_calls=data.get('capitalCalls'),
            distributions=data.get('distributions'),
            net_cash_flow=data.get('netCashFlow')
        )

    def update_from_dict(self, data):
        """Update model fields from a dictionary"""
        if 'year' in data:
            self.year = data['year']
        if 'quarter' in data:
            self.quarter = data['quarter']
        if 'capitalCalls' in data:
            self.capital_calls = data['capitalCalls']
        if 'distributions' in data:
            self.distributions = data['distributions']
        if 'netCashFlow' in data:
            self.net_cash_flow = data['netCashFlow']


class FundActivityModel(db.Model):
    """
    SQLAlchemy model for fund activities
    Stores transactions and events related to the fund
    """
    __tablename__ = 'fund_activities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False)
    activity_date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Float)
    status = Column(String(50))  # Completed, In Progress, Scheduled
    activity_type = Column(String(50))  # distribution, acquisition, refinancing, capital_call
    created_at = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f'<FundActivity {self.id}: {self.description[:30]}>'

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
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
        """Create a FundActivityModel instance from a dictionary"""
        from datetime import datetime as dt
        return FundActivityModel(
            fund_id=data.get('fundId'),
            activity_date=dt.fromisoformat(data['activityDate']).date() if data.get('activityDate') else None,
            description=data.get('description'),
            amount=data.get('amount'),
            status=data.get('status'),
            activity_type=data.get('activityType')
        )

    def update_from_dict(self, data):
        """Update model fields from a dictionary"""
        from datetime import datetime as dt

        if 'activityDate' in data:
            self.activity_date = dt.fromisoformat(data['activityDate']).date() if data['activityDate'] else None
        if 'description' in data:
            self.description = data['description']
        if 'amount' in data:
            self.amount = data['amount']
        if 'status' in data:
            self.status = data['status']
        if 'activityType' in data:
            self.activity_type = data['activityType']


class BenchmarkDataModel(db.Model):
    """
    SQLAlchemy model for benchmark comparison data
    Stores fund performance vs industry benchmarks
    """
    __tablename__ = 'benchmark_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False)
    metric_name = Column(String(100), nullable=False)  # Net IRR, TVPI, DPI
    fund_value = Column(Float)
    industry_benchmark = Column(Float)
    as_of_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f'<BenchmarkData {self.id}: {self.metric_name} for Fund {self.fund_id}>'

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        outperformance = self.fund_value - self.industry_benchmark if self.fund_value and self.industry_benchmark else 0
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
        """Create a BenchmarkDataModel instance from a dictionary"""
        from datetime import datetime as dt
        return BenchmarkDataModel(
            fund_id=data.get('fundId'),
            metric_name=data.get('metricName'),
            fund_value=data.get('fundValue'),
            industry_benchmark=data.get('industryBenchmark'),
            as_of_date=dt.fromisoformat(data['asOfDate']).date() if data.get('asOfDate') else None
        )

    def update_from_dict(self, data):
        """Update model fields from a dictionary"""
        from datetime import datetime as dt

        if 'metricName' in data:
            self.metric_name = data['metricName']
        if 'fundValue' in data:
            self.fund_value = data['fundValue']
        if 'industryBenchmark' in data:
            self.industry_benchmark = data['industryBenchmark']
        if 'asOfDate' in data:
            self.as_of_date = dt.fromisoformat(data['asOfDate']).date() if data['asOfDate'] else None
