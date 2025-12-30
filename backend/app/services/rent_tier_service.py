"""
Rent Tier Classification Service
Classifies properties into rent deciles (D1-D10) based on fundamental rental value

Academic Research Basis:
- D1 (lowest 10%): Delivers 4.53-11.19% total returns (US)
- D10 (highest 10%): Delivers 2.56-7.04% total returns (US)
- D1-D10 spread: 1.97-4.15 percentage points
- Classification should use PREDICTED rent, not observed rent (eliminates bias)
"""

from typing import Dict, Optional
from app.database import db, MarketDecileThresholds
from datetime import datetime


class RentTierService:
    """
    Service for classifying properties into rent deciles
    """

    @staticmethod
    def classify_property(
        predicted_rent: float,
        geography: str = 'national',
        bedrooms: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict:
        """
        Classify property into rent decile based on predicted fundamental rent

        Args:
            predicted_rent: Monthly rent predicted by hedonic model
            geography: Geographic market ('national', state code, or zipcode)
            bedrooms: Number of bedrooms (thresholds can vary by unit size)
            year: Data year (defaults to current year)

        Returns:
            Dictionary with:
                - national_decile: 1-10 (national classification)
                - regional_decile: 1-10 (regional classification if available)
                - tier_label: 'D1', 'D2', ..., 'D10'
                - percentile: Exact percentile (0-100)
                - rent_value: The predicted rent used for classification
                - geography: Geographic area used
                - comparison_to_median: Percentage above/below median
        """

        if year is None:
            year = datetime.now().year

        # Get national classification
        national_decile, national_percentile = RentTierService._classify_in_geography(
            predicted_rent,
            'national',
            bedrooms,
            year
        )

        # Get regional classification if specific geography provided
        regional_decile = None
        regional_percentile = None

        if geography != 'national':
            try:
                regional_decile, regional_percentile = RentTierService._classify_in_geography(
                    predicted_rent,
                    geography,
                    bedrooms,
                    year
                )
            except ValueError:
                # Regional thresholds not available, fall back to national
                regional_decile = national_decile
                regional_percentile = national_percentile

        # Use regional if available, otherwise use national
        primary_decile = regional_decile if regional_decile else national_decile
        primary_percentile = regional_percentile if regional_percentile else national_percentile

        # Calculate comparison to median (D5 threshold)
        median_threshold = RentTierService._get_decile_threshold(
            geography if regional_decile else 'national',
            5,
            bedrooms,
            year
        )

        comparison_to_median = 0.0
        if median_threshold and median_threshold > 0:
            comparison_to_median = ((predicted_rent - median_threshold) / median_threshold) * 100

        return {
            'national_decile': national_decile,
            'regional_decile': regional_decile or national_decile,
            'tier_label': f'D{primary_decile}',
            'percentile': round(primary_percentile, 1),
            'rent_value': predicted_rent,
            'geography': geography,
            'comparison_to_median': round(comparison_to_median, 1),
            'interpretation': RentTierService._get_tier_interpretation(primary_decile)
        }

    @staticmethod
    def _classify_in_geography(
        predicted_rent: float,
        geography: str,
        bedrooms: Optional[int],
        year: int
    ) -> tuple:
        """
        Internal method to classify in a specific geography

        Returns:
            Tuple of (decile, percentile)
        """

        # Get thresholds for this geography
        thresholds = RentTierService.get_decile_thresholds(geography, bedrooms, year)

        if not thresholds:
            # No thresholds available, use hardcoded national estimates
            thresholds = RentTierService._get_default_national_thresholds(bedrooms)

        # Classify into decile based on thresholds
        decile = 10  # Start with highest decile
        percentile = 95.0  # Approximate percentile

        for i in range(1, 11):
            threshold = thresholds.get(f'd{i}_threshold')
            if threshold and predicted_rent <= threshold:
                decile = i
                # Approximate percentile (midpoint of decile)
                percentile = (i - 1) * 10 + 5
                break

        return decile, percentile

    @staticmethod
    def get_decile_thresholds(
        geography: str = 'national',
        bedrooms: Optional[int] = None,
        year: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Retrieve rent decile thresholds for a market

        Args:
            geography: Geographic market identifier
            bedrooms: Number of bedrooms (optional filter)
            year: Data year (defaults to most recent)

        Returns:
            Dictionary with d1_threshold through d10_threshold, or None if not found
        """

        query = MarketDecileThresholds.query.filter_by(geography=geography)

        if bedrooms is not None:
            query = query.filter_by(bedrooms=bedrooms)

        if year is not None:
            query = query.filter_by(data_year=year)

        # Get most recent entry if multiple exist
        threshold_record = query.order_by(MarketDecileThresholds.data_year.desc()).first()

        if not threshold_record:
            return None

        return {
            'd1_threshold': threshold_record.d1_threshold,
            'd2_threshold': threshold_record.d2_threshold,
            'd3_threshold': threshold_record.d3_threshold,
            'd4_threshold': threshold_record.d4_threshold,
            'd5_threshold': threshold_record.d5_threshold,
            'd6_threshold': threshold_record.d6_threshold,
            'd7_threshold': threshold_record.d7_threshold,
            'd8_threshold': threshold_record.d8_threshold,
            'd9_threshold': threshold_record.d9_threshold,
            'd10_threshold': threshold_record.d10_threshold
        }

    @staticmethod
    def _get_decile_threshold(
        geography: str,
        decile: int,
        bedrooms: Optional[int],
        year: int
    ) -> Optional[float]:
        """
        Get threshold for a specific decile

        Args:
            geography: Geographic market
            decile: Which decile (1-10)
            bedrooms: Number of bedrooms
            year: Data year

        Returns:
            Threshold rent value, or None if not found
        """
        thresholds = RentTierService.get_decile_thresholds(geography, bedrooms, year)
        if not thresholds:
            return None

        return thresholds.get(f'd{decile}_threshold')

    @staticmethod
    def _get_default_national_thresholds(bedrooms: Optional[int] = None) -> Dict:
        """
        Get hardcoded default thresholds for national market
        Used when database thresholds are not available

        These are rough estimates based on US median rents
        Should be replaced with actual RentCast data via update_market_thresholds script

        Args:
            bedrooms: Number of bedrooms (affects threshold levels)

        Returns:
            Dictionary with d1_threshold through d10_threshold
        """

        # Base thresholds for 2BR units (approximate US market 2024)
        if bedrooms == 0 or bedrooms == 1:
            base_multiplier = 0.7  # Studios/1BR rent less
        elif bedrooms == 3:
            base_multiplier = 1.3  # 3BR rent more
        elif bedrooms and bedrooms >= 4:
            base_multiplier = 1.6  # 4+ BR rent much more
        else:
            base_multiplier = 1.0  # 2BR baseline

        # Approximate decile thresholds (monthly rent in USD)
        base_thresholds = {
            'd1_threshold': 600,    # Bottom 10%
            'd2_threshold': 800,
            'd3_threshold': 1000,
            'd4_threshold': 1200,
            'd5_threshold': 1400,   # Median
            'd6_threshold': 1700,
            'd7_threshold': 2000,
            'd8_threshold': 2400,
            'd9_threshold': 3000,
            'd10_threshold': 4500   # Top 10%
        }

        # Adjust for bedrooms
        return {
            key: round(value * base_multiplier, 2)
            for key, value in base_thresholds.items()
        }

    @staticmethod
    def _get_tier_interpretation(decile: int) -> Dict:
        """
        Get interpretation of what a decile classification means

        Args:
            decile: Decile classification (1-10)

        Returns:
            Dictionary with interpretation, expected returns, and risk profile
        """

        interpretations = {
            1: {
                'category': 'Very Low Rent (Bottom 10%)',
                'expected_return_range': '4.53-11.19% total return (US)',
                'risk_profile': 'Lower systematic risk than higher deciles',
                'arbitrage_opportunity': 'High - institutions typically avoid',
                'tenant_profile': 'Low income, may have debt indicators but similar payment rates',
                'color_code': '#22c55e'  # Green
            },
            2: {
                'category': 'Low Rent (10th-20th percentile)',
                'expected_return_range': '4.35-11.03% total return (US)',
                'risk_profile': 'Lower systematic risk',
                'arbitrage_opportunity': 'High',
                'tenant_profile': 'Low income',
                'color_code': '#22c55e'  # Green
            },
            3: {
                'category': 'Below Median Rent (20th-30th percentile)',
                'expected_return_range': '3.94-10.41% total return (US)',
                'risk_profile': 'Lower systematic risk',
                'arbitrage_opportunity': 'Moderate to High',
                'tenant_profile': 'Below median income',
                'color_code': '#84cc16'  # Light green
            },
            4: {
                'category': 'Below Median Rent (30th-40th percentile)',
                'expected_return_range': '3.70-9.79% total return (US)',
                'risk_profile': 'Moderate risk',
                'arbitrage_opportunity': 'Moderate',
                'tenant_profile': 'Below median income',
                'color_code': '#eab308'  # Yellow
            },
            5: {
                'category': 'Median Rent (40th-50th percentile)',
                'expected_return_range': '3.42-9.32% total return (US)',
                'risk_profile': 'Moderate risk',
                'arbitrage_opportunity': 'Moderate',
                'tenant_profile': 'Median income',
                'color_code': '#eab308'  # Yellow
            },
            6: {
                'category': 'Above Median Rent (50th-60th percentile)',
                'expected_return_range': '3.21-8.60% total return (US)',
                'risk_profile': 'Moderate risk',
                'arbitrage_opportunity': 'Low to Moderate',
                'tenant_profile': 'Above median income',
                'color_code': '#f59e0b'  # Orange
            },
            7: {
                'category': 'Above Median Rent (60th-70th percentile)',
                'expected_return_range': '3.19-8.22% total return (US)',
                'risk_profile': 'Moderate to higher risk',
                'arbitrage_opportunity': 'Low',
                'tenant_profile': 'Above median income',
                'color_code': '#f59e0b'  # Orange
            },
            8: {
                'category': 'High Rent (70th-80th percentile)',
                'expected_return_range': '3.01-7.76% total return (US)',
                'risk_profile': 'Higher systematic risk',
                'arbitrage_opportunity': 'Low',
                'tenant_profile': 'Higher income',
                'color_code': '#ef4444'  # Red
            },
            9: {
                'category': 'High Rent (80th-90th percentile)',
                'expected_return_range': '2.84-7.24% total return (US)',
                'risk_profile': 'Higher systematic risk',
                'arbitrage_opportunity': 'Very Low',
                'tenant_profile': 'Higher income',
                'color_code': '#ef4444'  # Red
            },
            10: {
                'category': 'Very High Rent (Top 10%)',
                'expected_return_range': '2.56-7.04% total return (US)',
                'risk_profile': 'Highest systematic risk, lowest returns',
                'arbitrage_opportunity': 'None - institutional competition',
                'tenant_profile': 'High income',
                'color_code': '#dc2626'  # Dark red
            }
        }

        return interpretations.get(decile, {
            'category': 'Unknown',
            'expected_return_range': 'N/A',
            'risk_profile': 'Unknown',
            'arbitrage_opportunity': 'Unknown',
            'tenant_profile': 'Unknown',
            'color_code': '#gray'
        })

    @staticmethod
    def update_market_thresholds(
        geography: str,
        bedrooms: int,
        thresholds: Dict,
        data_year: Optional[int] = None
    ) -> bool:
        """
        Update or create market decile thresholds

        Args:
            geography: Geographic market identifier
            bedrooms: Number of bedrooms
            thresholds: Dictionary with d1_threshold through d10_threshold
            data_year: Year of the data (defaults to current year)

        Returns:
            True if successful
        """

        if data_year is None:
            data_year = datetime.now().year

        # Check if record exists
        existing = MarketDecileThresholds.query.filter_by(
            geography=geography,
            bedrooms=bedrooms,
            data_year=data_year
        ).first()

        if existing:
            # Update existing
            for key, value in thresholds.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            existing.last_updated = datetime.utcnow()
        else:
            # Create new
            new_threshold = MarketDecileThresholds(
                geography=geography,
                bedrooms=bedrooms,
                data_year=data_year,
                **thresholds
            )
            db.session.add(new_threshold)

        db.session.commit()
        return True
