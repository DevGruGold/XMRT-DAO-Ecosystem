"""
XMRT DAO Ecosystem - Enhanced Main Application

This is the enhanced Flask application that serves as the entry point for the
XMRT DAO Ecosystem, providing comprehensive web interfaces and API endpoints for:
- Smart contract interactions (XMRT Token)
- Treasury management with AI decision making
- Mining pool integration (MobileMonero.com)
- DAO governance system
- Real-time WebSocket updates
- Monitoring and analytics

Enhanced with full ecosystem integration based on comprehensive documentation.
"""

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import asyncio
import logging
import json
from datetime import datetime
import os
import sys
from threading import Thread
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.orchestrator import XMRTOrchestrator
from agents.eliza_agent import ElizaAgent
from services.github_service import GitHubService
from services.redis_service import RedisService
from services.raglight_service import RAGlightService
from services.web3_service import Web3Service
from services.treasury_service import TreasuryManager
from services.mining_service import MiningPoolService
from services.governance_service import GovernanceService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'xmrt-dao-secret-key-2025')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration
config = {
    # Network configuration
    'default_network': 'sepolia',
    'sepolia_rpc_url': os.getenv('SEPOLIA_RPC_URL', ''),
    'mainnet_rpc_url': os.getenv('MAINNET_RPC_URL', ''),

    # Treasury configuration
    'treasury_allocation': {
        'eth': 0.30, 'xmr': 0.25, 'usdc': 0.35, 'xmrt': 0.10
    },
    'treasury_address': os.getenv('TREASURY_ADDRESS', ''),

    # Mining configuration
    'mobilemonero_api_url': 'https://api.mobilemonero.com/v1',
    'mobilemonero_api_key': os.getenv('MOBILEMONERO_API_KEY', ''),
    'xmrt_pool_address': os.getenv('XMRT_POOL_ADDRESS', ''),
    'expected_weekly_xmr': 2.3,

    # Governance configuration
    'ai_analysis_enabled': True,
    'voting_period_blocks': 45818,  # ~1 week
    'quorum_fraction': 4,  # 4%

    # Service configuration
    'github_token': os.getenv('GITHUB_TOKEN', ''),
    'github_username': os.getenv('GITHUB_USERNAME', 'DevGruGold'),
    'github_email': os.getenv('GITHUB_EMAIL', 'joeyleepcs@gmail.com'),
    'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
    'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379/0')
}

# Global service instances
services = {}
orchestrator = None
eliza_agent = None

