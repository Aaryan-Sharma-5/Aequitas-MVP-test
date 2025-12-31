"""
Limits to Arbitrage Service
Identifies market inefficiencies and arbitrage opportunities

Academic Research Basis:
- D1 properties have HIGHEST arbitrage opportunity
- Three barriers prevent efficient pricing:
  1. Renter Constraints: Can't afford to buy (stuck renting)
  2. Institutional Constraints: Avoid low-rent (stigma, liquidity)
  3. Medium Landlord Opportunity: 10-50 unit operators thrive here

Result: Mispricing persists, creating excess returns for sophisticated investors
"""

from typing import Dict, Optional
from app.database import db, RiskBenchmarkData


class ArbitrageLimitsService:
    """
    Service for identifying limits to arbitrage and market opportunities
    """

    @staticmethod
    def assess_renter_constraints(
        monthly_rent: float,
        median_income: Optional[float] = None,
        home_price_to_rent_ratio: Optional[float] = None,
        rent_decile: Optional[int] = None
    ) -> Dict:
        """
        Assess whether renters can afford to buy (or are constrained to rent)

        High renter constraints = stable rental demand = arbitrage opportunity

        Tests:
        1. Rent burden (rent as % of income)
        2. Ability to save for down payment
        3. Home price to rent ratio (buying vs renting economics)
        4. Credit access (proxied by decile)

        Args:
            monthly_rent: Property's monthly rent
            median_income: Area median household income (annual)
            home_price_to_rent_ratio: Local house price / annual rent ratio
            rent_decile: Property's rent tier

        Returns:
            {
                'rent_burden_pct': 35.0,
                'can_afford_down_payment': False,
                'years_to_save_down_payment': 12.5,
                'buying_vs_renting_ratio': 18.0,
                'credit_access': 'Limited',
                'renter_constraint_score': 75.0,  # 0-100, higher = more constrained
                'interpretation': 'High renter constraints - tenants unlikely to leave'
            }
        """

        # Estimate median income if not provided (based on rent)
        if median_income is None:
            # Rule of thumb: rent should be ~30% of income
            # Reverse engineer: income = rent * 12 / 0.30
            estimated_income = (monthly_rent * 12) / 0.30
            median_income = estimated_income

        # Test 1: Rent Burden (rent as % of income)
        annual_rent = monthly_rent * 12
        rent_burden_pct = (annual_rent / median_income) * 100

        # Score: Higher burden = higher constraint (0-30 points)
        if rent_burden_pct < 25:
            rent_burden_score = 5.0
        elif rent_burden_pct < 30:
            rent_burden_score = 10.0
        elif rent_burden_pct < 35:
            rent_burden_score = 20.0
        else:
            rent_burden_score = 30.0

        # Test 2: Down Payment Affordability
        # Assume 20% down payment needed
        # Assume 10% savings rate from disposable income
        estimated_home_price = annual_rent * (home_price_to_rent_ratio or 15)
        down_payment_needed = estimated_home_price * 0.20
        annual_savings = max((median_income - annual_rent) * 0.10, 0)

        if annual_savings > 0:
            years_to_save = down_payment_needed / annual_savings
        else:
            years_to_save = 999  # Effectively never

        can_afford_down_payment = years_to_save < 5

        # Score: More years = higher constraint (0-25 points)
        if years_to_save < 3:
            down_payment_score = 0.0
        elif years_to_save < 5:
            down_payment_score = 5.0
        elif years_to_save < 10:
            down_payment_score = 15.0
        else:
            down_payment_score = 25.0

        # Test 3: Buying vs Renting Economics
        buying_vs_renting_ratio = home_price_to_rent_ratio or 15

        # Higher ratio = renting is cheaper = higher renter constraint (0-20 points)
        if buying_vs_renting_ratio < 12:
            buy_vs_rent_score = 0.0
        elif buying_vs_renting_ratio < 15:
            buy_vs_rent_score = 5.0
        elif buying_vs_renting_ratio < 18:
            buy_vs_rent_score = 10.0
        elif buying_vs_renting_ratio < 22:
            buy_vs_rent_score = 15.0
        else:
            buy_vs_rent_score = 20.0

        # Test 4: Credit Access (proxied by rent decile)
        # D1-D3: Limited credit access
        # D4-D7: Moderate credit access
        # D8-D10: Good credit access
        credit_access = 'Unknown'
        credit_score = 0.0

        if rent_decile:
            if rent_decile <= 3:
                credit_access = 'Limited'
                credit_score = 25.0
            elif rent_decile <= 7:
                credit_access = 'Moderate'
                credit_score = 12.5
            else:
                credit_access = 'Good'
                credit_score = 0.0

        # Calculate composite renter constraint score (0-100)
        renter_constraint_score = (
            rent_burden_score +
            down_payment_score +
            buy_vs_rent_score +
            credit_score
        )

        renter_constraint_score = min(renter_constraint_score, 100.0)

        # Interpretation
        if renter_constraint_score > 70:
            interpretation = 'Very high renter constraints - tenants cannot easily transition to homeownership'
        elif renter_constraint_score > 50:
            interpretation = 'High renter constraints - tenants unlikely to leave for ownership'
        elif renter_constraint_score > 30:
            interpretation = 'Moderate renter constraints - some tenants may transition to ownership'
        else:
            interpretation = 'Low renter constraints - tenants can afford to buy'

        return {
            'rent_burden_pct': round(rent_burden_pct, 1),
            'can_afford_down_payment': can_afford_down_payment,
            'years_to_save_down_payment': round(years_to_save, 1) if years_to_save < 999 else 'Never',
            'buying_vs_renting_ratio': buying_vs_renting_ratio,
            'credit_access': credit_access,
            'renter_constraint_score': round(renter_constraint_score, 1),
            'interpretation': interpretation,
            'components': {
                'rent_burden_score': rent_burden_score,
                'down_payment_score': down_payment_score,
                'buy_vs_rent_score': buy_vs_rent_score,
                'credit_score': credit_score
            }
        }

    @staticmethod
    def assess_institutional_constraints(
        rent_decile: int,
        property_value: float,
        num_units: int = 1,
        liquidity_score: Optional[float] = None
    ) -> Dict:
        """
        Assess institutional investor barriers

        High institutional constraints = less competition = arbitrage opportunity

        Barriers:
        1. Deal size too small (institutions need $10M+ deals)
        2. Stigma against low-rent properties
        3. ESG/reputational concerns
        4. Liquidity concerns
        5. Management intensity

        Args:
            rent_decile: Property's rent tier
            property_value: Total property value
            num_units: Number of units
            liquidity_score: Market liquidity (0-100, optional)

        Returns:
            {
                'deal_size_barrier': True,
                'stigma_barrier': True,
                'management_intensity': 'High',
                'liquidity_concern': 'High',
                'institutional_constraint_score': 85.0,  # 0-100, higher = more barriers
                'interpretation': 'Very high institutional barriers - creates opportunity'
            }
        """

        # Barrier 1: Deal Size
        # Institutions typically need $10M+ minimum deal size
        deal_size_barrier = property_value < 10_000_000

        if property_value >= 50_000_000:
            deal_size_score = 0.0
        elif property_value >= 10_000_000:
            deal_size_score = 10.0
        elif property_value >= 5_000_000:
            deal_size_score = 20.0
        else:
            deal_size_score = 30.0

        # Barrier 2: Stigma Against Low-Rent
        # D1-D3: High stigma
        # D4-D7: Moderate stigma
        # D8-D10: No stigma (institutional preference)
        stigma_barrier = rent_decile <= 4

        if rent_decile <= 2:
            stigma_score = 30.0
        elif rent_decile <= 4:
            stigma_score = 20.0
        elif rent_decile <= 7:
            stigma_score = 10.0
        else:
            stigma_score = 0.0

        # Barrier 3: Management Intensity
        # Low-rent properties require more hands-on management
        # Institutions prefer passive, scalable management

        if rent_decile <= 3:
            management_intensity = 'High'
            management_score = 20.0
        elif rent_decile <= 7:
            management_intensity = 'Moderate'
            management_score = 10.0
        else:
            management_intensity = 'Low'
            management_score = 0.0

        # Barrier 4: Liquidity Concerns
        # Low-rent properties have shallower buyer pools
        if liquidity_score is not None:
            liquidity_concern_score = (100 - liquidity_score) * 0.15  # Max 15 points
            if liquidity_score < 30:
                liquidity_concern = 'High'
            elif liquidity_score < 60:
                liquidity_concern = 'Moderate'
            else:
                liquidity_concern = 'Low'
        else:
            # Estimate from decile and size
            if rent_decile <= 3 and num_units < 20:
                liquidity_concern = 'High'
                liquidity_concern_score = 15.0
            elif rent_decile <= 5 or num_units < 10:
                liquidity_concern = 'Moderate'
                liquidity_concern_score = 10.0
            else:
                liquidity_concern = 'Low'
                liquidity_concern_score = 5.0

        # Barrier 5: ESG/Reputational Concerns
        # Some institutions avoid affordable housing due to perceived reputational risk
        if rent_decile <= 2:
            esg_score = 5.0
        else:
            esg_score = 0.0

        # Calculate composite institutional constraint score (0-100)
        institutional_constraint_score = (
            deal_size_score +
            stigma_score +
            management_score +
            liquidity_concern_score +
            esg_score
        )

        institutional_constraint_score = min(institutional_constraint_score, 100.0)

        # Interpretation
        if institutional_constraint_score > 70:
            interpretation = 'Very high institutional barriers - institutions systematically avoid this segment'
        elif institutional_constraint_score > 50:
            interpretation = 'High institutional barriers - creates opportunity for medium landlords'
        elif institutional_constraint_score > 30:
            interpretation = 'Moderate institutional barriers - some institutional interest'
        else:
            interpretation = 'Low institutional barriers - competitive institutional market'

        return {
            'deal_size_barrier': deal_size_barrier,
            'stigma_barrier': stigma_barrier,
            'management_intensity': management_intensity,
            'liquidity_concern': liquidity_concern,
            'institutional_constraint_score': round(institutional_constraint_score, 1),
            'interpretation': interpretation,
            'components': {
                'deal_size_score': deal_size_score,
                'stigma_score': stigma_score,
                'management_score': management_score,
                'liquidity_score': liquidity_concern_score,
                'esg_score': esg_score
            }
        }

    @staticmethod
    def assess_medium_landlord_constraints(
        rent_decile: int,
        num_units: int = 1,
        property_value: float = 0,
        geographic_concentration: Optional[float] = None
    ) -> Dict:
        """
        Assess medium landlord (10-50 units) operational feasibility

        Low constraints = sweet spot = arbitrage opportunity

        Medium landlords excel in D1-D4 because:
        1. Can achieve economies of scale (10+ units)
        2. Not constrained by deal size minimums
        3. Local market knowledge advantage
        4. Hands-on management capability

        Args:
            rent_decile: Property's rent tier
            num_units: Number of units in property
            property_value: Total property value
            geographic_concentration: % of portfolio in single market

        Returns:
            {
                'economies_of_scale': True,
                'optimal_size_range': True,
                'management_capability': 'High',
                'local_knowledge_advantage': True,
                'medium_landlord_constraint_score': 15.0,  # 0-100, lower = better fit
                'interpretation': 'Excellent fit for medium landlords'
            }
        """

        # Factor 1: Economies of Scale
        # 10-50 units = optimal range
        # Single-family = too small
        # 100+ units = too large for medium landlord

        economies_of_scale = num_units >= 10

        if num_units >= 10 and num_units <= 50:
            scale_score = 0.0  # Perfect fit
            optimal_size_range = True
        elif num_units >= 5 and num_units < 10:
            scale_score = 10.0  # Can work
            optimal_size_range = False
        elif num_units > 50 and num_units <= 100:
            scale_score = 15.0  # Getting large
            optimal_size_range = False
        else:
            scale_score = 25.0  # Too small or too large
            optimal_size_range = False

        # Factor 2: Management Capability Match
        # Medium landlords excel at hands-on management
        # D1-D4 require more intensive management (good match)
        # D8-D10 can be passive (no advantage)

        if rent_decile <= 4:
            management_capability = 'High'
            management_match_score = 0.0  # Advantage
        elif rent_decile <= 7:
            management_capability = 'Moderate'
            management_match_score = 10.0  # Neutral
        else:
            management_capability = 'Low'
            management_match_score = 20.0  # Disadvantage vs institutions

        # Factor 3: Local Knowledge Advantage
        # Medium landlords have local market knowledge
        # More valuable in less efficient markets (D1-D4)

        if rent_decile <= 3:
            local_knowledge_advantage = True
            knowledge_score = 0.0
        elif rent_decile <= 6:
            local_knowledge_advantage = True
            knowledge_score = 5.0
        else:
            local_knowledge_advantage = False
            knowledge_score = 15.0

        # Factor 4: Capital Efficiency
        # Deal size appropriate for medium landlord capital base
        # $500K - $5M = sweet spot

        if property_value == 0:
            capital_score = 10.0  # Unknown, moderate
        elif property_value >= 500_000 and property_value <= 5_000_000:
            capital_score = 0.0  # Perfect
        elif property_value < 500_000:
            capital_score = 5.0  # Small but manageable
        elif property_value <= 10_000_000:
            capital_score = 10.0  # Large but possible
        else:
            capital_score = 25.0  # Too large for typical medium landlord

        # Factor 5: Geographic Concentration Risk
        # Medium landlords can concentrate locally (advantage)

        if geographic_concentration is not None:
            if geographic_concentration > 80:
                concentration_score = 5.0  # High concentration OK for local expert
            else:
                concentration_score = 0.0  # Diversified
        else:
            concentration_score = 2.5  # Default moderate

        # Calculate composite constraint score (0-100)
        # LOWER score = BETTER fit for medium landlords
        medium_landlord_constraint_score = (
            scale_score +
            management_match_score +
            knowledge_score +
            capital_score +
            concentration_score
        )

        medium_landlord_constraint_score = min(medium_landlord_constraint_score, 100.0)

        # Interpretation (inverted - lower is better)
        if medium_landlord_constraint_score < 20:
            interpretation = 'Excellent fit for medium landlords - all factors align'
        elif medium_landlord_constraint_score < 40:
            interpretation = 'Good fit for medium landlords - most factors favorable'
        elif medium_landlord_constraint_score < 60:
            interpretation = 'Moderate fit for medium landlords - mixed factors'
        else:
            interpretation = 'Poor fit for medium landlords - better suited for others'

        return {
            'economies_of_scale': economies_of_scale,
            'optimal_size_range': optimal_size_range,
            'management_capability': management_capability,
            'local_knowledge_advantage': local_knowledge_advantage,
            'medium_landlord_constraint_score': round(medium_landlord_constraint_score, 1),
            'interpretation': interpretation,
            'components': {
                'scale_score': scale_score,
                'management_match_score': management_match_score,
                'knowledge_score': knowledge_score,
                'capital_score': capital_score,
                'concentration_score': concentration_score
            }
        }

    @staticmethod
    def calculate_arbitrage_opportunity(
        renter_constraints: Dict,
        institutional_constraints: Dict,
        medium_landlord_constraints: Dict,
        rent_decile: int
    ) -> Dict:
        """
        Calculate overall arbitrage opportunity score

        High arbitrage = High renter constraints + High institutional barriers + Low medium landlord constraints

        Key Finding: D1 properties have HIGHEST arbitrage opportunity (75-90)

        Args:
            renter_constraints: Output from assess_renter_constraints()
            institutional_constraints: Output from assess_institutional_constraints()
            medium_landlord_constraints: Output from assess_medium_landlord_constraints()
            rent_decile: Property's rent tier

        Returns:
            {
                'arbitrage_opportunity_score': 82.5,  # 0-100, higher = more opportunity
                'opportunity_level': 'Very High',
                'recommended_investor_type': 'Medium Landlord (10-50 units)',
                'key_advantages': [...],
                'interpretation': 'Significant mispricing due to market inefficiencies'
            }
        """

        # Extract component scores
        renter_score = renter_constraints['renter_constraint_score']
        institutional_score = institutional_constraints['institutional_constraint_score']
        medium_landlord_score = medium_landlord_constraints['medium_landlord_constraint_score']

        # Calculate arbitrage opportunity
        # High renter + institutional constraints = opportunity
        # Low medium landlord constraints = can capitalize
        # Formula: (Renter × 0.35 + Institutional × 0.35) + (100 - Medium_Landlord) × 0.30

        opportunity_from_barriers = (renter_score * 0.35) + (institutional_score * 0.35)
        opportunity_from_fit = (100 - medium_landlord_score) * 0.30

        arbitrage_opportunity_score = opportunity_from_barriers + opportunity_from_fit

        arbitrage_opportunity_score = min(arbitrage_opportunity_score, 100.0)

        # Determine opportunity level
        if arbitrage_opportunity_score > 75:
            opportunity_level = 'Very High'
        elif arbitrage_opportunity_score > 60:
            opportunity_level = 'High'
        elif arbitrage_opportunity_score > 40:
            opportunity_level = 'Moderate'
        else:
            opportunity_level = 'Low'

        # Recommend investor type
        if medium_landlord_score < 30 and institutional_score > 50:
            recommended_investor_type = 'Medium Landlord (10-50 units)'
        elif institutional_score < 40:
            recommended_investor_type = 'Institutional Investor'
        elif medium_landlord_score < 50:
            recommended_investor_type = 'Small-Medium Landlord (5-20 units)'
        else:
            recommended_investor_type = 'Individual Investor (1-4 units)'

        # Identify key advantages
        key_advantages = []

        if renter_score > 60:
            key_advantages.append("Stable tenant base (high renter constraints)")

        if institutional_score > 60:
            key_advantages.append("Limited institutional competition")

        if medium_landlord_score < 30:
            key_advantages.append("Optimal scale for medium landlords")

        if rent_decile <= 3:
            key_advantages.append("Research-validated return premium (D1-D3 outperform by 2-4%/year)")

        # Interpretation
        if arbitrage_opportunity_score > 75:
            interpretation = (
                f"Significant arbitrage opportunity in D{rent_decile}. "
                "Market inefficiencies create excess return potential for sophisticated operators."
            )
        elif arbitrage_opportunity_score > 60:
            interpretation = (
                f"Strong arbitrage opportunity in D{rent_decile}. "
                "Barriers to competition allow for above-market returns."
            )
        elif arbitrage_opportunity_score > 40:
            interpretation = (
                f"Moderate arbitrage opportunity in D{rent_decile}. "
                "Some competitive advantages but also challenges."
            )
        else:
            interpretation = (
                f"Limited arbitrage opportunity in D{rent_decile}. "
                "Efficient market with strong competition."
            )

        return {
            'arbitrage_opportunity_score': round(arbitrage_opportunity_score, 1),
            'opportunity_level': opportunity_level,
            'recommended_investor_type': recommended_investor_type,
            'key_advantages': key_advantages,
            'interpretation': interpretation,
            'components': {
                'renter_constraint_score': renter_score,
                'institutional_constraint_score': institutional_score,
                'medium_landlord_fit_score': round(100 - medium_landlord_score, 1),  # Inverted for display
                'opportunity_from_barriers': round(opportunity_from_barriers, 1),
                'opportunity_from_fit': round(opportunity_from_fit, 1)
            }
        }

    @staticmethod
    def calculate_for_deal(
        deal_id: int,
        rent_decile: int,
        monthly_rent: float,
        property_value: float,
        num_units: int = 1
    ) -> Dict:
        """
        Calculate complete arbitrage analysis for a deal

        Args:
            deal_id: Deal ID
            rent_decile: Property's rent tier
            monthly_rent: Monthly rent
            property_value: Total property value
            num_units: Number of units

        Returns:
            Complete arbitrage opportunity analysis
        """

        # Assess renter constraints
        renter = ArbitrageLimitsService.assess_renter_constraints(
            monthly_rent=monthly_rent,
            median_income=None,  # Will be estimated
            home_price_to_rent_ratio=None,  # Will use default
            rent_decile=rent_decile
        )

        # Assess institutional constraints
        institutional = ArbitrageLimitsService.assess_institutional_constraints(
            rent_decile=rent_decile,
            property_value=property_value,
            num_units=num_units,
            liquidity_score=None
        )

        # Assess medium landlord fit
        medium_landlord = ArbitrageLimitsService.assess_medium_landlord_constraints(
            rent_decile=rent_decile,
            num_units=num_units,
            property_value=property_value,
            geographic_concentration=None
        )

        # Calculate overall arbitrage opportunity
        arbitrage = ArbitrageLimitsService.calculate_arbitrage_opportunity(
            renter_constraints=renter,
            institutional_constraints=institutional,
            medium_landlord_constraints=medium_landlord,
            rent_decile=rent_decile
        )

        return {
            'deal_id': deal_id,
            'rent_decile': rent_decile,
            'renter_constraints': renter,
            'institutional_constraints': institutional,
            'medium_landlord_fit': medium_landlord,
            'arbitrage_opportunity': arbitrage,
            'summary': {
                'opportunity_score': arbitrage['arbitrage_opportunity_score'],
                'opportunity_level': arbitrage['opportunity_level'],
                'recommended_investor': arbitrage['recommended_investor_type'],
                'key_advantages': arbitrage['key_advantages']
            }
        }
