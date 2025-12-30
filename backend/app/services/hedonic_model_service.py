"""
Hedonic Model Service
Predicts fundamental rental values using property characteristics

Model: log(Rent) = Σ(β × Characteristics) + α_neighborhood + α_time + ε

Academic Research Basis:
- Low-rent properties deliver 2-4% higher annual returns
- Fundamental rent (predicted) is better than observed rent for classification
- Sorting on observed rent creates mechanical bias
"""

import json
import os
import math
from typing import Dict, Optional
from datetime import datetime


class HedonicModelService:
    """
    Service for predicting fundamental rental values using hedonic regression
    """

    # Cache for loaded coefficients
    _coefficients_cache = {}

    @staticmethod
    def load_coefficients(model_version: str = 'us_national_v1') -> Dict:
        """
        Load hedonic model coefficients from JSON file

        Args:
            model_version: Which model to load (us_national_v1, california_v1, etc.)

        Returns:
            Dictionary of model coefficients and metadata
        """
        if model_version in HedonicModelService._coefficients_cache:
            return HedonicModelService._coefficients_cache[model_version]

        # Load from JSON file
        data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data'
        )
        coefficients_path = os.path.join(data_dir, 'hedonic_coefficients.json')

        try:
            with open(coefficients_path, 'r') as f:
                all_coefficients = json.load(f)

            if model_version not in all_coefficients:
                raise ValueError(f"Model version '{model_version}' not found in coefficients file")

            model_data = all_coefficients[model_version]

            # Cache it
            HedonicModelService._coefficients_cache[model_version] = model_data

            return model_data

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Hedonic coefficients file not found at {coefficients_path}. "
                "Please run seed_benchmark_data.py first."
            )
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in coefficients file: {coefficients_path}")

    @staticmethod
    def predict_fundamental_rent(property_data: Dict, model_version: str = 'us_national_v1') -> Dict:
        """
        Predict fundamental rental value using hedonic model

        Args:
            property_data: Dictionary with property characteristics:
                - square_footage (int): Property size in sqft
                - bedrooms (int): Number of bedrooms
                - bathrooms (float): Number of bathrooms
                - year_built (int): Construction year
                - property_type (str): 'single_family', 'multifamily', 'condo', etc.
                - epc_score (str, optional): Energy performance (A-F)
                - zipcode (str, optional): For neighborhood effects
            model_version: Which model to use

        Returns:
            Dictionary with:
                - predicted_rent: Monthly rent in USD
                - log_rent: Log-transformed prediction
                - confidence: Prediction confidence (based on R²)
                - model_version: Which model was used
                - components: Breakdown of contribution from each variable
        """

        # Load model coefficients
        model = HedonicModelService.load_coefficients(model_version)
        coefficients = model['coefficients']

        # Validate required fields
        required_fields = ['square_footage', 'bedrooms', 'bathrooms']
        missing_fields = [f for f in required_fields if f not in property_data or property_data[f] is None]

        if missing_fields:
            raise ValueError(f"Missing required fields for hedonic prediction: {missing_fields}")

        # Calculate age (current year - year_built)
        current_year = datetime.now().year
        year_built = property_data.get('year_built') or property_data.get('construction_year')
        age = current_year - year_built if year_built else 30  # Default 30 years if unknown

        # Extract features
        sqft = property_data.get('square_footage', 1000)
        bedrooms = property_data.get('bedrooms', 2)
        bathrooms = property_data.get('bathrooms', 1)
        property_type = property_data.get('property_type', '').lower()
        epc_score = property_data.get('epc_score', 'D')  # Default to D if unknown

        # Start with intercept
        log_rent = coefficients['intercept']
        components = {'intercept': coefficients['intercept']}

        # Square footage (linear, not log in this model)
        sqft_contribution = coefficients['log_sqft'] * sqft
        log_rent += sqft_contribution
        components['square_footage'] = sqft_contribution

        # Bedrooms
        bedrooms_contribution = coefficients['bedrooms'] * bedrooms
        log_rent += bedrooms_contribution
        components['bedrooms'] = bedrooms_contribution

        # Bathrooms
        bathrooms_contribution = coefficients['bathrooms'] * bathrooms
        log_rent += bathrooms_contribution
        components['bathrooms'] = bathrooms_contribution

        # Age (linear and quadratic)
        age_contribution = coefficients['age'] * age
        log_rent += age_contribution
        components['age'] = age_contribution

        if 'age_squared' in coefficients:
            age_sq_contribution = coefficients['age_squared'] * (age ** 2)
            log_rent += age_sq_contribution
            components['age_squared'] = age_sq_contribution

        # Property type (relative to single-family baseline)
        property_type_contribution = 0.0
        if 'multifamily' in property_type or 'apartment' in property_type:
            property_type_contribution = coefficients.get('property_type_multifamily', 0.0)
        elif 'condo' in property_type:
            property_type_contribution = coefficients.get('property_type_condo', 0.0)

        log_rent += property_type_contribution
        components['property_type'] = property_type_contribution

        # EPC Score (energy efficiency) - relative to D baseline
        epc_contribution = 0.0
        epc_key = f'epc_score_{epc_score.lower()}' if epc_score else 'epc_score_d'
        if epc_key in coefficients:
            epc_contribution = coefficients[epc_key]
            log_rent += epc_contribution
            components['epc_score'] = epc_contribution

        # Neighborhood effects (future enhancement)
        # zipcode = property_data.get('zipcode')
        # if zipcode and 'neighborhood_effects' in model:
        #     neighborhood_effect = model['neighborhood_effects'].get(zipcode, 0.0)
        #     log_rent += neighborhood_effect
        #     components['neighborhood'] = neighborhood_effect

        # Convert from log space to actual rent
        predicted_rent = math.exp(log_rent)

        # Calculate confidence based on R²
        r_squared = model.get('model_performance', {}).get('r_squared', 0.65)
        confidence = r_squared * 100  # Convert to percentage

        return {
            'predicted_rent': round(predicted_rent, 2),
            'log_rent': round(log_rent, 4),
            'confidence': round(confidence, 1),
            'model_version': model_version,
            'components': components,
            'property_characteristics': {
                'square_footage': sqft,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'age': age,
                'property_type': property_type,
                'epc_score': epc_score
            }
        }

    @staticmethod
    def validate_prediction(predicted_rent: float, observed_rent: Optional[float] = None) -> Dict:
        """
        Validate prediction quality and flag outliers

        Args:
            predicted_rent: Rent predicted by hedonic model
            observed_rent: Actual observed rent (if available)

        Returns:
            Dictionary with validation results:
                - is_valid: Boolean
                - deviation_pct: Percentage deviation from observed (if available)
                - warning: Warning message if prediction seems off
        """
        warnings = []

        # Check if prediction is reasonable (not too low or too high)
        if predicted_rent < 300:
            warnings.append("Predicted rent unusually low (<$300/month). Check property characteristics.")
        elif predicted_rent > 10000:
            warnings.append("Predicted rent unusually high (>$10,000/month). May be luxury property.")

        # Compare to observed rent if available
        deviation_pct = None
        if observed_rent and observed_rent > 0:
            deviation_pct = ((predicted_rent - observed_rent) / observed_rent) * 100

            # Flag large deviations
            if abs(deviation_pct) > 50:
                warnings.append(
                    f"Large deviation from observed rent ({deviation_pct:+.1f}%). "
                    "Property may have unique characteristics not captured by model."
                )
            elif abs(deviation_pct) > 30:
                warnings.append(
                    f"Moderate deviation from observed rent ({deviation_pct:+.1f}%). "
                    "Consider using observed rent with caution."
                )

        return {
            'is_valid': len(warnings) == 0,
            'deviation_pct': round(deviation_pct, 1) if deviation_pct is not None else None,
            'warnings': warnings
        }

    @staticmethod
    def get_available_models() -> list:
        """
        Get list of available hedonic models

        Returns:
            List of model version names
        """
        data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data'
        )
        coefficients_path = os.path.join(data_dir, 'hedonic_coefficients.json')

        try:
            with open(coefficients_path, 'r') as f:
                all_coefficients = json.load(f)
            return list(all_coefficients.keys())
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def select_model_for_location(state: Optional[str] = None, region: Optional[str] = None) -> str:
        """
        Select appropriate hedonic model based on property location

        Args:
            state: Two-letter state code (e.g., 'CA', 'TX')
            region: Region name (e.g., 'West Coast', 'South')

        Returns:
            Model version string to use

        Note:
            For Phase 1, always returns 'us_national_v1'
            Regional models will be added in Phase 8
        """
        # Future enhancement: Use state-specific models
        # if state == 'CA':
        #     return 'california_v1'
        # elif state == 'TX':
        #     return 'texas_v1'

        # For now, always use national model
        return 'us_national_v1'
