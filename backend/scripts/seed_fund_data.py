"""
Seed fund data script
Populates the database with sample fund data matching the wireframe
"""
import sys
import os
from datetime import date, datetime

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
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


def seed_fund_data():
    """Seed the database with fund data matching wireframe"""

    app = create_app()

    with app.app_context():
        print("Starting fund data seeding...")

        # Check if fund already exists
        existing_fund = FundModel.query.filter_by(fund_name="Aequitas Fund I").first()
        if existing_fund:
            print("Fund data already exists. Skipping seeding.")
            return

        # 1. Create Fund
        print("Creating fund...")
        fund = FundModel(
            fund_name="Aequitas Fund I",
            fund_size=450000000,  # $450M
            status="active",
            vintage_year=2022,
            investment_period_start=date(2022, 1, 1),
            investment_period_end=date(2027, 6, 30)  # 2.5 years remaining from now
        )
        db.session.add(fund)
        db.session.flush()  # Get the fund ID
        fund_id = fund.id

        # 2. Create Fund Metrics
        print("Creating fund metrics...")
        metrics = FundMetricsModel(
            fund_id=fund_id,
            as_of_date=date(2024, 12, 30),
            deployed_capital=373000000,  # $373M
            remaining_capital=77000000,  # $77M ($450M - $373M)
            net_irr=12.4,
            tvpi=1.7,
            dpi=0.3,
            total_value=637000000  # $637M
        )
        db.session.add(metrics)

        # 3. Create Quarterly Performance (8 quarters: 2023 Q1-Q4, 2024 Q1-Q4)
        print("Creating quarterly performance data...")
        quarterly_irr_data = [
            (2023, 1, 10.2),
            (2023, 2, 10.8),
            (2023, 3, 11.5),
            (2023, 4, 11.9),
            (2024, 1, 12.0),
            (2024, 2, 12.2),
            (2024, 3, 12.3),
            (2024, 4, 12.4)
        ]

        for year, quarter, irr in quarterly_irr_data:
            perf = QuarterlyPerformanceModel(
                fund_id=fund_id,
                year=year,
                quarter=quarter,
                irr=irr
            )
            db.session.add(perf)

        # 4. Create Investment Strategies
        print("Creating investment strategies...")
        acquisitions = InvestmentStrategyModel(
            fund_id=fund_id,
            strategy_name="Acquisitions",
            deployed_capital=259000000,  # $259M
            current_value=310000000,  # $310M (growth)
            allocation_percent=60,
            irr=14.0
        )
        db.session.add(acquisitions)

        development = InvestmentStrategyModel(
            fund_id=fund_id,
            strategy_name="Development",
            deployed_capital=114000000,  # $114M
            current_value=130000000,  # $130M (growth)
            allocation_percent=40,
            irr=9.0
        )
        db.session.add(development)

        # 5. Create Cash Flows (8 quarters)
        print("Creating cash flow data...")
        cash_flow_data = [
            # (year, quarter, capital_calls, distributions, net_cash_flow)
            (2023, 1, 2500000, 800000, -1700000),
            (2023, 2, 2300000, 900000, -1400000),
            (2023, 3, 2400000, 1100000, -1300000),
            (2023, 4, 2200000, 1200000, -1000000),
            (2024, 1, 2100000, 1300000, -800000),
            (2024, 2, 2000000, 1000000, -1000000),
            (2024, 3, 1800000, 1100000, -700000),
            (2024, 4, 2200000, 800000, -1400000)
        ]

        for year, quarter, calls, distributions, net in cash_flow_data:
            cash_flow = CashFlowModel(
                fund_id=fund_id,
                year=year,
                quarter=quarter,
                capital_calls=calls,
                distributions=distributions,
                net_cash_flow=net
            )
            db.session.add(cash_flow)

        # 6. Create Benchmarks
        print("Creating benchmark data...")
        benchmarks = [
            ("Net IRR", 12.4, 10.8),
            ("TVPI", 1.7, 1.4),
            ("DPI", 0.3, 0.3)
        ]

        for metric_name, fund_value, industry_benchmark in benchmarks:
            benchmark = BenchmarkDataModel(
                fund_id=fund_id,
                metric_name=metric_name,
                fund_value=fund_value,
                industry_benchmark=industry_benchmark,
                as_of_date=date(2024, 12, 30)
            )
            db.session.add(benchmark)

        # 7. Create Recent Activities
        print("Creating fund activities...")
        activities = [
            (
                date(2024, 11, 15),
                "Riverside Commons refinancing distribution",
                410000000,  # $410M
                "Completed",
                "distribution"
            ),
            (
                date(2024, 12, 5),
                "New acquisition - Metro Gardens, Denver",
                28000000,  # $28M
                "In Progress",
                "acquisition"
            ),
            (
                date(2024, 12, 20),
                "Harbor Park quarterly distribution",
                2800000,  # $2.8M
                "Scheduled",
                "distribution"
            ),
            (
                date(2025, 1, 10),
                "Greenwood Funding - Sunrise Phase 2",
                15000000,  # $15M
                "Scheduled",
                "capital_call"
            )
        ]

        for activity_date, description, amount, status, activity_type in activities:
            activity = FundActivityModel(
                fund_id=fund_id,
                activity_date=activity_date,
                description=description,
                amount=amount,
                status=status,
                activity_type=activity_type
            )
            db.session.add(activity)

        # Commit all changes
        print("Committing to database...")
        db.session.commit()

        print("✅ Fund data seeded successfully!")
        print(f"   Fund ID: {fund_id}")
        print(f"   Fund Name: Aequitas Fund I")
        print(f"   Fund Size: $450M")
        print(f"   Deployed Capital: $373M")
        print(f"   Net IRR: 12.4%")


if __name__ == '__main__':
    seed_fund_data()
