"""
XMRT-DAO-Ecosystem Main Flask Application
Version 2.1.0: The Eliza Command Interface Launch
This is the root entry point for the Gunicorn server.
"""

import os
import logging
import asyncio
from datetime import datetime
from flask import Flask, jsonify, request, render_template, current_app
from flask_cors import CORS

# --- Service and Blueprint Imports ---
from services.mining_service import EnhancedSupportXMRService
from services.meshnet_service import MESHNETService
from api.meshnet_routes import meshnet_bp, init_meshnet_service
from services.eliza_agent_service import ElizaAgentService

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder='templates')
    CORS(app)

    # --- Configuration ---
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-for-xmrt-launch'),
    })

    # --- Service Initialization ---
    # Use a context to ensure services are available to all routes
    with app.app_context():
        # Initialize Mining Service
        current_app.mining_service = EnhancedSupportXMRService(config={})
        logger.info("✅ EnhancedSupportXMRService initialized.")

        # Initialize MESHNET Service
        current_app.meshnet_service = init_meshnet_service(config={})
        logger.info("✅ MESHNETService initialized.")
        
        # Initialize Eliza Agent Service and give her access to the other services
        current_app.eliza_agent = ElizaAgentService(
            mining_service=current_app.mining_service, 
            meshnet_service=current_app.meshnet_service
        )
        logger.info("✅ Eliza Agent Service integrated and online.")

    # --- Blueprint Registration ---
    app.register_blueprint(meshnet_bp, url_prefix='/api/meshnet')
    logger.info("✅ MESHNET API blueprint registered.")

    # --- Core API & UI Routes ---

    @app.route('/')
    def chatbot_ui():
        """Serve the main Eliza chatbot UI from templates/index.html."""
        return render_template('index.html')

    @app.route('/api/chat', methods=['POST'])
    def handle_chat():
        """Handle chat messages sent to Eliza."""
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': 'Invalid request format.'}), 400
        
        user_message = data['message']
        
        # Run the async agent command and get the result
        try:
            reply = asyncio.run(current_app.eliza_agent.process_command(user_message))
            return jsonify({'success': True, 'reply': reply})
        except Exception as e:
            logger.error(f"Error processing command in Eliza agent: {e}")
            return jsonify({'success': False, 'error': 'An internal error occurred in the agent.'}), 500

    @app.route('/health')
    def health_check():
        """Comprehensive health check for all core services."""
        # This route is now fully async-aware
        async def do_health_check():
            try:
                mining_health, meshnet_health = await asyncio.gather(
                    current_app.mining_service.ping_mining_infrastructure(),
                    current_app.meshnet_service.get_mesh_network_health()
                )
                
                mining_ok = (mining_health.get('api_accessibility', {}).get('status') == 'accessible')
                meshnet_ok = meshnet_health.get('network_health') == 'healthy'
                overall_healthy = mining_ok and meshnet_ok

                return jsonify({
                    'healthy': overall_healthy,
                    'status': 'operational' if overall_healthy else 'degraded',
                    'services': { 'mining_infra': mining_health, 'meshnet_infra': meshnet_health },
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
            dashboard_data = asyncio.run(current_app.mining_service.get_comprehensive_mining_dashboard())
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
# This line is crucial for Gunicorn to find the app object when it imports the file.
app = create_app()

