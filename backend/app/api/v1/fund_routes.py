"""
Fund management API routes
Provides REST endpoints for fund data operations
"""
from flask import Blueprint, request, jsonify
from app.services.fund_service import FundService

fund_routes = Blueprint('fund_routes', __name__)


@fund_routes.route('/funds/<int:fund_id>', methods=['GET'])
def get_fund(fund_id):
    """
    Get a single fund by ID

    Args:
        fund_id: ID of the fund

    Returns:
        JSON response with fund data
    """
    try:
        fund = FundService.get_fund(fund_id)

        if not fund:
            return jsonify({
                'error': 'Fund not found'
            }), 404

        return jsonify({
            'fund': fund.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@fund_routes.route('/funds/<int:fund_id>/overview', methods=['GET'])
def get_fund_overview(fund_id):
    """
    Get complete fund overview with all related data
    This is the primary endpoint used by the frontend

    Args:
        fund_id: ID of the fund

    Returns:
        JSON response with complete fund data including:
        - fund: Basic fund information
        - metrics: Latest performance metrics
        - quarterlyPerformance: IRR performance by quarter
        - strategies: Investment strategy breakdown
        - cashFlows: Quarterly cash flows
        - cashFlowSummary: Summary calculations
        - benchmarks: Performance vs industry benchmarks
        - recentActivities: Recent fund activities
    """
    try:
        overview = FundService.get_fund_overview(fund_id)

        if not overview:
            return jsonify({
                'error': 'Fund not found'
            }), 404

        return jsonify(overview), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@fund_routes.route('/funds/<int:fund_id>/metrics', methods=['GET'])
def get_fund_metrics(fund_id):
    """
    Get latest fund metrics

    Args:
        fund_id: ID of the fund

    Returns:
        JSON response with fund metrics
    """
    try:
        metrics = FundService.get_fund_metrics(fund_id)

        if not metrics:
            return jsonify({
                'error': 'Metrics not found'
            }), 404

        return jsonify({
            'metrics': metrics.to_dict()
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@fund_routes.route('/funds/<int:fund_id>/quarterly-performance', methods=['GET'])
def get_quarterly_performance(fund_id):
    """
    Get quarterly IRR performance

    Args:
        fund_id: ID of the fund

    Query Parameters:
        limit: Maximum number of quarters to return (default 8)

    Returns:
        JSON response with quarterly performance data
    """
    try:
        limit = request.args.get('limit', 8, type=int)
        performance = FundService.get_quarterly_performance(fund_id, limit=limit)

        return jsonify({
            'performance': [p.to_dict() for p in performance]
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@fund_routes.route('/funds/<int:fund_id>/strategies', methods=['GET'])
def get_investment_strategies(fund_id):
    """
    Get investment strategies

    Args:
        fund_id: ID of the fund

    Returns:
        JSON response with investment strategies
    """
    try:
        strategies = FundService.get_investment_strategies(fund_id)

        return jsonify({
            'strategies': [s.to_dict() for s in strategies]
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@fund_routes.route('/funds/<int:fund_id>/cash-flows', methods=['GET'])
def get_cash_flows(fund_id):
    """
    Get quarterly cash flows with summary

    Args:
        fund_id: ID of the fund

    Query Parameters:
        limit: Maximum number of quarters to return (default 8)

    Returns:
        JSON response with cash flows and summary
    """
    try:
        limit = request.args.get('limit', 8, type=int)
        cash_flow_data = FundService.get_cash_flows(fund_id, limit=limit)

        return jsonify(cash_flow_data), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@fund_routes.route('/funds/<int:fund_id>/activities', methods=['GET'])
def get_fund_activities(fund_id):
    """
    Get recent fund activities

    Args:
        fund_id: ID of the fund

    Query Parameters:
        limit: Maximum number of activities to return (default 10)
        status: Optional status filter ('Completed', 'In Progress', 'Scheduled')

    Returns:
        JSON response with fund activities
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        status = request.args.get('status')

        activities = FundService.get_fund_activities(fund_id, limit=limit, status=status)

        return jsonify({
            'activities': [a.to_dict() for a in activities]
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@fund_routes.route('/funds/<int:fund_id>/benchmarks', methods=['GET'])
def get_benchmark_comparisons(fund_id):
    """
    Get benchmark comparisons

    Args:
        fund_id: ID of the fund

    Returns:
        JSON response with benchmark data
    """
    try:
        benchmarks = FundService.get_benchmark_comparisons(fund_id)

        return jsonify({
            'benchmarks': [b.to_dict() for b in benchmarks]
        }), 200

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@fund_routes.route('/funds', methods=['POST'])
def create_fund():
    """
    Create a new fund (for future use)

    Request Body:
        JSON object with fund data (fundName and fundSize are required)

    Returns:
        JSON response with created fund
    """
    try:
        fund_data = request.get_json()

        if not fund_data:
            return jsonify({
                'error': 'Request body must be JSON'
            }), 400

        fund = FundService.create_fund(fund_data)

        return jsonify({
            'fund': fund.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({
            'error': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
