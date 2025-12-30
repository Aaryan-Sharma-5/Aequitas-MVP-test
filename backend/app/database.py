"""
Database configuration and models for Aequitas MVP
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
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
