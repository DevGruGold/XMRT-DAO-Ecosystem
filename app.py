"""
XMRT-DAO-Ecosystem Main Flask Application
Version 2.2.3: Phoenix Protocol - Simulated Sentience Core (Full Integration)
This version correctly integrates the Intelligent Dispatcher into the main chat
endpoint while preserving all existing application functionality.
"""

import os
import logging
import asyncio
import json
from datetime import datetime
from flask import Flask, jsonify, request, render_template, current_app
from flask_cors import CORS

# --- CORRECTED IMPORTS (All original imports preserved) ---
try:
    from src.services.mining_service import EnhancedSupportXMRService
    from src.services.meshnet_service import MESHNETService
    from src.api.meshnet_routes import meshnet_bp, init_meshnet_service
    from src.services.eliza_agent_service import ElizaAgentService
    from src.services.health_service import HealthService
    from src.services.speech_service import SpeechService
    from src.services.memory_service import MemoryService
    from src.services.autonomy_service import AutonomyService
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
    from services.mining_service import EnhancedSupportXMRService
    from services.meshnet_service import MESHNETService
    from api.meshnet_routes import meshnet_bp, init_meshnet_service
    from services.eliza_agent_service import ElizaAgentService
    from services.health_service import HealthService
    from services.speech_service import SpeechService
    from services.memory_service import MemoryService
    from services.autonomy_service import AutonomyService

