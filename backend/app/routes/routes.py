from flask import Blueprint, jsonify

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return jsonify({
        'status': 'ok',
        'message': 'Welcome to PE-Aequitas Flask backend'
    })

@main_bp.route('/health')
def health():
    return jsonify({'status': 'healthy'})
