"""
Seed benchmark data from academic research
Populates RiskBenchmarkData table with findings from research papers

Data Source: Academic research on affordable housing returns
Tables: 2, A3, B2, B3 from research papers
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import db, RiskBenchmarkData, HedonicModelCoefficients
from app import create_app


def seed_us_benchmarks():
    """
    Seed US benchmark data (primary focus)

    Data from research showing:
    - D1 (low-rent) properties: Higher returns, lower risk
    - D10 (high-rent) properties: Lower returns, higher risk
    """

    us_benchmarks = [
        # Decile 1 (Bottom 10% - Lowest Rents)
        {
            'rent_decile': 1,
            'geography': 'US',
            'net_yield_min': 3.55,
            'net_yield_max': 5.70,
            'capital_gain_min': 0.99,
            'capital_gain_max': 5.50,
            'total_return_min': 4.53,
            'total_return_max': 11.19,
            'maintenance_cost_pct': 1.5,
            'turnover_cost_pct': 2.5,
            'default_cost_pct': 0.9,
            'systematic_risk_beta': -0.19,  # Negative beta vs GDP
            'cash_flow_volatility': 7.5
        },
        # Decile 2
        {
            'rent_decile': 2,
            'geography': 'US',
            'net_yield_min': 3.43,
            'net_yield_max': 5.88,
            'capital_gain_min': 0.92,
            'capital_gain_max': 5.15,
            'total_return_min': 4.35,
            'total_return_max': 11.03,
            'maintenance_cost_pct': 1.4,
            'turnover_cost_pct': 2.4,
            'default_cost_pct': 0.9,
            'systematic_risk_beta': -0.15,
            'cash_flow_volatility': 7.8
        },
        # Decile 3
        {
            'rent_decile': 3,
            'geography': 'US',
            'net_yield_min': 3.23,
            'net_yield_max': 5.81,
            'capital_gain_min': 0.71,
            'capital_gain_max': 4.60,
            'total_return_min': 3.94,
            'total_return_max': 10.41,
            'maintenance_cost_pct': 1.3,
            'turnover_cost_pct': 2.3,
            'default_cost_pct': 0.8,
            'systematic_risk_beta': -0.10,
            'cash_flow_volatility': 8.0
        },
        # Decile 4
        {
            'rent_decile': 4,
            'geography': 'US',
            'net_yield_min': 3.10,
            'net_yield_max': 5.72,
            'capital_gain_min': 0.60,
            'capital_gain_max': 4.07,
            'total_return_min': 3.70,
            'total_return_max': 9.79,
            'maintenance_cost_pct': 1.2,
            'turnover_cost_pct': 2.2,
            'default_cost_pct': 0.8,
            'systematic_risk_beta': -0.05,
            'cash_flow_volatility': 7.9
        },
        # Decile 5 (Median)
        {
            'rent_decile': 5,
            'geography': 'US',
            'net_yield_min': 2.94,
            'net_yield_max': 5.58,
            'capital_gain_min': 0.48,
            'capital_gain_max': 3.74,
            'total_return_min': 3.42,
            'total_return_max': 9.32,
            'maintenance_cost_pct': 1.1,
            'turnover_cost_pct': 2.1,
            'default_cost_pct': 0.7,
            'systematic_risk_beta': 0.00,
            'cash_flow_volatility': 7.5
        },
        # Decile 6
        {
            'rent_decile': 6,
            'geography': 'US',
            'net_yield_min': 2.82,
            'net_yield_max': 5.42,
            'capital_gain_min': 0.39,
            'capital_gain_max': 3.18,
            'total_return_min': 3.21,
            'total_return_max': 8.60,
            'maintenance_cost_pct': 1.0,
            'turnover_cost_pct': 2.0,
            'default_cost_pct': 0.7,
            'systematic_risk_beta': 0.02,
            'cash_flow_volatility': 7.2
        },
        # Decile 7
        {
            'rent_decile': 7,
            'geography': 'US',
            'net_yield_min': 2.73,
            'net_yield_max': 5.31,
            'capital_gain_min': 0.46,
            'capital_gain_max': 2.91,
            'total_return_min': 3.19,
            'total_return_max': 8.22,
            'maintenance_cost_pct': 0.9,
            'turnover_cost_pct': 1.9,
            'default_cost_pct': 0.6,
            'systematic_risk_beta': 0.03,
            'cash_flow_volatility': 7.0
        },
        # Decile 8
        {
            'rent_decile': 8,
            'geography': 'US',
            'net_yield_min': 2.61,
            'net_yield_max': 5.21,
            'capital_gain_min': 0.40,
            'capital_gain_max': 2.55,
            'total_return_min': 3.01,
            'total_return_max': 7.76,
            'maintenance_cost_pct': 0.8,
            'turnover_cost_pct': 1.8,
            'default_cost_pct': 0.6,
            'systematic_risk_beta': 0.04,
            'cash_flow_volatility': 6.8
        },
        # Decile 9
        {
            'rent_decile': 9,
            'geography': 'US',
            'net_yield_min': 2.52,
            'net_yield_max': 5.10,
            'capital_gain_min': 0.32,
            'capital_gain_max': 2.14,
            'total_return_min': 2.84,
            'total_return_max': 7.24,
            'maintenance_cost_pct': 0.7,
            'turnover_cost_pct': 1.8,
            'default_cost_pct': 0.5,
            'systematic_risk_beta': 0.04,
            'cash_flow_volatility': 6.5
        },
        # Decile 10 (Top 10% - Highest Rents)
        {
            'rent_decile': 10,
            'geography': 'US',
            'net_yield_min': 2.66,
            'net_yield_max': 5.09,
            'capital_gain_min': -0.10,
            'capital_gain_max': 1.95,
            'total_return_min': 2.56,
            'total_return_max': 7.04,
            'maintenance_cost_pct': 0.6,
            'turnover_cost_pct': 1.8,
            'default_cost_pct': 0.5,
            'systematic_risk_beta': 0.04,
            'cash_flow_volatility': 6.0
        }
    ]

    print("Seeding US benchmark data...")
    for benchmark in us_benchmarks:
        existing = RiskBenchmarkData.query.filter_by(
            rent_decile=benchmark['rent_decile'],
            geography=benchmark['geography']
        ).first()

        if existing:
            print(f"  Updating D{benchmark['rent_decile']} (US)...")
            for key, value in benchmark.items():
                if key not in ['rent_decile', 'geography']:
                    setattr(existing, key, value)
        else:
            print(f"  Creating D{benchmark['rent_decile']} (US)...")
            new_benchmark = RiskBenchmarkData(**benchmark)
            db.session.add(new_benchmark)

    db.session.commit()
    print(f"✓ Seeded {len(us_benchmarks)} US benchmark records")


def seed_belgium_benchmarks():
    """
    Seed Belgium benchmark data (for comparison)
    """
    belgium_benchmarks = [
        {
            'rent_decile': 1,
            'geography': 'Belgium',
            'net_yield_min': 3.55,
            'net_yield_max': 3.55,
            'capital_gain_min': 0.99,
            'capital_gain_max': 0.99,
            'total_return_min': 4.53,
            'total_return_max': 4.53,
            'maintenance_cost_pct': 1.6,
            'turnover_cost_pct': 2.7,
            'default_cost_pct': 0.9,
            'systematic_risk_beta': -0.22,
            'cash_flow_volatility': 11.5
        },
        {
            'rent_decile': 5,
            'geography': 'Belgium',
            'net_yield_min': 2.94,
            'net_yield_max': 2.94,
            'capital_gain_min': 0.48,
            'capital_gain_max': 0.48,
            'total_return_min': 3.42,
            'total_return_max': 3.42,
            'maintenance_cost_pct': 1.1,
            'turnover_cost_pct': 2.1,
            'default_cost_pct': 0.7,
            'systematic_risk_beta': 0.00,
            'cash_flow_volatility': 8.5
        },
        {
            'rent_decile': 10,
            'geography': 'Belgium',
            'net_yield_min': 2.66,
            'net_yield_max': 2.66,
            'capital_gain_min': -0.10,
            'capital_gain_max': -0.10,
            'total_return_min': 2.56,
            'total_return_max': 2.56,
            'maintenance_cost_pct': 0.4,
            'turnover_cost_pct': 1.7,
            'default_cost_pct': 0.5,
            'systematic_risk_beta': 0.05,
            'cash_flow_volatility': 7.0
        }
    ]

    print("\nSeeding Belgium benchmark data (for comparison)...")
    for benchmark in belgium_benchmarks:
        existing = RiskBenchmarkData.query.filter_by(
            rent_decile=benchmark['rent_decile'],
            geography=benchmark['geography']
        ).first()

        if existing:
            print(f"  Updating D{benchmark['rent_decile']} (Belgium)...")
            for key, value in benchmark.items():
                if key not in ['rent_decile', 'geography']:
                    setattr(existing, key, value)
        else:
            print(f"  Creating D{benchmark['rent_decile']} (Belgium)...")
            new_benchmark = RiskBenchmarkData(**benchmark)
            db.session.add(new_benchmark)

    db.session.commit()
    print(f"✓ Seeded {len(belgium_benchmarks)} Belgium benchmark records")


def seed_netherlands_benchmarks():
    """
    Seed Netherlands benchmark data (for comparison)
    """
    netherlands_benchmarks = [
        {
            'rent_decile': 1,
            'geography': 'Netherlands',
            'net_yield_min': 4.42,
            'net_yield_max': 4.42,
            'capital_gain_min': 5.68,
            'capital_gain_max': 5.68,
            'total_return_min': 10.10,
            'total_return_max': 10.10,
            'maintenance_cost_pct': 1.4,
            'turnover_cost_pct': 5.4,  # Higher turnover in Netherlands
            'default_cost_pct': 0.9,
            'systematic_risk_beta': -0.18,
            'cash_flow_volatility': 11.5
        },
        {
            'rent_decile': 5,
            'geography': 'Netherlands',
            'net_yield_min': 3.51,
            'net_yield_max': 3.51,
            'capital_gain_min': 6.08,
            'capital_gain_max': 6.08,
            'total_return_min': 9.59,
            'total_return_max': 9.59,
            'maintenance_cost_pct': 1.0,
            'turnover_cost_pct': 5.2,
            'default_cost_pct': 0.7,
            'systematic_risk_beta': 0.00,
            'cash_flow_volatility': 8.5
        },
        {
            'rent_decile': 10,
            'geography': 'Netherlands',
            'net_yield_min': 3.29,
            'net_yield_max': 3.29,
            'capital_gain_min': 3.08,
            'capital_gain_max': 3.08,
            'total_return_min': 6.37,
            'total_return_max': 6.37,
            'maintenance_cost_pct': 0.5,
            'turnover_cost_pct': 5.0,
            'default_cost_pct': 0.5,
            'systematic_risk_beta': 0.03,
            'cash_flow_volatility': 5.5
        }
    ]

    print("\nSeeding Netherlands benchmark data (for comparison)...")
    for benchmark in netherlands_benchmarks:
        existing = RiskBenchmarkData.query.filter_by(
            rent_decile=benchmark['rent_decile'],
            geography=benchmark['geography']
        ).first()

        if existing:
            print(f"  Updating D{benchmark['rent_decile']} (Netherlands)...")
            for key, value in benchmark.items():
                if key not in ['rent_decile', 'geography']:
                    setattr(existing, key, value)
        else:
            print(f"  Creating D{benchmark['rent_decile']} (Netherlands)...")
            new_benchmark = RiskBenchmarkData(**benchmark)
            db.session.add(new_benchmark)

    db.session.commit()
    print(f"✓ Seeded {len(netherlands_benchmarks)} Netherlands benchmark records")


def seed_hedonic_coefficients():
    """
    Seed initial hedonic model coefficients for US national model
    Based on calibration to research findings
    """
    print("\nSeeding hedonic model coefficients...")

    existing = HedonicModelCoefficients.query.filter_by(
        model_version='v1',
        region='national'
    ).first()

    if existing:
        print("  Hedonic coefficients already exist, skipping...")
        return

    coefficients = HedonicModelCoefficients(
        model_version='v1',
        region='national',
        coef_sqft=0.00035,
        coef_bedrooms=0.12,
        coef_bathrooms=0.08,
        coef_age=-0.003,
        coef_property_type_multi=-0.05,
        coef_property_type_condo=0.02,
        intercept=6.2,
        neighborhood_effects='{}',  # Empty for now, will be populated later
        time_effects='{}',  # Empty for now
        r_squared=0.65,
        rmse=0.15,
        sample_size=10000
    )

    db.session.add(coefficients)
    db.session.commit()
    print("✓ Seeded hedonic model coefficients (v1, national)")


def main():
    """
    Main seeding function
    """
    print("=" * 60)
    print("RISK ASSESSMENT BENCHMARK DATA SEEDING")
    print("=" * 60)
    print()

    app = create_app()

    with app.app_context():
        # Seed all benchmark data
        seed_us_benchmarks()
        seed_belgium_benchmarks()
        seed_netherlands_benchmarks()
        seed_hedonic_coefficients()

        # Summary
        print("\n" + "=" * 60)
        print("SEEDING COMPLETE")
        print("=" * 60)

        total_benchmarks = RiskBenchmarkData.query.count()
        total_coefficients = HedonicModelCoefficients.query.count()

        print(f"\nTotal benchmark records: {total_benchmarks}")
        print(f"Total hedonic coefficient sets: {total_coefficients}")
        print()
        print("Key findings from research:")
        print("  • D1 (low-rent) total return: 4.53-11.19% (US)")
        print("  • D10 (high-rent) total return: 2.56-7.04% (US)")
        print("  • D1-D10 spread: 1.97-4.15 percentage points")
        print("  • Risk: D1 has LOWER systematic risk than D10")
        print()


if __name__ == '__main__':
    main()