def initialize_services():
    """Initialize all ecosystem services"""
    global services, orchestrator, eliza_agent

    try:
        logger.info("Initializing XMRT DAO Ecosystem services...")

        # Initialize Redis Service
        services['redis'] = RedisService(
            host='localhost',
            port=6379,
            password=os.getenv('REDIS_PASSWORD'),
            ssl=os.getenv('REDIS_SSL', 'false').lower() == 'true'
        )

        # Initialize Web3 Service
        services['web3'] = Web3Service(config)

        # Initialize Treasury Manager
        services['treasury'] = TreasuryManager(
            config, 
            redis_service=services['redis'],
            web3_service=services['web3']
        )

        # Initialize Mining Pool Service
        services['mining'] = MiningPoolService(
            config,
            redis_service=services['redis']
        )

        # Initialize Governance Service
        services['governance'] = GovernanceService(
            config,
            web3_service=services['web3'],
            redis_service=services['redis']
        )

        # Initialize GitHub Service
        services['github'] = GitHubService({
            'github_token': config['github_token'],
            'github_username': config['github_username'],
            'github_email': config['github_email']
        })

        # Initialize RAGlight Service
        services['raglight'] = RAGlightService()

        # Initialize Orchestrator
        orchestrator = XMRTOrchestrator(config)

        # Initialize Eliza Agent
        eliza_agent = ElizaAgent(
            config,
            github_service=services['github'],
            redis_service=services['redis'],
            raglight_service=services['raglight']
        )

        logger.info("✅ All services initialized successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        return False

# HTML Templates for web interface
dashboard_template = """
<!DOCTYPE html>
<html>
<head>
    <title>XMRT DAO Ecosystem Dashboard</title>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #0a0e1a; color: #e0e0e0; }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: #4a9eff; margin: 0; }
        .header p { color: #888; }
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: #1a1f2e; border: 1px solid #2d3748; border-radius: 8px; padding: 20px; }
        .card h3 { color: #4a9eff; margin-top: 0; }
        .metric { display: flex; justify-content: space-between; margin: 10px 0; }
        .status { padding: 4px 8px; border-radius: 4px; font-size: 12px; }
        .status.online { background: #22c55e; color: white; }
        .status.offline { background: #ef4444; color: white; }
        .btn { background: #4a9eff; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #3b82f6; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 XMRT DAO Ecosystem</h1>
        <p>Autonomous Decentralized Organization with AI-Powered Decision Making</p>
    </div>

    <div class="dashboard">
        <div class="card">
            <h3>🏦 Treasury Status</h3>
            <div id="treasury-data">Loading...</div>
        </div>

        <div class="card">
            <h3>⛏️ Mining Operations</h3>
            <div id="mining-data">Loading...</div>
        </div>

        <div class="card">
            <h3>🗳️ Governance</h3>
            <div id="governance-data">Loading...</div>
        </div>

        <div class="card">
            <h3>🤖 AI Agent Status</h3>
            <div id="agent-data">Loading...</div>
        </div>

        <div class="card">
            <h3>📊 Network Status</h3>
            <div id="network-data">Loading...</div>
        </div>

        <div class="card">
            <h3>🔧 System Controls</h3>
            <button class="btn" onclick="startOrchestrator()">Start Orchestrator</button>
            <button class="btn" onclick="activateEliza()">Activate Eliza</button>
            <button class="btn" onclick="refreshDashboard()">Refresh Data</button>
        </div>
    </div>

    <script>
        const socket = io();

        function updateDashboard() {
            fetch('/api/v1/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('treasury-data').innerHTML = formatTreasuryData(data.treasury);
                    document.getElementById('mining-data').innerHTML = formatMiningData(data.mining);
                    document.getElementById('governance-data').innerHTML = formatGovernanceData(data.governance);
                    document.getElementById('agent-data').innerHTML = formatAgentData(data.agent_status);
                    document.getElementById('network-data').innerHTML = formatNetworkData(data.network);
                });
        }

        function formatTreasuryData(data) {
            if (!data) return 'Service unavailable';
            return `
                <div class="metric"><span>Total Value:</span><span>$${(data.total_value_usd || 0).toLocaleString()}</span></div>
                <div class="metric"><span>ETH:</span><span>${(data.balances?.eth || 0)} ETH</span></div>
                <div class="metric"><span>XMR:</span><span>${(data.balances?.xmr || 0)} XMR</span></div>
                <div class="metric"><span>USDC:</span><span>${(data.balances?.usdc || 0).toLocaleString()} USDC</span></div>
                <div class="metric"><span>XMRT:</span><span>${(data.balances?.xmrt || 0)} XMRT</span></div>
            `;
        }

        function formatMiningData(data) {
            if (!data) return 'Service unavailable';
            return `
                <div class="metric"><span>Hashrate:</span><span>${((data.miner_data?.hashrate_current || 0) / 1000000).toFixed(1)} MH/s</span></div>
                <div class="metric"><span>Daily Revenue:</span><span>${(data.performance_metrics?.actual_daily_revenue || 0).toFixed(3)} XMR</span></div>
                <div class="metric"><span>Efficiency:</span><span>${(data.performance_metrics?.hashrate_efficiency || 0).toFixed(1)}%</span></div>
                <div class="metric"><span>Health:</span><span class="status ${data.health_status?.status === 'excellent' ? 'online' : 'offline'}">${data.health_status?.status || 'unknown'}</span></div>
            `;
        }

        function formatGovernanceData(data) {
            if (!data) return 'Service unavailable';
            return `
                <div class="metric"><span>Total Proposals:</span><span>${data.total_proposals || 0}</span></div>
                <div class="metric"><span>Active Proposals:</span><span>${data.active_proposals || 0}</span></div>
                <div class="metric"><span>Participation:</span><span>${((data.participation_rate || 0) * 100).toFixed(1)}%</span></div>
                <div class="metric"><span>Efficiency:</span><span>${((data.governance_efficiency || 0) * 100).toFixed(1)}%</span></div>
            `;
        }

        function formatAgentData(data) {
            if (!data) return 'Service unavailable';
            return `
                <div class="metric"><span>Status:</span><span class="status ${data.active ? 'online' : 'offline'}">${data.active ? 'Active' : 'Inactive'}</span></div>
                <div class="metric"><span>Decisions Made:</span><span>${data.decisions_made || 0}</span></div>
                <div class="metric"><span>Accuracy:</span><span>${((data.decision_accuracy || 0) * 100).toFixed(1)}%</span></div>
            `;
        }

        function formatNetworkData(data) {
            if (!data) return 'Service unavailable';
            return `
                <div class="metric"><span>Network:</span><span>${data.network || 'Unknown'}</span></div>
                <div class="metric"><span>Connected:</span><span class="status ${data.connected ? 'online' : 'offline'}">${data.connected ? 'Yes' : 'No'}</span></div>
                <div class="metric"><span>Latest Block:</span><span>${(data.latest_block || 0).toLocaleString()}</span></div>
                <div class="metric"><span>Gas Price:</span><span>${data.gas_price_gwei || 0} Gwei</span></div>
            `;
        }

        function startOrchestrator() {
            fetch('/api/v1/orchestrator/start', {method: 'POST'})
                .then(response => response.json())
                .then(data => alert(JSON.stringify(data)));
        }

        function activateEliza() {
            fetch('/api/v1/eliza/activate', {method: 'POST'})
                .then(response => response.json())
                .then(data => alert(JSON.stringify(data)));
        }

        function refreshDashboard() {
            updateDashboard();
        }

        // Auto-refresh dashboard
        setInterval(updateDashboard, 30000); // Every 30 seconds
        updateDashboard(); // Initial load

        // Socket.io real-time updates
        socket.on('treasury_update', function(data) {
            console.log('Treasury update:', data);
            updateDashboard();
        });

        socket.on('mining_update', function(data) {
            console.log('Mining update:', data);
            updateDashboard();
        });

        socket.on('governance_update', function(data) {
            console.log('Governance update:', data);
            updateDashboard();
        });
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def home():
    """Dashboard home page"""
    return render_template_string(dashboard_template)

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'web3': services.get('web3') is not None,
                'treasury': services.get('treasury') is not None,
                'mining': services.get('mining') is not None,
                'governance': services.get('governance') is not None,
                'redis': services.get('redis') is not None,
                'orchestrator': orchestrator is not None,
                'eliza': eliza_agent is not None
            }
        }
        return jsonify(health_status)
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/v1/status')
async def get_comprehensive_status():
    """Get comprehensive system status"""
    try:
        status = {
            'timestamp': datetime.utcnow().isoformat(),
            'network': services['web3'].get_network_status() if services.get('web3') else None,
            'treasury': await services['treasury'].get_treasury_status() if services.get('treasury') else None,
            'mining': await services['mining'].get_mining_stats() if services.get('mining') else None,
            'governance': await services['governance'].get_governance_metrics() if services.get('governance') else None,
            'agent_status': {
                'active': eliza_agent.is_active() if eliza_agent else False,
                'decisions_made': getattr(eliza_agent, 'decisions_made', 0) if eliza_agent else 0,
                'decision_accuracy': 0.89  # From documentation
            },
            'orchestrator_status': {
                'running': orchestrator.is_running() if orchestrator else False,
                'cycle_count': getattr(orchestrator, 'cycle_count', 0) if orchestrator else 0
            }
        }
        return jsonify(status)
    except Exception as e:
        logger.error(f"Status endpoint error: {e}")
        return jsonify({'error': str(e)}), 500

# Treasury API Endpoints
@app.route('/api/v1/treasury/status')
async def treasury_status():
    """Get treasury status"""
    try:
        if not services.get('treasury'):
            return jsonify({'error': 'Treasury service not available'}), 503

        status = await services['treasury'].get_treasury_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/treasury/rebalance/evaluate', methods=['POST'])
async def evaluate_rebalancing():
    """Evaluate treasury rebalancing with AI"""
    try:
        if not services.get('treasury'):
            return jsonify({'error': 'Treasury service not available'}), 503

        decision = await services['treasury'].evaluate_rebalancing_decision()
        return jsonify(decision)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Mining API Endpoints
@app.route('/api/v1/mining/stats')
async def mining_stats():
    """Get mining statistics"""
    try:
        if not services.get('mining'):
            return jsonify({'error': 'Mining service not available'}), 503

        stats = await services['mining'].get_mining_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/mining/alerts')
async def mining_alerts():
    """Get mining alerts"""
    try:
        if not services.get('mining'):
            return jsonify({'error': 'Mining service not available'}), 503

        alerts = await services['mining'].get_mining_alerts()
        return jsonify({'alerts': alerts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Governance API Endpoints
@app.route('/api/v1/governance/proposals', methods=['GET', 'POST'])
async def governance_proposals():
    """Handle governance proposals"""
    try:
        if not services.get('governance'):
            return jsonify({'error': 'Governance service not available'}), 503

        if request.method == 'POST':
            data = request.get_json()
            result = await services['governance'].create_proposal(
                proposer=data['proposer'],
                title=data['title'],
                description=data['description'],
                targets=data.get('targets', []),
                values=data.get('values', []),
                calldatas=data.get('calldatas', [])
            )
            return jsonify(result)
        else:
            status_filter = request.args.get('status')
            limit = int(request.args.get('limit', 50))
            proposals = await services['governance'].get_all_proposals(status_filter, limit)
            return jsonify({'proposals': proposals})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/governance/proposals/<proposal_id>')
async def get_proposal(proposal_id):
    """Get specific proposal"""
    try:
        if not services.get('governance'):
            return jsonify({'error': 'Governance service not available'}), 503

        proposal = await services['governance'].get_proposal(proposal_id)
        return jsonify(proposal)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/governance/vote', methods=['POST'])
async def cast_vote():
    """Cast a vote on a proposal"""
    try:
        if not services.get('governance'):
            return jsonify({'error': 'Governance service not available'}), 503

        data = request.get_json()
        result = await services['governance'].cast_vote(
            voter=data['voter'],
            proposal_id=data['proposal_id'],
            support=data['support'],
            reason=data.get('reason', '')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Web3 API Endpoints
@app.route('/api/v1/token/info')
async def token_info():
    """Get XMRT token information"""
    try:
        if not services.get('web3'):
            return jsonify({'error': 'Web3 service not available'}), 503

        info = await services['web3'].get_token_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/token/balance/<address>')
async def token_balance(address):
    """Get XMRT token balance for address"""
    try:
        if not services.get('web3'):
            return jsonify({'error': 'Web3 service not available'}), 503

        balance = await services['web3'].get_balance(address)
        return jsonify(balance)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Agent Control Endpoints
@app.route('/api/v1/eliza/activate', methods=['POST'])
def activate_eliza():
    """Activate Eliza agent"""
    try:
        if not eliza_agent:
            return jsonify({'error': 'Eliza agent not available'}), 503

        result = eliza_agent.activate()
        return jsonify({'status': 'activated', 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/eliza/deactivate', methods=['POST'])
def deactivate_eliza():
    """Deactivate Eliza agent"""
    try:
        if not eliza_agent:
            return jsonify({'error': 'Eliza agent not available'}), 503

        result = eliza_agent.deactivate()
        return jsonify({'status': 'deactivated', 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/orchestrator/start', methods=['POST'])
def start_orchestrator():
    """Start orchestrator"""
    try:
        if not orchestrator:
            return jsonify({'error': 'Orchestrator not available'}), 503

        result = orchestrator.start()
        return jsonify({'status': 'started', 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/orchestrator/stop', methods=['POST'])
def stop_orchestrator():
    """Stop orchestrator"""
    try:
        if not orchestrator:
            return jsonify({'error': 'Orchestrator not available'}), 503

        result = orchestrator.stop()
        return jsonify({'status': 'stopped', 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('status', {'message': 'Connected to XMRT DAO Ecosystem'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

def background_task():
    """Background task to emit real-time updates"""
    while True:
        try:
            # Emit periodic updates
            socketio.emit('treasury_update', {'timestamp': datetime.utcnow().isoformat()})
            socketio.emit('mining_update', {'timestamp': datetime.utcnow().isoformat()})
            socketio.emit('governance_update', {'timestamp': datetime.utcnow().isoformat()})
            time.sleep(30)  # Every 30 seconds
        except Exception as e:
            logger.error(f"Background task error: {e}")
            time.sleep(60)

if __name__ == '__main__':
    print("🚀 XMRT DAO Ecosystem - Enhanced Application")
    print("=" * 60)

    # Initialize services
    if initialize_services():
        print("✅ All services initialized successfully")

        # Start background task
        background_thread = Thread(target=background_task)
        background_thread.daemon = True
        background_thread.start()

        print("🌐 Starting web server...")
        print("📊 Dashboard: http://localhost:5000")
        print("🔗 API Base: http://localhost:5000/api/v1")
        print("=" * 60)

        socketio.run(app, debug=False, host='0.0.0.0', port=5000)
    else:
        print("❌ Failed to initialize services. Exiting.")
        sys.exit(1)
