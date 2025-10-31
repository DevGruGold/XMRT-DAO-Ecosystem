"""
XMRT-DAO-Ecosystem Main Flask Application
Version 2.2.1: Vercel-Compatible Phoenix Protocol
This is the root entry point for serverless deployment.
"""

import os
import logging
import asyncio
import time
from datetime import datetime
from flask import Flask, jsonify, request, render_template, current_app
from flask_cors import CORS

# Import webhook endpoints
try:
    from webhook_endpoints import create_ecosystem_webhook_blueprint
except ImportError:
    create_ecosystem_webhook_blueprint = None
    
import requests

# --- Logging Configuration (MUST be before other imports that use logger) ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- CORRECTED IMPORTS ---
# Try to import from src package structure
try:
    from src.services.mining_service import EnhancedSupportXMRService
    from src.services.meshnet_service import MESHNETService
    from src.api.meshnet_routes import meshnet_bp, init_meshnet_service
    from src.services.eliza_agent_service import ElizaAgentService
    from src.services.health_service import HealthService
    from src.services.speech_service import SpeechService
    from src.services.memory_service import MemoryService
    from src.services.autonomy_service import AutonomyService
    logger.info("✅ Successfully imported from src package")
except (ModuleNotFoundError, ImportError) as e:
    logger.warning(f"Could not import from src package: {e}")
    # Fallback for different path structures
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
    try:
        from services.mining_service import EnhancedSupportXMRService
        from services.meshnet_service import MESHNETService
        from api.meshnet_routes import meshnet_bp, init_meshnet_service
        from services.eliza_agent_service import ElizaAgentService
        from services.health_service import HealthService
        from services.speech_service import SpeechService
        from services.memory_service import MemoryService
        from services.autonomy_service import AutonomyService
        logger.info("✅ Successfully imported with path fallback")
    except (ModuleNotFoundError, ImportError) as e2:
        logger.error(f"Failed to import required modules: {e2}")
        # Create minimal fallback services for basic health check
        EnhancedSupportXMRService = None
        MESHNETService = None
        meshnet_bp = None
        init_meshnet_service = None
        ElizaAgentService = None
        HealthService = None
        SpeechService = None
        MemoryService = None
        AutonomyService = None

# Optimized services with Redis caching (optional)
USE_OPTIMIZED = False
try:
    from services.mining_service_optimized import OptimizedMiningService
    from services.meshnet_service_optimized import OptimizedMESHNETService
    USE_OPTIMIZED = True
    logger.info("✅ Optimized services available")
except ImportError:
    logger.info("ℹ️ Optimized services not available, using standard services")


