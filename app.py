"""
XMRT DAO Ecosystem - Main Application

This is the main Flask application that serves as the entry point for the
XMRT DAO Ecosystem, providing web interfaces and API endpoints for
interacting with the autonomous Eliza agent and orchestrator.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import asyncio
import logging
from datetime import datetime
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.orchestrator import XMRTOrchestrator
from agents.eliza_agent import ElizaAgent
from services.github_service import GitHubService

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
orchestrator = None
eliza_agent = None
github_service = None

def create_config():
    """Create configuration for the ecosystem."""
    return {
        'cycle_interval': 300,  # 5 minutes
        'agent_cycle_interval': 60,  # 1 minute
        'max_applications': 10,
        'github_token': os.getenv('GITHUB_TOKEN'),
        'github_username': os.getenv('GITHUB_USERNAME', 'DevGruGold'),
        'github_email': os.getenv('GITHUB_EMAIL', 'joeyleepcs@gmail.com'),
        'github_access': {
            'enabled': True,
            'auto_commit': True,
            'auto_deploy': True
        }
    }

@app.route('/')
def home():
    """Home endpoint."""
    return jsonify({
        "message": "XMRT DAO Ecosystem - Initial Framework",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "description": "Autonomous Eliza AI for XMRT DAO with self-improvement capabilities"
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    global orchestrator, eliza_agent, github_service
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "orchestrator": {
                "initialized": orchestrator is not None,
                "running": orchestrator.is_running if orchestrator else False
            },
            "eliza_agent": {
                "initialized": eliza_agent is not None,
                "active": eliza_agent.is_active if eliza_agent else False
            },
            "github_service": {
                "initialized": github_service is not None,
                "authenticated": github_service.user is not None if github_service else False
            }
        }
    }
    
    return jsonify(health_status)

@app.route('/status')
def status():
    """Get detailed status of all components."""
    global orchestrator, eliza_agent, github_service
    
    status_data = {
        "timestamp": datetime.now().isoformat(),
        "orchestrator": orchestrator.get_status() if orchestrator else None,
        "eliza_agent": eliza_agent.get_status() if eliza_agent else None,
        "github_service": github_service.get_status() if github_service else None
    }
    
    return jsonify(status_data)

@app.route('/eliza/applications')
def eliza_applications():
    """Get applications created by Eliza."""
    global eliza_agent
    
    if not eliza_agent:
        return jsonify({"error": "Eliza agent not initialized"}), 500
    
    applications = eliza_agent.get_created_applications()
    return jsonify({
        "applications": applications,
        "count": len(applications),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/orchestrator/start', methods=['POST'])
def start_orchestrator():
    """Start the orchestrator."""
    global orchestrator
    
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized"}), 500
    
    if orchestrator.is_running:
        return jsonify({"message": "Orchestrator already running"})
    
    # Start orchestrator in background
    asyncio.create_task(orchestrator.start())
    
    return jsonify({
        "message": "Orchestrator started",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/orchestrator/stop', methods=['POST'])
def stop_orchestrator():
    """Stop the orchestrator."""
    global orchestrator
    
    if not orchestrator:
        return jsonify({"error": "Orchestrator not initialized"}), 500
    
    if not orchestrator.is_running:
        return jsonify({"message": "Orchestrator not running"})
    
    # Stop orchestrator
    asyncio.create_task(orchestrator.stop())
    
    return jsonify({
        "message": "Orchestrator stopped",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/eliza/activate', methods=['POST'])
def activate_eliza():
    """Activate Eliza agent."""
    global eliza_agent
    
    if not eliza_agent:
        return jsonify({"error": "Eliza agent not initialized"}), 500
    
    if eliza_agent.is_active:
        return jsonify({"message": "Eliza agent already active"})
    
    # Activate Eliza in background
    asyncio.create_task(eliza_agent.activate())
    
    return jsonify({
        "message": "Eliza agent activated",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/eliza/deactivate', methods=['POST'])
def deactivate_eliza():
    """Deactivate Eliza agent."""
    global eliza_agent
    
    if not eliza_agent:
        return jsonify({"error": "Eliza agent not initialized"}), 500
    
    if not eliza_agent.is_active:
        return jsonify({"message": "Eliza agent not active"})
    
    # Deactivate Eliza
    asyncio.create_task(eliza_agent.deactivate())
    
    return jsonify({
        "message": "Eliza agent deactivated",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/github/repositories')
def github_repositories():
    """Get list of GitHub repositories."""
    global github_service
    
    if not github_service:
        return jsonify({"error": "GitHub service not initialized"}), 500
    
    # This would need to be made async in a real implementation
    repos = []  # github_service.list_repositories() - would need async handling
    
    return jsonify({
        "repositories": repos,
        "count": len(repos),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/info')
def api_info():
    """Get API information."""
    return jsonify({
        "name": "XMRT DAO Ecosystem API",
        "version": "0.1.0",
        "description": "API for interacting with the autonomous XMRT DAO Ecosystem",
        "endpoints": {
            "/": "Home page",
            "/health": "Health check",
            "/status": "Detailed status",
            "/eliza/applications": "Eliza's created applications",
            "/orchestrator/start": "Start orchestrator (POST)",
            "/orchestrator/stop": "Stop orchestrator (POST)",
            "/eliza/activate": "Activate Eliza (POST)",
            "/eliza/deactivate": "Deactivate Eliza (POST)",
            "/github/repositories": "List GitHub repositories",
            "/api/info": "This endpoint"
        },
        "timestamp": datetime.now().isoformat()
    })

def initialize_components():
    """Initialize all ecosystem components."""
    global orchestrator, eliza_agent, github_service
    
    logger.info("Initializing XMRT DAO Ecosystem components")
    
    # Create configuration
    config = create_config()
    
    # Initialize GitHub service
    github_service = GitHubService(config)
    logger.info("GitHub service initialized")
    
    # Initialize Eliza agent
    eliza_agent = ElizaAgent(config)
    logger.info("Eliza agent initialized")
    
    # Initialize orchestrator
    orchestrator = XMRTOrchestrator(config)
    logger.info("Orchestrator initialized")
    
    # Register components with orchestrator
    orchestrator.register_agent('eliza', eliza_agent)
    orchestrator.register_service('github', github_service)
    
    logger.info("All components initialized successfully")

if __name__ == '__main__':
    # Initialize components
    initialize_components()
    
    # Start the Flask application
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

