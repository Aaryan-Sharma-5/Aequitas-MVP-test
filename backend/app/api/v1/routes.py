from flask import Blueprint, jsonify, request, current_app
import os
import json

from pathlib import Path
from app.services.census_service import CensusService

api_v1 = Blueprint('api_v1', __name__)

# Initialize Census service (will be created on first request)
_census_service = None


def get_census_service():
    """Get or create Census service instance."""
    global _census_service
    if _census_service is None:
        _census_service = CensusService(
            api_key=current_app.config.get('CENSUS_API_KEY', ''),
            base_url=current_app.config.get('CENSUS_API_BASE_URL', 'https://api.census.gov/data'),
            api_year=current_app.config.get('CENSUS_API_YEAR', '2022'),
            cache_ttl=current_app.config.get('CENSUS_CACHE_TTL', 86400)
        )
    return _census_service

@api_v1.route('/ping', methods=['GET'])
def ping():
    return jsonify({'pong': True})

@api_v1.route('/echo', methods=['POST'])
def echo():
    payload = request.get_json(silent=True) or {}
    return jsonify({'received': payload}), 201

@api_v1.route('/status', methods=['GET'])
def status():
    return jsonify({'service': 'PE-Aequitas API', 'version': 'v1'})


@api_v1.route('/metrics', methods=['GET'])
def metrics():
    """Return simple metrics for the frontend dashboard.

    Reads values from `Web_scraping/available_properties.json` and 
    `Web_scraping/potential_properties.json`. Otherwise returns reasonable defaults.
    """
    repo_root = Path(__file__).resolve().parents[4]
    available_path = repo_root / 'Web_scraping' / 'available_properties.json'
    potential_path = repo_root / 'Web_scraping' / 'potential_properties.json'

    defaults = {
        'total_affordable_units': 12847,
        'families_housed': 28903,
        'market_insights': {
            'avg_ami_served': 58.5,
            'total_markets': 4,
            'avg_market_income': 75000,
            'avg_occupancy_rate': 94.2,
            'avg_median_rent': 1450
        }
    }

    try:
        total_units = defaults['total_affordable_units']
        families = defaults['families_housed']
        market_insights = defaults['market_insights'].copy()

        # Try to read available_properties for unit count
        if available_path.exists():
            with open(available_path, 'r', encoding='utf-8') as f:
                available_data = json.load(f)
                props = available_data.get('properties', [])
                # If there's a totalUnits in the first property or metadata, use it
                if props and 'totalUnits' in props[0]:
                    try:
                        total_units = int(props[0]['totalUnits'])
                    except Exception:
                        pass

        # Try to read potential_properties for additional context if needed
        if potential_path.exists():
            with open(potential_path, 'r', encoding='utf-8') as f:
                potential_data = json.load(f)
                # Optionally derive additional metrics from potential_data

        return jsonify({
            'total_affordable_units': total_units,
            'families_housed': families,
            'market_insights': market_insights
        })
    except Exception:
            return jsonify(defaults)

    return jsonify(defaults)


@api_v1.route('/demographics/<zipcode>', methods=['GET'])
def get_demographics(zipcode):
    """
    Get comprehensive demographic data for a ZIP code.

    Args:
        zipcode: 5-digit ZIP code

    Returns:
        JSON response with demographic data or error
    """
    try:
        census_service = get_census_service()
        demographic_data = census_service.get_demographics_by_zipcode(zipcode)

        if demographic_data is None:
            return jsonify({
                'success': False,
                'error': f'No demographic data available for ZIP code {zipcode}',
                'code': 'NO_DATA'
            }), 404

        return jsonify({
            'success': True,
            'data': demographic_data.to_dict(),
            'cached': False  # Could be enhanced to track cache hits
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'INVALID_INPUT'
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'code': 'SERVER_ERROR'
        }), 500


@api_v1.route('/demographics/batch', methods=['POST'])
def get_demographics_batch():
    """
    Get demographics for multiple ZIP codes in one request.

    Request body:
        {
            "zipcodes": ["95814", "95819", ...]
        }

    Returns:
        JSON response with demographic data for all ZIP codes
    """
    try:
        data = request.get_json()
        if not data or 'zipcodes' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing "zipcodes" in request body',
                'code': 'INVALID_INPUT'
            }), 400

        zipcodes = data['zipcodes']

        if not isinstance(zipcodes, list):
            return jsonify({
                'success': False,
                'error': '"zipcodes" must be an array',
                'code': 'INVALID_INPUT'
            }), 400

        if len(zipcodes) > 50:
            return jsonify({
                'success': False,
                'error': 'Maximum 50 ZIP codes per request',
                'code': 'TOO_MANY_REQUESTS'
            }), 400

        census_service = get_census_service()
        results = {}
        errors = {}

        for zipcode in zipcodes:
            try:
                demographic_data = census_service.get_demographics_by_zipcode(str(zipcode))
                if demographic_data:
                    results[zipcode] = demographic_data.to_dict()
                else:
                    errors[zipcode] = 'No data available'
            except Exception as e:
                errors[zipcode] = str(e)

        return jsonify({
            'success': True,
            'data': results,
            'errors': errors if errors else None
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'code': 'SERVER_ERROR'
        }), 500


@api_v1.route('/ami-calculator', methods=['POST'])
def calculate_ami():
    """
    Calculate AMI-based rent limits for a property.

    Request body:
        {
            "zipcode": "95814",
            "ami_percent": 60,
            "bedrooms": 2
        }

    Returns:
        JSON response with AMI calculations
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Missing request body',
                'code': 'INVALID_INPUT'
            }), 400

        zipcode = data.get('zipcode')
        ami_percent = data.get('ami_percent', 60)
        bedrooms = data.get('bedrooms', 2)

        if not zipcode:
            return jsonify({
                'success': False,
                'error': 'Missing required field: zipcode',
                'code': 'INVALID_INPUT'
            }), 400

        if ami_percent not in [30, 50, 60, 80]:
            return jsonify({
                'success': False,
                'error': 'ami_percent must be 30, 50, 60, or 80',
                'code': 'INVALID_INPUT'
            }), 400

        census_service = get_census_service()
        result = census_service.calculate_ami_rent_limit(
            zipcode=str(zipcode),
            ami_percent=ami_percent,
            bedrooms=bedrooms
        )

        if result is None:
            return jsonify({
                'success': False,
                'error': f'Unable to calculate AMI for ZIP code {zipcode}',
                'code': 'NO_DATA'
            }), 404

        return jsonify({
            'success': True,
            'data': result
        })

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'INVALID_INPUT'
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'code': 'SERVER_ERROR'
        }), 500
