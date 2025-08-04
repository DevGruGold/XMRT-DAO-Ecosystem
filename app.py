"""
XMRT-DAO-Ecosystem Main Flask Application
This is the root entry point for the Gunicorn server.
It correctly imports all necessary components from the 'src' package.
"""

import os
import logging
import asyncio
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

# --- CORRECTED IMPORTS ---
# We tell Python to look inside the 'src' package for our modules.
# This resolves the ModuleNotFoundError.
from src.services.mining_service import EnhancedSupportXMRService
from src.services.meshnet_service import MESHNETService
from src.api.meshnet_routes import meshnet_bp, init_meshnet_service

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)

    # --- Configuration ---
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-for-xmrt'),
        'XMRT_TOKEN_ADDRESS': '0x77307DFbc436224d5e6f2048d2b6bDfA66998a15',
        'MINING_WALLET': '46UxNFuGM2E3UwmZWWJicaRPoRwqwW4byQkaTHkX8yPcVihp91qAVtSFipWUGJJUyTXgzSqxDQtNLf2bsp2DX2qCCgC5mg',
        # Add any other necessary config values here
    })

    # --- Service Initialization ---
    # We pass the necessary config directly to the services.
    mining_service = EnhancedSupportXMRService(config={})
    logger.info("✅ EnhancedSupportXMRService initialized.")

    meshnet_service = init_meshnet_service(config={})
    logger.info("✅ MESHNETService initialized.")

    # Add services to the app context so they can be accessed in blueprints/routes
    app.mining_service = mining_service
    app.meshnet_service = meshnet_service
    
    # --- Blueprint Registration ---
    app.register_blueprint(meshnet_bp, url_prefix='/api/meshnet')
    logger.info("✅ MESHNET API blueprint registered.")

    # --- Core API Routes ---

    @app.route('/')
    def home():
        """Home page with XMRT-DAO-Ecosystem overview."""
        return jsonify({
            'name': 'XMRT-DAO-Ecosystem',
            'version': '2.1.0', # The Launch Version!
            'status': 'Online and Operational',
            'timestamp': datetime.now().isoformat()
        })

    @app.route('/health')
    def health_check():
        """Comprehensive health check for all core services."""
        # This route is now fully async-aware
        async def do_health_check():
            try:
                mining_health, meshnet_health = await asyncio.gather(
                    app.mining_service.ping_mining_infrastructure(),
                    app.meshnet_service.get_mesh_network_health()
                )
                
                mining_ok = (mining_health.get('supportxmr_ping', {}).get('status') == 'online' and 
                             mining_health.get('api_accessibility', {}).get('status') == 'accessible')
                meshnet_ok = meshnet_health.get('network_health') == 'healthy'
                overall_healthy = mining_ok and meshnet_ok

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
        
        return asyncio.run(do_health_check())

    @app.route('/api/dashboard')
    def get_system_dashboard():
        """Get the comprehensive mining and ecosystem dashboard."""
        try:
            dashboard_data = asyncio.run(app.mining_service.get_comprehensive_mining_dashboard())
            return jsonify({'success': True, 'data': dashboard_data})
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # --- Error Handlers ---
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal Server Error: {error}")
        return jsonify({'error': 'Internal server error'}), 500

    return app

# --- Application Entry Point for Gunicorn ---
# This line is crucial for Gunicorn to find the app object.
app = create_app()

# This block is for local development only.
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"🚀 Starting XMRT-DAO-Ecosystem in LOCAL DEV MODE on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)

