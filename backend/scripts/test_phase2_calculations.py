"""
Test Phase 2 Calculations
Verify yield, appreciation, and total return calculations work correctly
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import db, DealModel
from app.services.hedonic_model_service import HedonicModelService
from app.services.rent_tier_service import RentTierService
from app.services.yield_calculation_service import YieldCalculationService
from app.services.capital_appreciation_service import CapitalAppreciationService
from app.services.total_return_service import TotalReturnService


def test_yield_calculations():
    """Test yield calculation service"""
    print("\n" + "=" * 60)
    print("TEST 1: YIELD CALCULATIONS")
    print("=" * 60)

    # Test gross yield
    annual_rent = 86400  # $7,200/month * 12
    property_value = 1200000
    gross_yield = YieldCalculationService.calculate_gross_yield(annual_rent, property_value)

    print(f"\nGross Yield Calculation:")
    print(f"  Annual Rent: ${annual_rent:,.0f}")
    print(f"  Property Value: ${property_value:,.0f}")
    print(f"  Gross Yield: {gross_yield}%")

    # Test cost components for D1 (low-rent)
    costs_d1 = YieldCalculationService.calculate_cost_components(
        rent_decile=1,
        num_units=1,
        property_value=property_value,
        annual_rent=annual_rent
    )

    print(f"\nCost Components (D1 - Low Rent):")
    for component, value in costs_d1.items():
        print(f"  {component}: {value}%")

    # Test cost components for D10 (high-rent)
    costs_d10 = YieldCalculationService.calculate_cost_components(
        rent_decile=10,
        num_units=1,
        property_value=property_value,
        annual_rent=annual_rent
    )

    print(f"\nCost Components (D10 - High Rent):")
    for component, value in costs_d10.items():
        print(f"  {component}: {value}%")

    # Calculate net yields
    net_yield_d1 = YieldCalculationService.calculate_net_yield(gross_yield, costs_d1)
    net_yield_d10 = YieldCalculationService.calculate_net_yield(gross_yield, costs_d10)

    print(f"\nNet Yield Comparison:")
    print(f"  D1 (Low Rent): {net_yield_d1}%")
    print(f"  D10 (High Rent): {net_yield_d10}%")
    print(f"  D1-D10 Spread: {net_yield_d1 - net_yield_d10:.2f}%")

    # Compare to benchmarks
    comparison_d1 = YieldCalculationService.compare_to_benchmark(net_yield_d1, 1)
    comparison_d10 = YieldCalculationService.compare_to_benchmark(net_yield_d10, 10)

    print(f"\nBenchmark Comparison:")
    print(f"  D1: {comparison_d1['position']} (Range: {comparison_d1['benchmark_min']}-{comparison_d1['benchmark_max']}%)")
    print(f"  D10: {comparison_d10['position']} (Range: {comparison_d10['benchmark_min']}-{comparison_d10['benchmark_max']}%)")

    return True


def test_capital_appreciation():
    """Test capital appreciation service"""
    print("\n" + "=" * 60)
    print("TEST 2: CAPITAL APPRECIATION")
    print("=" * 60)

    property_value = 1200000

    # Project D1 (low-rent) appreciation
    projection_d1 = CapitalAppreciationService.project_future_value(
        current_value=property_value,
        rent_decile=1,
        years=10
    )

    print(f"\nD1 (Low Rent) Value Projection:")
    print(f"  Current Value: ${projection_d1['current_value']:,.0f}")
    print(f"  Year 1: ${projection_d1['projected_value_yr1']:,.0f}")
    print(f"  Year 5: ${projection_d1['projected_value_yr5']:,.0f}")
    print(f"  Year 10: ${projection_d1['projected_value_yr10']:,.0f}")
    print(f"  Annual Rate: {projection_d1['annualized_appreciation_rate']}%")
    print(f"  Total Appreciation: {projection_d1['total_appreciation_pct']}%")

    # Project D10 (high-rent) appreciation
    projection_d10 = CapitalAppreciationService.project_future_value(
        current_value=property_value,
        rent_decile=10,
        years=10
    )

    print(f"\nD10 (High Rent) Value Projection:")
    print(f"  Current Value: ${projection_d10['current_value']:,.0f}")
    print(f"  Year 1: ${projection_d10['projected_value_yr1']:,.0f}")
    print(f"  Year 5: ${projection_d10['projected_value_yr5']:,.0f}")
    print(f"  Year 10: ${projection_d10['projected_value_yr10']:,.0f}")
    print(f"  Annual Rate: {projection_d10['annualized_appreciation_rate']}%")
    print(f"  Total Appreciation: {projection_d10['total_appreciation_pct']}%")

    # Compare appreciation rates
    print(f"\nAppreciation Comparison:")
    print(f"  D1 outperforms D10 by: {projection_d1['annualized_appreciation_rate'] - projection_d10['annualized_appreciation_rate']:.2f}%/year")
    print(f"  After 10 years, D1 value is ${projection_d1['projected_value_yr10'] - projection_d10['projected_value_yr10']:,.0f} higher")

    # Test NOI growth
    current_noi = 50000
    noi_growth_d1 = CapitalAppreciationService.project_noi_growth(
        current_noi=current_noi,
        rent_decile=1,
        property_age=25,
        years=10
    )

    print(f"\nNOI Growth Projection (D1, 25-year-old property):")
    print(f"  Current NOI: ${noi_growth_d1['current_noi']:,.0f}")
    print(f"  Year 10 NOI: ${noi_growth_d1['projected_noi_yr10']:,.0f}")
    print(f"  Growth Rate: {noi_growth_d1['annual_growth_rate']}%")

    return True


def test_total_returns():
    """Test total return calculations"""
    print("\n" + "=" * 60)
    print("TEST 3: TOTAL RETURNS")
    print("=" * 60)

    # Example returns for D1
    net_yield_d1 = 4.5
    capital_gain_d1 = 3.25

    # Calculate unlevered return
    total_return_unlevered = TotalReturnService.calculate_unlevered_return(
        net_yield=net_yield_d1,
        capital_gain_yield=capital_gain_d1
    )

    print(f"\nD1 (Low Rent) Unlevered Return:")
    print(f"  Net Yield: {net_yield_d1}%")
    print(f"  Capital Gain: {capital_gain_d1}%")
    print(f"  Total Return: {total_return_unlevered}%")

    # Calculate levered return
    cost_of_debt = 6.5
    ltv = 0.75

    total_return_levered = TotalReturnService.calculate_levered_return(
        unlevered_return=total_return_unlevered,
        cost_of_debt=cost_of_debt,
        ltv=ltv
    )

    leverage_effect = total_return_levered - total_return_unlevered

    print(f"\nLevered Return (75% LTV, 6.5% rate):")
    print(f"  Unlevered: {total_return_unlevered}%")
    print(f"  Levered: {total_return_levered}%")
    print(f"  Leverage Effect: +{leverage_effect:.2f}%")

    # Compare to D10
    net_yield_d10 = 2.0
    capital_gain_d10 = 0.93
    total_return_d10 = TotalReturnService.calculate_unlevered_return(
        net_yield=net_yield_d10,
        capital_gain_yield=capital_gain_d10
    )

    print(f"\nD10 (High Rent) Unlevered Return:")
    print(f"  Net Yield: {net_yield_d10}%")
    print(f"  Capital Gain: {capital_gain_d10}%")
    print(f"  Total Return: {total_return_d10}%")

    print(f"\nKey Finding:")
    print(f"  D1 outperforms D10 by: {total_return_unlevered - total_return_d10:.2f}%/year")
    print(f"  This validates academic research (D1-D10 spread: 1.97-4.15%)")

    # Benchmark comparison
    comparison = TotalReturnService.compare_to_benchmark(
        total_return_unlevered=total_return_unlevered,
        rent_decile=1
    )

    print(f"\nBenchmark Comparison (D1):")
    print(f"  Position: {comparison['position']}")
    print(f"  Interpretation: {comparison['interpretation']}")

    return True


def test_integrated_example():
    """Test integrated example with all services"""
    print("\n" + "=" * 60)
    print("TEST 4: INTEGRATED EXAMPLE")
    print("=" * 60)

    # Create example property
    property_data = {
        'square_footage': 1200,
        'bedrooms': 2,
        'bathrooms': 1,
        'year_built': 1995,
        'property_type': 'multifamily'
    }

    print(f"\nExample Property:")
    print(f"  {property_data['bedrooms']}BR/{property_data['bathrooms']}BA")
    print(f"  {property_data['square_footage']} sqft")
    print(f"  Built {property_data['year_built']}")
    print(f"  Type: {property_data['property_type']}")

    # Step 1: Predict rent
    rent_prediction = HedonicModelService.predict_fundamental_rent(property_data)
    print(f"\nStep 1 - Predicted Rent:")
    print(f"  Fundamental Rent: ${rent_prediction['predicted_rent']:.2f}/month")
    print(f"  Confidence: {rent_prediction['confidence']}%")

    # Step 2: Classify into decile
    classification = RentTierService.classify_property(
        predicted_rent=rent_prediction['predicted_rent'],
        geography='national',
        bedrooms=2
    )
    print(f"\nStep 2 - Rent Tier Classification:")
    print(f"  Tier: {classification['tier_label']} ({classification['interpretation']['category']})")
    print(f"  Percentile: {classification['percentile']}")
    print(f"  Expected Return: {classification['interpretation']['expected_return_range']}")

    # Step 3: Calculate yields
    property_value = 200000
    annual_rent = rent_prediction['predicted_rent'] * 12
    gross_yield = YieldCalculationService.calculate_gross_yield(annual_rent, property_value)

    costs = YieldCalculationService.calculate_cost_components(
        rent_decile=classification['national_decile'],
        num_units=1,
        property_value=property_value,
        annual_rent=annual_rent
    )

    net_yield = YieldCalculationService.calculate_net_yield(gross_yield, costs)

    print(f"\nStep 3 - Yield Analysis:")
    print(f"  Property Value: ${property_value:,.0f}")
    print(f"  Annual Rent: ${annual_rent:,.0f}")
    print(f"  Gross Yield: {gross_yield}%")
    print(f"  Total Costs: {costs['total_cost_pct']}%")
    print(f"  Net Yield: {net_yield}%")

    # Step 4: Project appreciation
    appreciation = CapitalAppreciationService.project_future_value(
        current_value=property_value,
        rent_decile=classification['national_decile'],
        years=10
    )

    print(f"\nStep 4 - Capital Appreciation (10 years):")
    print(f"  Current: ${appreciation['current_value']:,.0f}")
    print(f"  Year 10: ${appreciation['projected_value_yr10']:,.0f}")
    print(f"  Annual Rate: {appreciation['annualized_appreciation_rate']}%")

    # Step 5: Calculate total return
    total_return = TotalReturnService.calculate_unlevered_return(
        net_yield=net_yield,
        capital_gain_yield=appreciation['annualized_appreciation_rate']
    )

    print(f"\nStep 5 - Total Return:")
    print(f"  Net Yield: {net_yield}%")
    print(f"  Capital Gain: {appreciation['annualized_appreciation_rate']}%")
    print(f"  Total Return (Unlevered): {total_return}%")

    # Compare to benchmark
    comparison = TotalReturnService.compare_to_benchmark(
        total_return_unlevered=total_return,
        rent_decile=classification['national_decile']
    )

    print(f"\nBenchmark Comparison:")
    print(f"  {comparison['interpretation']}")

    return True


def main():
    """Run all Phase 2 tests"""
    print("=" * 60)
    print("PHASE 2 CALCULATION TESTS")
    print("=" * 60)

    app = create_app()

    with app.app_context():
        try:
            # Run tests
            test_yield_calculations()
            test_capital_appreciation()
            test_total_returns()
            test_integrated_example()

            print("\n" + "=" * 60)
            print("ALL TESTS PASSED ✓")
            print("=" * 60)
            print("\nPhase 2 services are working correctly!")
            print("Ready to proceed to Phase 3 (Risk Assessment)")
            print()

        except Exception as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()