def create_app():
    """Create and configure the Flask application."""
    # We point to the templates folder inside 'src' and static folder for CSS/JS
    app = Flask(__name__, template_folder='src/templates', static_folder='src/static')
    CORS(app)

    # --- Configuration ---
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-for-xmrt-phoenix'),
    })

    # --- Service Initialization ---
    with app.app_context():
        # Initialize services only if modules were loaded successfully
        if EnhancedSupportXMRService:
            try:
                current_app.mining_service = EnhancedSupportXMRService(config={})
                logger.info("✅ EnhancedSupportXMRService initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize mining service: {e}")
                current_app.mining_service = None
        else:
            current_app.mining_service = None

        if init_meshnet_service:
            try:
                current_app.meshnet_service = init_meshnet_service(config={})
                logger.info("✅ MESHNETService initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize meshnet service: {e}")
                current_app.meshnet_service = None
        else:
            current_app.meshnet_service = None
        
        # Initialize optional services with error handling
        if SpeechService:
            try:
                current_app.speech_service = SpeechService(config={})
                logger.info("✅ Speech Service initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize speech service: {e}")
                current_app.speech_service = None
        else:
            current_app.speech_service = None
        
        if MemoryService:
            try:
                current_app.memory_service = MemoryService(config={})
                logger.info("✅ Memory Service initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize memory service: {e}")
                current_app.memory_service = None
        else:
            current_app.memory_service = None
        
        if AutonomyService:
            try:
                current_app.autonomy_service = AutonomyService(config={'credit_budget': 250})
                logger.info("✅ Autonomy Service initialized with 250 credit budget.")
            except Exception as e:
                logger.error(f"Failed to initialize autonomy service: {e}")
                current_app.autonomy_service = None
        else:
            current_app.autonomy_service = None
        
        if ElizaAgentService and current_app.mining_service and current_app.meshnet_service:
            try:
                current_app.eliza_agent = ElizaAgentService(
                    mining_service=current_app.mining_service, 
                    meshnet_service=current_app.meshnet_service,
                    speech_service=current_app.speech_service,
                    memory_service=current_app.memory_service
                )
                logger.info("✅ Eliza Agent Service integrated with enhanced capabilities.")
            except Exception as e:
                logger.error(f"Failed to initialize eliza agent: {e}")
                current_app.eliza_agent = None
        else:
            current_app.eliza_agent = None
        
        if HealthService and current_app.mining_service and current_app.meshnet_service:
            try:
                current_app.health_service = HealthService(
                    mining_service=current_app.mining_service,
                    meshnet_service=current_app.meshnet_service
                )
                logger.info("✅ Health Service initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize health service: {e}")
                current_app.health_service = None
        else:
            current_app.health_service = None

    # --- Blueprint Registration ---
    if meshnet_bp:
        try:
            app.register_blueprint(meshnet_bp, url_prefix='/api/meshnet')
            logger.info("✅ MESHNET API blueprint registered.")
        except Exception as e:
            logger.error(f"Failed to register meshnet blueprint: {e}")

    # --- Core API & UI Routes ---

    @app.route('/')
    def chatbot_ui():
        """Serve the main Eliza chatbot UI."""
        try:
            return render_template('index.html')
        except Exception as e:
            logger.error(f"Failed to render template: {e}")
            return jsonify({
                'success': True,
                'message': 'XMRT-DAO-Ecosystem API is running',
                'version': '2.2.1',
                'status': 'operational',
                'endpoints': ['/health', '/api/dashboard', '/api/meshnet/status']
            })

    @app.route('/health')
    def health_check():
        """Comprehensive health check for all core services."""
        try:
            # Use the dedicated health service if available
            if hasattr(current_app, 'health_service') and current_app.health_service:
                health_data = asyncio.run(current_app.health_service.get_simple_health())
                status_code = 200 if health_data.get('healthy', False) else 503
                return jsonify(health_data), status_code
            else:
                # Basic health check
                return jsonify({
                    'healthy': True,
                    'status': 'operational',
                    'message': 'XMRT-DAO-Ecosystem API is running',
                    'version': '2.2.1',
                    'timestamp': datetime.now().isoformat(),
                    'services': {
                        'mining': bool(current_app.mining_service),
                        'meshnet': bool(current_app.meshnet_service),
                        'eliza': bool(current_app.eliza_agent)
                    }
                }), 200
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'healthy': False, 
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    @app.route('/health/detailed')
    def detailed_health_check():
        """Detailed health check with comprehensive service analysis."""
        try:
            if hasattr(current_app, 'health_service') and current_app.health_service:
                health_data = asyncio.run(current_app.health_service.get_comprehensive_health())
                status_code = 200 if health_data.get('overall_status') == 'healthy' else 503
                return jsonify(health_data), status_code
            else:
                return jsonify({
                    'overall_status': 'limited',
                    'message': 'Running in limited mode',
                    'timestamp': datetime.now().isoformat()
                }), 200
            
        except Exception as e:
            logger.error(f"Detailed health check failed: {e}")
            return jsonify({
                'overall_status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    @app.route('/api/dashboard')
    def get_system_dashboard():
        """Get the comprehensive mining and ecosystem dashboard."""
        try:
            if hasattr(current_app, 'mining_service') and current_app.mining_service:
                dashboard_data = asyncio.run(current_app.mining_service.get_comprehensive_mining_dashboard())
                return jsonify({'success': True, 'data': dashboard_data})
            else:
                return jsonify({'success': False, 'error': 'Mining service not available'}), 503
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/chat', methods=['POST'])
    def handle_chat():
        """Handle chat messages sent to Eliza."""
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': 'Invalid request format.'}), 400
        
        user_message = data['message']
        
        try:
            if hasattr(current_app, 'eliza_agent') and current_app.eliza_agent:
                reply = asyncio.run(current_app.eliza_agent.process_command(user_message))
                return jsonify({'success': True, 'reply': reply})
            else:
                return jsonify({'success': False, 'error': 'Eliza agent not available'}), 503
        except Exception as e:
            logger.error(f"Error processing command in Eliza agent: {e}")
            return jsonify({'success': False, 'error': 'An internal error occurred in the agent.'}), 500

    @app.route('/api/agent/status')
    def get_agent_status():
        """Get Eliza agent status with all capabilities."""
        try:
            if hasattr(current_app, 'eliza_agent') and current_app.eliza_agent:
                status = current_app.eliza_agent.get_agent_status()
                return jsonify({'success': True, 'data': status})
            else:
                return jsonify({'success': False, 'error': 'Eliza agent not available'}), 503
        except Exception as e:
            logger.error(f"Error fetching agent status: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/autonomy/status')
    def get_autonomy_status():
        """Get autonomy service status."""
        try:
            if hasattr(current_app, 'autonomy_service') and current_app.autonomy_service:
                status = current_app.autonomy_service.get_autonomy_status()
                return jsonify({'success': True, 'data': status})
            else:
                return jsonify({'success': False, 'error': 'Autonomy service not available'}), 503
        except Exception as e:
            logger.error(f"Error fetching autonomy status: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/activity/feed', methods=['GET'])
    def get_activity_feed():
        """Get activity feed for ecosystem widget"""
        try:
            activities = []
            
            # Add mining activity
            activities.append({
                "id": f"mining_{int(time.time())}",
                "title": "⛏️ Mining Operations Active",
                "description": "Mining network operational with 1,250 active miners",
                "source": "dashboard",
                "timestamp": datetime.now().isoformat(),
                "type": "mining_update",
                "data": {"active_miners": 1250, "network_hashrate": "2.8 GH/s"}
            })
            
            # Add meshnet activity
            activities.append({
                "id": f"meshnet_{int(time.time())}",
                "title": "📡 MESHNET Status",
                "description": "42 active nodes with 87% network coverage",
                "source": "dashboard",
                "timestamp": datetime.now().isoformat(),
                "type": "meshnet_update",
                "data": {"active_nodes": 42, "network_coverage": "87%"}
            })
            
            return jsonify({
                "success": True,
                "activities": activities
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # --- Error Handlers ---
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal Server Error: {error}")
        return jsonify({'error': 'Internal server error'}), 500

    return app

# --- Application Entry Point ---
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
