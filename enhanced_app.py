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
    from src.services.health_service import HealthService
    from src.services.speech_service import SpeechService
    from src.services.autonomy_service import AutonomyService
except ModuleNotFoundError:
    # This block helps with local development if the path isn't set.
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
    from services.mining_service import EnhancedSupportXMRService
    from services.meshnet_service import MESHNETService
    from api.meshnet_routes import meshnet_bp, init_meshnet_service
    from services.health_service import HealthService
    from services.speech_service import SpeechService
    from services.autonomy_service import AutonomyService

# Import our enhanced services
from enhanced_memory_service import EnhancedMemoryService
from enhanced_eliza_agent_service import EnhancedElizaAgentService

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format=
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    # We point to the templates folder inside 'src'
    app = Flask(__name__, template_folder='src/templates')
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

        # Initialize enhanced memory service with XMRT knowledgebase
        current_app.memory_service = EnhancedMemoryService(config={
            'memory_file': 'data/eliza_memory.json',
            'knowledgebase_file': '/home/ubuntu/xmrt_knowledgebase.json'
        })
        logger.info("✅ Enhanced Memory Service initialized with XMRT knowledgebase.")

        # Initialize autonomy service with 250 credit budget
        current_app.autonomy_service = AutonomyService(config={'credit_budget': 250})
        logger.info("✅ Autonomy Service initialized with 250 credit budget.")

        # Initialize enhanced Eliza agent with all services
        current_app.eliza_agent = EnhancedElizaAgentService(
            mining_service=current_app.mining_service,
            meshnet_service=current_app.meshnet_service,
            speech_service=current_app.speech_service,
            memory_service=current_app.memory_service
        )
        logger.info("✅ Enhanced Eliza Agent Service integrated with XMRT knowledgebase.")

        current_app.health_service = HealthService(
            mining_service=current_app.mining_service,
            meshnet_service=current_app.meshnet_service
        )
        logger.info("✅ Health Service initialized.")

    # --- Blueprint Registration ---
    app.register_blueprint(meshnet_bp, url_prefix='/api/meshnet')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/chat', methods=['POST'])
    def handle_chat():
        user_command = request.json.get('command')
        user_id = request.json.get('user_id', 'anonymous')
        session_id = request.json.get('session_id', 'default')
        
        if not user_command:
            return jsonify({'response': 'No command provided'}), 400

        logger.info(f"Processing command: '{user_command}'")

        # Process command with enhanced Eliza agent
        eliza_response = current_app.eliza_agent.process_command(
            user_command, user_id=user_id, session_id=session_id
        )

        return jsonify({'response': eliza_response})

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
        """Provides a comprehensive dashboard of system metrics and service statuses."""
        try:
            dashboard_data = {
                'mining_status': current_app.mining_service.get_status(),
                'meshnet_status': current_app.meshnet_service.get_mesh_network_health(),
                'eliza_status': current_app.eliza_agent.get_agent_status(),
                'memory_stats': current_app.memory_service.get_memory_stats(),
                'autonomy_status': current_app.autonomy_service.get_autonomy_status(),
                'timestamp': datetime.now().isoformat()
            }
            return jsonify(dashboard_data)
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
    def get_autonomy_tasks():
        """Get current and historical autonomy tasks."""
        try:
            tasks = current_app.autonomy_service.get_autonomy_tasks()
            return jsonify({'success': True, 'data': tasks})
        except Exception as e:
            logger.error(f"Error fetching autonomy tasks: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/autonomy/execute', methods=['POST'])
    def execute_autonomy_task():
        """Manually trigger an autonomy task."""
        task_name = request.json.get('task_name')
        if not task_name:
            return jsonify({'success': False, 'error': 'Task name not provided'}), 400
        try:
            result = current_app.autonomy_service.execute_task(task_name)
            return jsonify({'success': True, 'data': result})
        except Exception as e:
            logger.error(f"Error executing autonomy task {task_name}: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/memory/search', methods=['POST'])
    def search_memory():
        """Search Eliza's memory for specific information."""
        query = request.json.get('query')
        user_id = request.json.get('user_id')
        session_id = request.json.get('session_id')
        limit = request.json.get('limit', 10)

        if not query:
            return jsonify({'success': False, 'error': 'Search query not provided'}), 400

        try:
            results = current_app.memory_service.search_memories(query, user_id, session_id, limit)
            return jsonify({'success': True, 'data': [mem.to_dict() for mem in results]})
        except Exception as e:
            logger.error(f"Error searching memory: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/memory/add', methods=['POST'])
    def add_memory_entry():
        """Add a new memory entry to Eliza's memory."""
        content = request.json.get('content')
        context = request.json.get('context')
        importance = request.json.get('importance', 5)
        tags = request.json.get('tags', [])
        user_id = request.json.get('user_id')
        session_id = request.json.get('session_id')
        category = request.json.get('category')

        if not content or not context:
            return jsonify({'success': False, 'error': 'Content and context are required'}), 400

        try:
            mem_id = current_app.memory_service.add_memory(content, context, importance, tags, user_id, session_id, category)
            return jsonify({'success': True, 'memory_id': mem_id})
        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/memory/conversation', methods=['POST'])
    def add_conversation_entry():
        """Add an entry to the conversation context."""
        entry = request.json.get('entry')
        if not entry:
            return jsonify({'success': False, 'error': 'Conversation entry not provided'}), 400
        try:
            current_app.memory_service.add_to_conversation_context(entry)
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error adding conversation entry: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/memory/profile', methods=['POST'])
    def update_user_profile():
        """Update or create a user profile."""
        user_id = request.json.get('user_id')
        profile_data = request.json.get('profile_data')
        if not user_id or not profile_data:
            return jsonify({'success': False, 'error': 'User ID and profile data are required'}), 400
        try:
            current_app.memory_service.update_user_profile(user_id, profile_data)
            return jsonify({'success': True})
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    # New XMRT-specific endpoints
    @app.route('/api/xmrt/knowledge', methods=['GET'])
    def get_xmrt_knowledge():
        """Get XMRT DAO knowledge by topic."""
        topic = request.args.get('topic')
        try:
            knowledge = current_app.memory_service.get_xmrt_knowledge(topic)
            return jsonify({'success': True, 'data': knowledge})
        except Exception as e:
            logger.error(f"Error fetching XMRT knowledge: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/xmrt/ask', methods=['POST'])
    def ask_xmrt_question():
        """Ask a question about XMRT DAO."""
        question = request.json.get('question')
        if not question:
            return jsonify({'success': False, 'error': 'Question not provided'}), 400
        
        try:
            answer = current_app.memory_service.answer_xmrt_question(question)
            return jsonify({'success': True, 'answer': answer})
        except Exception as e:
            logger.error(f"Error answering XMRT question: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/xmrt/reload-knowledge', methods=['POST'])
    def reload_xmrt_knowledge():
        """Reload the XMRT knowledgebase."""
        try:
            current_app.memory_service.reload_knowledgebase()
            return jsonify({'success': True, 'message': 'XMRT knowledgebase reloaded successfully'})
        except Exception as e:
            logger.error(f"Error reloading XMRT knowledgebase: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/api/agent/conversation-summary', methods=['GET'])
    def get_conversation_summary():
        """Get conversation summary for a user/session."""
        user_id = request.args.get('user_id')
        session_id = request.args.get('session_id')
        
        try:
            summary = current_app.eliza_agent.get_conversation_summary(user_id, session_id)
            return jsonify({'success': True, 'summary': summary})
        except Exception as e:
            logger.error(f"Error getting conversation summary: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