# --- NEW: Intelligent Dispatcher (Replaces AI Router Placeholders) ---
class IntelligentDispatcher:
    """
    Simulates AI by dispatching queries to the appropriate internal service
    to generate robust, data-driven responses without external API calls.
    """
    def __init__(self):
        self.request_log = []

    def analyze_and_dispatch(self, query: str) -> dict:
        """Analyzes query and dispatches to the correct internal handler."""
        query_lower = query.lower()
        
        # Keyword-based routing to internal services
        if 'dashboard' in query_lower:
            return self.get_dashboard_data()
        elif 'mining' in query_lower or 'hashrate' in query_lower:
            return self.get_mining_stats()
        elif 'meshnet' in query_lower or 'nodes' in query_lower:
            return self.get_meshnet_status()
        elif 'autonomy' in query_lower or 'task' in query_lower:
            return self.get_autonomy_status()
        elif 'memory' in query_lower:
            return self.get_memory_stats()
        elif 'health' in query_lower or 'status' in query_lower:
            return self.get_health_status()
        elif 'agent' in query_lower:
            return self.get_agent_status()
        else:
            # Fallback for general or unrecognized queries
            return self.get_default_response(query)

    # --- Internal Service Handlers ---
    def get_dashboard_data(self) -> dict:
        logger.info("Dispatcher: Routing to get_system_dashboard.")
        response, _ = get_system_dashboard()
        return response.get_json()

    def get_mining_stats(self) -> dict:
        logger.info("Dispatcher: Routing to mining_service for stats.")
        # This is a simplified call; a dedicated method in MiningService would be better
        dashboard_data = asyncio.run(current_app.mining_service.get_comprehensive_mining_dashboard())
        return {"mining_summary": dashboard_data.get('pool_statistics')}

    def get_meshnet_status(self) -> dict:
        logger.info("Dispatcher: Routing to meshnet_service.")
        return current_app.meshnet_service.get_mesh_network_status()

    def get_autonomy_status(self) -> dict:
        logger.info("Dispatcher: Routing to autonomy_service.")
        response, _ = get_autonomy_status()
        return response.get_json()

    def get_memory_stats(self) -> dict:
        logger.info("Dispatcher: Routing to memory_service.")
        response, _ = get_memory_stats()
        return response.get_json()

    def get_health_status(self) -> dict:
        logger.info("Dispatcher: Routing to health_service.")
        response, _ = health_check()
        return response.get_json()

    def get_agent_status(self) -> dict:
        logger.info("Dispatcher: Routing to eliza_agent for status.")
        response, _ = get_agent_status()
        return response.get_json()
        
    def get_default_response(self, query: str) -> dict:
        logger.info("Dispatcher: No specific keyword match, using Eliza's default processor.")
        # Uses Eliza's original command processing as a final fallback
        return asyncio.run(current_app.eliza_agent.process_command(query))

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder='src/templates')
    CORS(app)

    # --- Configuration (Preserved) ---
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-for-xmrt-phoenix'),
    })

    # --- Service Initialization (All original services preserved) ---
    with app.app_context():
        # NEW: Initialize the Intelligent Dispatcher
        current_app.intelligent_dispatcher = IntelligentDispatcher()
        logger.info("✅ XMRT Intelligent Dispatcher initialized.")
        
        # Existing service initializations
        current_app.mining_service = EnhancedSupportXMRService(config={})
        logger.info("✅ EnhancedSupportXMRService initialized.")
        current_app.meshnet_service = init_meshnet_service(config={})
        logger.info("✅ MESHNETService initialized.")
        current_app.speech_service = SpeechService(config={})
        logger.info("✅ Speech Service initialized.")
        current_app.memory_service = MemoryService(config={})
        logger.info("✅ Memory Service initialized.")
        current_app.autonomy_service = AutonomyService(config={'credit_budget': 250})
        logger.info("✅ Autonomy Service initialized.")
        current_app.eliza_agent = ElizaAgentService(
            mining_service=current_app.mining_service, 
            meshnet_service=current_app.meshnet_service,
            speech_service=current_app.speech_service,
            memory_service=current_app.memory_service
        )
        logger.info("✅ Eliza Agent Service integrated.")
        current_app.health_service = HealthService(
            mining_service=current_app.mining_service,
            meshnet_service=current_app.meshnet_service
        )
        logger.info("✅ Health Service initialized.")

    # --- Blueprint Registration (Preserved) ---
    app.register_blueprint(meshnet_bp, url_prefix='/api/meshnet')
    logger.info("✅ MESHNET API blueprint registered.")

    # --- Core API & UI Routes ---

    @app.route('/')
    def chatbot_ui():
        """Serve the main Eliza chatbot UI."""
        return render_template('index.html')

    # ========================================================================
    # === CRITICAL FIX: /api/chat now uses the Intelligent Dispatcher ===
    # ========================================================================
    @app.route('/api/chat', methods=['POST'])
    def handle_chat():
        """Handle chat messages by routing them through the Intelligent Dispatcher."""
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': 'Invalid request format.'}), 400
        
        user_message = data['message']
        
        try:
            # The dispatcher analyzes the query and calls the correct internal service
            intelligent_response = current_app.intelligent_dispatcher.analyze_and_dispatch(user_message)
            
            # The response is now rich with real, live system data
            return jsonify({'success': True, 'reply': intelligent_response})
            
        except Exception as e:
            logger.error(f"Error in Intelligent Dispatcher: {e}", exc_info=True)
            return jsonify({'success': False, 'error': 'An internal error occurred in the agent dispatch core.'}), 500

    # ========================================================================
    # === ALL OTHER ROUTES ARE PRESERVED FOR DIRECT ACCESS ===
    # ========================================================================

    @app.route('/health')
    def health_check():
        """Comprehensive health check for all core services."""
        try:
            health_data = asyncio.run(current_app.health_service.get_simple_health())
            status_code = 200 if health_data.get('healthy', False) else 503
            return jsonify(health_data), status_code
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({'healthy': False, 'status': 'error', 'error': str(e)}), 500

    @app.route('/health/detailed')
    def detailed_health_check():
        """Detailed health check with comprehensive service analysis."""
        try:
            health_data = asyncio.run(current_app.health_service.get_comprehensive_health())
            status_code = 200 if health_data.get('overall_status') == 'healthy' else 503
            return jsonify(health_data), status_code
        except Exception as e:
            logger.error(f"Detailed health check failed: {e}")
            return jsonify({'overall_status': 'unhealthy', 'error': str(e)}), 500

    @app.route('/api/dashboard')
    def get_system_dashboard():
        """Get the comprehensive mining and ecosystem dashboard."""
        try:
            dashboard_data = asyncio.run(current_app.mining_service.get_comprehensive_mining_dashboard())
            return jsonify({'success': True, 'data': dashboard_data}), 200
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/agent/status')
    def get_agent_status():
        """Get Eliza agent status with all capabilities."""
        try:
            status = current_app.eliza_agent.get_agent_status()
            return jsonify({'success': True, 'data': status}), 200
        except Exception as e:
            logger.error(f"Error fetching agent status: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # (All other autonomy, memory, and speech routes are preserved below)

    @app.route('/api/autonomy/status')
    def get_autonomy_status():
        try:
            status = current_app.autonomy_service.get_autonomy_status()
            return jsonify({'success': True, 'data': status}), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/autonomy/tasks')
    def get_task_summary():
        try:
            tasks = current_app.autonomy_service.get_task_summary()
            return jsonify({'success': True, 'data': tasks}), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/autonomy/execute', methods=['POST'])
    def execute_autonomous_tasks():
        try:
            executed = asyncio.run(current_app.autonomy_service.execute_pending_tasks())
            return jsonify({'success': True, 'executed_tasks': executed}), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/memory/stats')
    def get_memory_stats():
        try:
            stats = current_app.memory_service.get_memory_stats()
            return jsonify({'success': True, 'data': stats}), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/speech/status')
    def get_speech_status():
        try:
            status = current_app.speech_service.get_voice_status()
            return jsonify({'success': True, 'data': status}), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    # --- Error Handlers (Preserved) ---
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal Server Error: {error}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

    return app

# --- Application Entry Point for Gunicorn (Preserved) ---
app = create_app()
