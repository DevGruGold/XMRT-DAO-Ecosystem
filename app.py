"""
XMRT-DAO-Ecosystem Main Flask Application
Version 2.2.4: Phoenix Protocol - Dispatch Core Repair (Feature Complete)

This version correctly integrates the Intelligent Dispatcher into the main chat
endpoint while preserving 100% of the original application's features and routes.
The asyncio conflict is resolved by calling services directly.
"""

import os
import logging
import asyncio
import json
from datetime import datetime
from flask import Flask, jsonify, request, render_template, current_app
from flask_cors import CORS

# --- All original imports are preserved ---
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

# --- NEW: Intelligent Dispatcher (Corrected to call services directly) ---
class IntelligentDispatcher:
    """
    Simulates AI by dispatching queries to the appropriate internal service.
    This version calls services directly to avoid asyncio conflicts.
    """
    def __init__(self):
        self.request_log = []

    async def analyze_and_dispatch(self, query: str) -> dict:
        """Analyzes query and dispatches to the correct internal handler."""
        query_lower = query.lower()
        
        # Keyword-based routing to internal services
        if 'dashboard' in query_lower:
            return await self.get_dashboard_data()
        elif 'mining' in query_lower or 'hashrate' in query_lower:
            return await self.get_mining_stats()
        elif 'meshnet' in query_lower or 'nodes' in query_lower:
            return current_app.meshnet_service.get_mesh_network_status() # Not async
        elif 'autonomy' in query_lower or 'task' in query_lower:
            return current_app.autonomy_service.get_autonomy_status() # Not async
        elif 'memory' in query_lower:
            return current_app.memory_service.get_memory_stats() # Not async
        elif 'health' in query_lower:
            return await self.get_health_status()
        elif 'status' in query_lower or 'agent' in query_lower:
             return current_app.eliza_agent.get_agent_status() # Not async
        else:
            return await self.get_default_response(query)

    # --- Direct Service Handlers (THE FIX) ---
    async def get_dashboard_data(self) -> dict:
        logger.info("Dispatcher: Calling mining_service.get_comprehensive_mining_dashboard...")
        return await current_app.mining_service.get_comprehensive_mining_dashboard()

    async def get_mining_stats(self) -> dict:
        logger.info("Dispatcher: Calling mining_service.get_current_stats...")
        return await current_app.mining_service.get_current_stats()
        
    async def get_health_status(self) -> dict:
        logger.info("Dispatcher: Calling health_service.get_simple_health...")
        return await current_app.health_service.get_simple_health()
        
    async def get_default_response(self, query: str) -> dict:
        logger.info("Dispatcher: No keyword match, using Eliza's default processor.")
        return await current_app.eliza_agent.process_command(query)

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder='src/templates')
    CORS(app)
    app.config.update({'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key')})

    # --- Service Initialization (All original services preserved) ---
    with app.app_context():
        current_app.intelligent_dispatcher = IntelligentDispatcher()
        logger.info("✅ XMRT Intelligent Dispatcher (v2.2.4 - Core Repaired) initialized.")
        current_app.mining_service = EnhancedSupportXMRService(config={})
        current_app.meshnet_service = init_meshnet_service(config={})
        current_app.speech_service = SpeechService(config={})
        current_app.memory_service = MemoryService(config={})
        current_app.autonomy_service = AutonomyService(config={'credit_budget': 250})
        current_app.eliza_agent = ElizaAgentService(
            mining_service=current_app.mining_service, 
            meshnet_service=current_app.meshnet_service,
            speech_service=current_app.speech_service,
            memory_service=current_app.memory_service
        )
        current_app.health_service = HealthService(
            mining_service=current_app.mining_service,
            meshnet_service=current_app.meshnet_service
        )

    # --- Blueprint Registration (Preserved) ---
    app.register_blueprint(meshnet_bp, url_prefix='/api/meshnet')

    # --- Core API & UI Routes ---

    @app.route('/')
    def chatbot_ui():
        """Serve the main Eliza chatbot UI."""
        return render_template('index.html')

    # ========================================================================
    # === CRITICAL FIX: /api/chat now uses the Intelligent Dispatcher ===
    # ========================================================================
    @app.route('/api/chat', methods=['POST'])
    async def handle_chat():
        """Handle chat messages using the corrected Intelligent Dispatcher."""
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': 'Invalid request format.'}), 400
        
        user_message = data['message']
        
        try:
            intelligent_response = await current_app.intelligent_dispatcher.analyze_and_dispatch(user_message)
            
            # Format the dictionary response for clean, readable output
            if isinstance(intelligent_response, dict):
                intelligent_response = json.dumps(intelligent_response, indent=2, default=str)

            return jsonify({'success': True, 'reply': intelligent_response})
            
        except Exception as e:
            logger.error(f"Error in Intelligent Dispatcher: {e}", exc_info=True)
            return jsonify({'success': False, 'error': 'An internal error occurred in the agent dispatch core.'}), 500

    # ========================================================================
    # === ALL OTHER ORIGINAL ROUTES ARE PRESERVED FOR DIRECT ACCESS ===
    # ========================================================================

    @app.route('/health')
    async def health_check():
        """Comprehensive health check for all core services."""
        try:
            health_data = await current_app.health_service.get_simple_health()
            status_code = 200 if health_data.get('healthy', False) else 503
            return jsonify(health_data), status_code
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({'healthy': False, 'status': 'error', 'error': str(e)}), 500

    @app.route('/health/detailed')
    async def detailed_health_check():
        """Detailed health check with comprehensive service analysis."""
        try:
            health_data = await current_app.health_service.get_comprehensive_health()
            status_code = 200 if health_data.get('overall_status') == 'healthy' else 503
            return jsonify(health_data), status_code
        except Exception as e:
            return jsonify({'overall_status': 'unhealthy', 'error': str(e)}), 500

    @app.route('/api/dashboard')
    async def get_system_dashboard():
        """Get the comprehensive mining and ecosystem dashboard."""
        try:
            dashboard_data = await current_app.mining_service.get_comprehensive_mining_dashboard()
            return jsonify({'success': True, 'data': dashboard_data}), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/agent/status')
    def get_agent_status():
        """Get Eliza agent status with all capabilities."""
        try:
            status = current_app.eliza_agent.get_agent_status()
            return jsonify({'success': True, 'data': status}), 200
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

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
    async def execute_autonomous_tasks():
        try:
            executed = await current_app.autonomy_service.execute_pending_tasks()
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
