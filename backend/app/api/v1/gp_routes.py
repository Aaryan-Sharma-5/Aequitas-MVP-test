"""
GP (General Partner) management API routes
Provides REST endpoints for GP portfolio data operations
"""
from flask import Blueprint, request, jsonify
from app.services.gp_service import GPService

gp_routes = Blueprint('gp_routes', __name__)


@gp_routes.route('/gps', methods=['GET'])
def get_all_gps():
    """
    Get all GPs

    Returns:
        JSON response with list of all GPs
    """
    try:
        gps = GPService.get_all_gps()
        return jsonify({
            'gps': gps
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@gp_routes.route('/gps/<int:gp_id>', methods=['GET'])
def get_gp(gp_id):
    """
    Get a single GP by ID

    Args:
        gp_id: ID of the GP

    Returns:
        JSON response with GP data
    """
    try:
        gp = GPService.get_gp(gp_id)

        if not gp:
            return jsonify({
                'error': 'GP not found'
            }), 404

        return jsonify({
            'gp': gp
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@gp_routes.route('/gps/<int:gp_id>/overview', methods=['GET'])
def get_gp_overview(gp_id):
    """
    Get complete GP overview with all related data
    This is the primary endpoint used by the frontend

    Args:
        gp_id: ID of the GP

    Returns:
        JSON response with complete GP data including:
        - gp: Basic GP information
        - quarterlyPerformance: IRR performance by quarter
        - portfolioSummary: Performance distribution by quartile
    """
    try:
        overview = GPService.get_gp_overview(gp_id)

        if not overview:
            return jsonify({
                'error': 'GP not found'
            }), 404

        return jsonify(overview), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@gp_routes.route('/gps/performance-comparison', methods=['GET'])
def get_performance_comparison():
    """
    Get performance comparison data for all GPs
    Used for the performance comparison chart

    Returns:
        JSON response with GP performance comparison data
    """
    try:
        comparison = GPService.get_gp_performance_comparison()
        return jsonify({
            'comparison': comparison
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@gp_routes.route('/gps/top-performers', methods=['GET'])
def get_top_performers():
    """
    Get top performing GPs and those needing attention

    Returns:
        JSON response with top performers and attention items
    """
    try:
        performers = GPService.get_top_performers()
        return jsonify(performers), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@gp_routes.route('/gps', methods=['POST'])
def create_gp():
    """
    Create a new GP

    Request Body:
        JSON object with GP data

    Returns:
        JSON response with created GP data
    """
    try:
        gp_data = request.get_json()

        if not gp_data or 'gpName' not in gp_data:
            return jsonify({
                'error': 'GP name is required'
            }), 400

        gp = GPService.create_gp(gp_data)
        return jsonify({
            'gp': gp
        }), 201

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@gp_routes.route('/gps/<int:gp_id>', methods=['PUT'])
def update_gp(gp_id):
    """
    Update an existing GP

    Args:
        gp_id: ID of the GP to update

    Request Body:
        JSON object with updated GP data

    Returns:
        JSON response with updated GP data
    """
    try:
        gp_data = request.get_json()

        if not gp_data:
            return jsonify({
                'error': 'No data provided'
            }), 400

        gp = GPService.update_gp(gp_id, gp_data)

        if not gp:
            return jsonify({
                'error': 'GP not found'
            }), 404

        return jsonify({
            'gp': gp
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@gp_routes.route('/gps/<int:gp_id>', methods=['DELETE'])
def delete_gp(gp_id):
    """
    Delete a GP

    Args:
        gp_id: ID of the GP to delete

    Returns:
        JSON response with success message
    """
    try:
        success = GPService.delete_gp(gp_id)

        if not success:
            return jsonify({
                'error': 'GP not found'
            }), 404

        return jsonify({
            'message': 'GP deleted successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
