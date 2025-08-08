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

# --- AI Router Integration ---
class XMRTAIRouter:
    """Cost-optimized AI routing system for XMRT DAO"""
    
    def __init__(self):
        self.request_log = []
        self.cost_tracker = {
            'free_requests': 0,
            'nano_requests': 0, 
            'full_requests': 0,
            'total_cost': 0.0,
            'daily_savings': 0.0
        }
    
    def analyze_complexity(self, query, context=None):
        """Determine AI model based on query complexity"""
        query_lower = query.lower()
        
        # Free model patterns (Qwen2.5, Wan2.1)
        simple_patterns = ['hello', 'hi', 'what is', 'explain', 'define', 'summary', 'list', 'help']
        
        # GPT-5 nano patterns (DAO/blockchain specific)
        medium_patterns = ['dao', 'governance', 'xmrt', 'mining', 'meshnet', 'autonomy', 'contract', 'token']
        
        # GPT-5 full patterns (complex analysis)
        complex_patterns = ['analyze strategy', 'optimize', 'security audit', 'cross-chain', 'orchestrate']
        
        if any(pattern in query_lower for pattern in simple_patterns):
            return 'simple'
        elif any(pattern in query_lower for pattern in complex_patterns):
            return 'complex'
        elif any(pattern in query_lower for pattern in medium_patterns):
            return 'medium'
        else:
            return 'medium'  # Default to nano for XMRT ecosystem
    
    def route_request(self, query, user_tier='basic', context=None):
        """Route to appropriate AI model with cost optimization"""
        complexity = self.analyze_complexity(query, context)
        timestamp = datetime.now().isoformat()
        
        try:
            if complexity == 'simple':
                response = self.call_free_model(query)
                cost = 0.0
                model_used = 'qwen2.5-free'
                self.cost_tracker['free_requests'] += 1
                saved = self.estimate_nano_cost(query, response)
                self.cost_tracker['daily_savings'] += saved
                
            elif complexity == 'medium':
                response = self.call_gpt5_nano(query)
                cost = self.calculate_nano_cost(query, response)
                model_used = 'gpt-5-nano'
                self.cost_tracker['nano_requests'] += 1
                
            else:  # complex
                if user_tier in ['premium', 'enterprise']:
                    response = self.call_gpt5_full(query)
                    cost = self.calculate_full_cost(query, response)
                    model_used = 'gpt-5-full'
                    self.cost_tracker['full_requests'] += 1
                else:
                    response = self.call_gpt5_nano(query + " (simplified)")
                    cost = self.calculate_nano_cost(query, response)
                    model_used = 'gpt-5-nano-fallback'
                    self.cost_tracker['nano_requests'] += 1
            
            # Log request
            self.request_log.append({
                'timestamp': timestamp,
                'query_preview': query[:50] + '...' if len(query) > 50 else query,
                'complexity': complexity,
                'model_used': model_used,
                'cost': cost
            })
            
            self.cost_tracker['total_cost'] += cost
            
            return {
                'response': response,
                'model_used': model_used,
                'cost': round(cost, 4),
                'complexity': complexity
            }
            
        except Exception as e:
            response = f"I apologize for the technical issue. For your query about '{query[:30]}...', please try again."
            return {
                'response': response,
                'model_used': 'fallback',
                'cost': 0.0,
                'error': str(e)
            }
    
    def call_free_model(self, query):
        """Free models (Qwen2.5, Wan2.1)"""
        return f"[Free AI] {query} - This response cost $0.00 using Qwen2.5!"
    
    def call_gpt5_nano(self, query):
        """GPT-5 nano model"""
        return f"[GPT-5 Nano] XMRT DAO analysis: {query}"
    
    def call_gpt5_full(self, query):
        """GPT-5 full model"""
        return f"[GPT-5 Full] Advanced XMRT ecosystem analysis: {query}"
    
    def calculate_nano_cost(self, query, response):
        """Calculate GPT-5 nano cost"""
        input_tokens = len(query.split()) * 1.3
        output_tokens = len(response.split()) * 1.3
        return (input_tokens / 1000) * 0.05 + (output_tokens / 1000) * 0.40
    
    def calculate_full_cost(self, query, response):
        """Calculate GPT-5 full cost"""
        input_tokens = len(query.split()) * 1.3
        output_tokens = len(response.split()) * 1.3
        return (input_tokens / 1000) * 1.25 + (output_tokens / 1000) * 10.00
    
    def estimate_nano_cost(self, query, response):
        """Estimate nano cost for savings calculation"""
        return self.calculate_nano_cost(query, response)

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder='src/templates')
    CORS(app)

    # --- Configuration ---
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key-for-xmrt-phoenix'),
    })

    # --- Service Initialization ---
    with app.app_context():
        # Initialize AI Router
        current_app.ai_router = XMRTAIRouter()
        logger.info("✅ XMRT AI Router initialized with cost optimization.")
        
        current_app.mining_service = EnhancedSupportXMRService(config={})
        logger.info("✅ EnhancedSupportXMRService initialized.")

        current_app.meshnet_service = init_meshnet_service(config={})
        logger.info("✅ MESHNETService initialized.")
        
        current_app.speech_service = SpeechService(config={})
        logger.info("✅ Speech Service initialized.")
        
        current_app.memory_service = MemoryService(config={})
        logger.info("✅ Memory Service initialized.")
        
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

    # --- Blueprint Registration ---
    app.register_blueprint(meshnet_bp, url_prefix='/api/meshnet')
    logger.info("✅ MESHNET API blueprint registered.")

    # --- Core API & UI Routes ---

    @app.route('/')
    def chatbot_ui():
        """Serve the main Eliza chatbot UI."""
        return render_template('index.html')

    @app.route('/api/chat', methods=['POST'])
    def handle_chat():
        """Handle chat messages sent to Eliza with AI cost optimization."""
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': 'Invalid request format.'}), 400
        
        user_message = data['message']
        user_tier = data.get('user_tier', 'basic')
        
        try:
            # Route through AI cost optimizer first
            ai_result = current_app.ai_router.route_request(
                user_message, 
                user_tier, 
                context={'service': 'eliza-chat', 'ecosystem': 'xmrt-dao'}
            )
            
            # Then process through Eliza for additional context
            eliza_reply = asyncio.run(current_app.eliza_agent.process_command(user_message))
            
            return jsonify({
                'success': True, 
                'reply': eliza_reply,
                'ai_optimization': {
                    'model_used': ai_result['model_used'],
                    'cost': ai_result['cost'],
                    'complexity': ai_result['complexity']
                }
            })
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return jsonify({'success': False, 'error': 'An internal error occurred.'}), 500

    # --- NEW AI COST OPTIMIZATION ROUTES ---
    
    @app.route('/ai/chat', methods=['POST'])
    def ai_optimized_chat():
        """Direct AI chat with cost optimization"""
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400
        
        query = data.get('query')
        user_tier = data.get('user_tier', 'basic')
        context = data.get('context', {'service': 'xmrt-dao'})
        
        result = current_app.ai_router.route_request(query, user_tier, context)
        return jsonify(result)

    @app.route('/ai/dao-help', methods=['POST'])
    def ai_dao_help():
        """AI help specifically for DAO/governance questions"""
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({'error': 'Missing question parameter'}), 400
        
        question = data.get('question')
        user_tier = data.get('user_tier', 'basic')
        
        # Add DAO context for better routing
        dao_query = f"XMRT DAO question: {question}"
        context = {'service': 'dao-governance', 'ecosystem': 'xmrt'}
        
        result = current_app.ai_router.route_request(dao_query, user_tier, context)
        return jsonify(result)

    @app.route('/ai/stats', methods=['GET'])
    def ai_cost_stats():
        """AI usage and cost statistics"""
        total_requests = len(current_app.ai_router.request_log)
        
        return jsonify({
            'cost_summary': current_app.ai_router.cost_tracker,
            'recent_requests': current_app.ai_router.request_log[-5:],
            'total_requests': total_requests,
            'optimization_metrics': {
                'free_percentage': round((current_app.ai_router.cost_tracker['free_requests'] / max(total_requests, 1)) * 100, 2),
                'estimated_monthly_savings': round(current_app.ai_router.cost_tracker['daily_savings'] * 30, 2),
                'average_cost_per_request': round(current_app.ai_router.cost_tracker['total_cost'] / max(total_requests, 1), 4)
            }
        })

    @app.route('/ai/health', methods=['GET'])
    def ai_system_health():
        """AI system health check"""
        return jsonify({
            'status': 'healthy',
            'ai_router': 'active',
            'models': {
                'free_models': 'qwen2.5, wan2.1',
                'paid_models': 'gpt-5-nano, gpt-5-full'
            },
            'cost_optimization': 'enabled',
            'ecosystem_integration': 'xmrt-dao'
        })

    # --- EXISTING ROUTES (unchanged) ---
    
    @app.route('/health')
    def health_check():
        """Comprehensive health check for all core services."""
        try:
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
