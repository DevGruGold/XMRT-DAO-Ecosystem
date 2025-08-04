"""
XMRT-DAO-Ecosystem Main Flask Application
Enhanced with comprehensive MESHNET integration via Meshtastic
and fully asynchronous service architecture.
"""

import os
import logging
import asyncio
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# --- Service and Blueprint Imports ---
# Correctly import the refactored services and blueprints
from services.mining_service import EnhancedSupportXMRService
from services.meshnet_service import MESHNETService
from api.meshnet_routes import meshnet_bp, init_meshnet_service

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)

    # --- Configuration ---
    # Centralized configuration for easy management
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-for-xmrt'),
        'XMRT_TOKEN_ADDRESS': '0x77307DFbc436224d5e6f2048d2b6bDfA66998a15',
        'XMRT_IP_NFT_ADDRESS': '0x9d691fc136a846d7442d1321a2d1b6aaef494eda',
        'MINING_WALLET': '46UxNFuGM2E3UwmZWWJicaRPoRwqwW4byQkaTHkX8yPcVihp91qAVtSFipWUGJJUyTXgzSqxDQtNLf2bsp2DX2qCCgC5mg',
        'SUPPORTXMR_API': 'https://supportxmr.com/api',
        'CACHE_TTL': int(os.environ.get('CACHE_TTL', 120)),
        'MIN_HASHRATE': int(os.environ.get('MIN_HASHRATE', 1000)),
        'OFFLINE_THRESHOLD': int(os.environ.get('OFFLINE_THRESHOLD', 30))
    })

    # --- Service Initialization ---
    # Initialize the enhanced mining service with proper configuration
    mining_service_config = {
        'cache_ttl': app.config['CACHE_TTL'],
        'min_hashrate': app.config['MIN_HASHRATE'],
        'offline_threshold': app.config['OFFLINE_THRESHOLD']
    }
    mining_service = EnhancedSupportXMRService(mining_service_config)
    logger.info("✅ EnhancedSupportXMRService initialized.")

    # Initialize MESHNET service
    meshnet_config = {
        'mesh_port': os.environ.get('MESH_PORT', 'simulate'),
        'update_interval': int(os.environ.get('MESH_UPDATE_INTERVAL', '30'))
    }
    meshnet_service = init_meshnet_service(meshnet_config)
    logger.info("✅ MESHNETService initialized.")
    
    # NOTE: Background task initialization for MESHNET should be handled by a proper task runner
    # For now, we assume it's handled or will be added via a background worker setup.
    
    # --- Blueprint Registration ---
    app.register_blueprint(meshnet_bp, url_prefix='/api/meshnet')
    logger.info("✅ MESHNET API blueprint registered.")

    # --- Core API Routes ---

    @app.route('/')
    def home():
        """Home page with XMRT-DAO-Ecosystem overview."""
        return jsonify({
            'name': 'XMRT-DAO-Ecosystem',
            'version': '2.0.1', # Version bump for this glorious launch
            'status': 'Online and Operational',
            'description': 'Advanced DAO Ecosystem with MESHNET Integration',
            'timestamp': datetime.now().isoformat()
        })

    @app.route('/health')
    def health_check():
        """Comprehensive health check for all core services."""
        try:
            # Run async checks concurrently
            mining_health, meshnet_health = asyncio.run(
                asyncio.gather(
                    mining_service.ping_mining_infrastructure(),
                    meshnet_service.get_mesh_network_health()
                )
            )
            
            overall_healthy = (mining_health.get('supportxmr_ping', {}).get('status') == 'online' and 
                               mining_health.get('api_accessibility', {}).get('status') == 'accessible' and
                               meshnet_health.get('network_health') == 'healthy')

            return jsonify({
                'healthy': overall_healthy,
                'status': 'operational' if overall_healthy else 'degraded',
                'services': {
                    'mining_infra': mining_health,
                    'meshnet_infra': meshnet_health
                },
                'timestamp': datetime.now().isoformat()
            }), 200 if overall_healthy else 503

        except Exception as e:
            logger.error(f"Health check failed catastrophically: {e}")
            return jsonify({'healthy': False, 'status': f'health check failed: {str(e)}'}), 500

    @app.route('/api/dashboard')
    def get_system_dashboard():
        """Get the comprehensive mining and ecosystem dashboard."""
        try:
            dashboard_data = asyncio.run(mining_service.get_comprehensive_mining_dashboard())
            return jsonify({'success': True, 'data': dashboard_data})
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # --- Error Handlers ---

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint not found',
            'message': 'The requested URL was not found on the server.'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal Server Error: {error}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please check the logs.'
        }), 500

    return app

# --- Application Entry Point ---
if __name__ == '__main__':
    # This block is for local development, not for Gunicorn
    app = create_app()
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'

    logger.info(f"🚀 Starting XMRT-DAO-Ecosystem in local development mode on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
else:
    # This block is for Gunicorn production
    # We create the app instance for Gunicorn to discover
    app = create_app()
