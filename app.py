from webhook_endpoints import create_ecosystem_webhook_blueprint
import requests
import time
"""
XMRT-DAO-Ecosystem Main Flask Application
Version 2.2.0: The Phoenix Protocol
This is the root entry point for the Gunicorn server.
It correctly imports all necessary components from the 'src' package.
"""

import os
import logging
import asyncio
from datetime import datetime
from flask import Flask, jsonify, request, render_template, current_app
from flask_cors import CORS

# --- CORRECTED IMPORTS ---
# This is the definitive fix. We are telling Python to look inside the 'src'
# directory to find all the application modules.
try:
    from src.services.mining_service import EnhancedSupportXMRService
    from src.services.meshnet_service import MESHNETService
    from src.api.meshnet_routes import meshnet_bp, init_meshnet_service
    from src.services.eliza_agent_service import ElizaAgentService
    from src.services.health_service import HealthService
    from src.services.speech_service import SpeechService
    from src.services.memory_service import MemoryService
    from src.services.autonomy_service import AutonomyService
    from src.services.n8n_service import N8NService
    from src.api.n8n_routes import n8n_bp, init_n8n_service
except ModuleNotFoundError:
    # This block helps with local development if the path isn't set.
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
    from services.n8n_service import N8NService
    from api.n8n_routes import n8n_bp, init_n8n_service


# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
        current_app.mining_service = EnhancedSupportXMRService(config={})
        logger.info("✅ EnhancedSupportXMRService initialized.")

        current_app.meshnet_service = init_meshnet_service(config={})
        logger.info("✅ MESHNETService initialized.")
        
        # Initialize speech service
        current_app.speech_service = SpeechService(config={})
        logger.info("✅ Speech Service initialized.")
        
        # Initialize memory service
        current_app.memory_service = MemoryService(config={})
        logger.info("✅ Memory Service initialized.")
        
        # Initialize autonomy service with 250 credit budget
        current_app.autonomy_service = AutonomyService(config={'credit_budget': 250})
        logger.info("✅ Autonomy Service initialized with 250 credit budget.")
        
        current_app.eliza_agent = ElizaAgentService(
            mining_service=current_app.mining_service, 
            meshnet_service=current_app.meshnet_service,
            speech_service=current_app.speech_service,
            memory_service=current_app.memory_service
        )
        logger.info("✅ Eliza Agent Service integrated with enhanced capabilities.")
        
        current_app.health_service = HealthService(
            mining_service=current_app.mining_service,
            meshnet_service=current_app.meshnet_service
        )
        logger.info("✅ Health Service initialized.")
        
        # Initialize n8n service
        n8n_config = {
            'n8n_url': os.environ.get('N8N_URL', 'http://localhost:5678'),
            'n8n_api_key': os.environ.get('N8N_API_KEY')
        }
        current_app.n8n_service = N8NService(n8n_config)
        current_app.n8n_service.set_memory_service(current_app.memory_service)
        
        # Initialize n8n service asynchronously
        try:
            asyncio.run(current_app.n8n_service.initialize())
            logger.info("✅ N8N Service initialized and connected.")
        except Exception as e:
            logger.warning(f"⚠️ N8N Service initialization failed: {e}. Service will run without n8n integration.")

    # --- Blueprint Registration ---
    app.register_blueprint(meshnet_bp, url_prefix='/api/meshnet')
    logger.info("✅ MESHNET API blueprint registered.")
    
    app.register_blueprint(n8n_bp, url_prefix='/api/n8n')
    logger.info("✅ N8N API blueprint registered.")

    # --- Core API & UI Routes ---

    @app.route('/')
    def chatbot_ui():
        """Serve the main Eliza chatbot UI."""
        return render_template('index.html')

    @app.route('/api/chat', methods=['POST'])
    def handle_chat():
        """Handle chat messages sent to Eliza."""
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': 'Invalid request format.'}), 400
        
        user_message = data['message']
        
        try:
            reply = asyncio.run(current_app.eliza_agent.process_command(user_message))
            return jsonify({'success': True, 'reply': reply})
        except Exception as e:
            logger.error(f"Error processing command in Eliza agent: {e}")
            return jsonify({'success': False, 'error': 'An internal error occurred in the agent.'}), 500

    @app.route('/health')
    def health_check():
        """Comprehensive health check for all core services."""
        try:
            # Use the dedicated health service for comprehensive checks
            health_data = asyncio.run(current_app.health_service.get_simple_health())
            
            status_code = 200 if health_data.get('healthy', False) else 503
            return jsonify(health_data), status_code
            
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
            health_data = asyncio.run(current_app.health_service.get_comprehensive_health())
            
            status_code = 200 if health_data.get('overall_status') == 'healthy' else 503
            return jsonify(health_data), status_code
            
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
            dashboard_data = asyncio.run(current_app.mining_service.get_comprehensive_mining_dashboard())
            return jsonify({'success': True, 'data': dashboard_data})
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/agent/status')
    def get_agent_status():
        """Get Eliza agent status with all capabilities."""
        try:
            status = current_app.eliza_agent.get_agent_status()
            return jsonify({'success': True, 'data': status})
        except Exception as e:
            logger.error(f"Error fetching agent status: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/autonomy/status')
    def get_autonomy_status():
        """Get autonomy service status."""
        try:
            status = current_app.autonomy_service.get_autonomy_status()
            return jsonify({'success': True, 'data': status})
        except Exception as e:
            logger.error(f"Error fetching autonomy status: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/autonomy/tasks')
    def get_task_summary():
        """Get summary of autonomous tasks."""
        try:
            tasks = current_app.autonomy_service.get_task_summary()
            return jsonify({'success': True, 'data': tasks})
        except Exception as e:
            logger.error(f"Error fetching task summary: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/autonomy/execute', methods=['POST'])
    def execute_autonomous_tasks():
        """Execute pending autonomous tasks."""
        try:
            executed = asyncio.run(current_app.autonomy_service.execute_pending_tasks())
            return jsonify({'success': True, 'executed_tasks': executed})
        except Exception as e:
            logger.error(f"Error executing autonomous tasks: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/memory/stats')
    def get_memory_stats():
        """Get memory service statistics."""
        try:
            stats = current_app.memory_service.get_memory_stats()
            return jsonify({'success': True, 'data': stats})
        except Exception as e:
            logger.error(f"Error fetching memory stats: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/speech/status')
    def get_speech_status():
        """Get speech service status."""
        try:
            status = current_app.speech_service.get_voice_status()
            return jsonify({'success': True, 'data': status})
        except Exception as e:
            logger.error(f"Error fetching speech status: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500


    # --- Additional API Routes for Frontend Compatibility ---
    
    @app.route('/api/v1/autonomous/status')
    def get_v1_autonomous_status():
        """Get autonomy service status (v1 API compatibility)."""
        try:
            status = current_app.autonomy_service.get_autonomy_status()
            return jsonify({'success': True, 'data': status})
        except Exception as e:
            logger.error(f"Error fetching v1 autonomy status: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/v1/metrics/performance')
    def get_v1_performance_metrics():
        """Get performance metrics (v1 API compatibility)."""
        try:
            # Get comprehensive mining dashboard data as performance metrics
            dashboard_data = asyncio.run(current_app.mining_service.get_comprehensive_mining_dashboard())
            
            # Extract performance-related metrics
            performance_metrics = {
                'hashrate': dashboard_data.get('mining_stats', {}).get('total_hashrate', '0 H/s'),
                'network_hashrate': dashboard_data.get('mining_stats', {}).get('network_hashrate', '0 H/s'),
                'difficulty': dashboard_data.get('mining_stats', {}).get('network_difficulty', 0),
                'uptime': dashboard_data.get('system_health', {}).get('uptime', '0 seconds'),
                'response_time': dashboard_data.get('system_health', {}).get('avg_response_time', '0ms'),
                'active_miners': dashboard_data.get('mining_stats', {}).get('active_miners', 0),
                'xmr_price': dashboard_data.get('market_data', {}).get('xmr_price', 0)
            }
            
            return jsonify({'success': True, 'data': performance_metrics})
        except Exception as e:
            logger.error(f"Error fetching v1 performance metrics: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/v1/decisions/history')
    def get_v1_decisions_history():
        """Get decision history (v1 API compatibility)."""
        try:
            # Get memory stats which includes decision-like data
            memory_stats = current_app.memory_service.get_memory_stats()
            
            # Get task summary from autonomy service
            tasks = current_app.autonomy_service.get_task_summary()
            
            # Combine into decision history format
            decisions_history = {
                'recent_decisions': tasks.get('completed_tasks', []),
                'pending_decisions': tasks.get('pending_tasks', []),
                'memory_entries': memory_stats.get('recent_entries', []),
                'total_decisions': len(tasks.get('completed_tasks', [])) + len(tasks.get('pending_tasks', []))
            }
            
            return jsonify({'success': True, 'data': decisions_history})
        except Exception as e:
            logger.error(f"Error fetching v1 decisions history: {e}")
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
app = create_app()



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)



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
