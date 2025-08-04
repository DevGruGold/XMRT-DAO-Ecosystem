"""
XMRT-DAO-Ecosystem Main Flask Application
Enhanced with comprehensive MESHNET integration via Meshtastic
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import logging
import asyncio
from datetime import datetime
import os

# Import services
from services.mining_service import EnhancedSupportXMRService
from src.services.meshnet_service import MESHNETService
from src.api.meshnet_routes import meshnet_bp, init_meshnet_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    CORS(app)

    # Configuration
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-secret-key'),
        'XMRT_TOKEN_ADDRESS': '0x77307DFbc436224d5e6f2048d2b6bDfA66998a15',
        'XMRT_IP_NFT_ADDRESS': '0x9d691fc136a846d7442d1321a2d1b6aaef494eda',
        'MINING_WALLET': '46UxNFuGM2E3UwmZWWJicaRPoRwqwW4byQkaTHkX8yPcVihp91qAVtSFipWUGJJUyTXgzSqxDQtNLf2bsp2DX2qCCgC5mg',
        'SUPPORTXMR_API': 'https://supportxmr.com/api'
    })

    # Initialize services
    mining_service = MiningService({
        'mining_wallet': app.config['MINING_WALLET'],
        'api_url': app.config['SUPPORTXMR_API']
    })

    # Initialize MESHNET service
    meshnet_config = {
        'mesh_port': os.environ.get('MESH_PORT', 'simulate'),
        'update_interval': int(os.environ.get('MESH_UPDATE_INTERVAL', '30'))
    }
    meshnet_service = init_meshnet_service(meshnet_config)

    # Initialize MESHNET in the background
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(meshnet_service.initialize_mesh_interface())
        loop.run_until_complete(meshnet_service.integrate_mining_participants())
        loop.close()
        logger.info("✅ MESHNET service initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize MESHNET: {e}")

    # Register blueprints
    app.register_blueprint(meshnet_bp)

    @app.route('/')
    def home():
        """Home page with XMRT-DAO-Ecosystem overview"""
        return jsonify({
            'name': 'XMRT-DAO-Ecosystem',
            'version': '2.0.0',
            'description': 'Advanced DAO Ecosystem with MESHNET Integration',
            'features': [
                'SupportXMR Mining Integration',
                'Meshtastic MESHNET Connectivity',
                'Enhanced Mining Leaderboard',
                'Participant Verification System',
                'Real-time Network Monitoring',
                'Cross-chain Compatibility'
            ],
            'contracts': {
                'xmrt_token': app.config['XMRT_TOKEN_ADDRESS'],
                'xmrt_ip_nft': app.config['XMRT_IP_NFT_ADDRESS']
            },
            'apis': {
                'mining': '/api/mining/',
                'meshnet': '/api/meshnet/',
                'health': '/health'
            },
            'timestamp': datetime.now().isoformat()
        })

    @app.route('/health')
    def health_check():
        """Comprehensive health check"""
        try:
            # Check mining service
            mining_healthy = True
            try:
                mining_data = mining_service.get_mining_stats()
                mining_status = "operational"
            except Exception as e:
                mining_healthy = False
                mining_status = f"error: {str(e)}"

            # Check MESHNET service
            meshnet_healthy = True
            try:
                meshnet_status = meshnet_service.get_mesh_network_status()
                meshnet_status_msg = f"{meshnet_status['network_health']} - {meshnet_status['total_nodes']} nodes"
            except Exception as e:
                meshnet_healthy = False
                meshnet_status_msg = f"error: {str(e)}"

            overall_healthy = mining_healthy and meshnet_healthy

            return jsonify({
                'healthy': overall_healthy,
                'status': 'operational' if overall_healthy else 'degraded',
                'services': {
                    'mining': {
                        'healthy': mining_healthy,
                        'status': mining_status
                    },
                    'meshnet': {
                        'healthy': meshnet_healthy,
                        'status': meshnet_status_msg
                    }
                },
                'timestamp': datetime.now().isoformat()
            }), 200 if overall_healthy else 503

        except Exception as e:
            return jsonify({
                'healthy': False,
                'status': f'health check failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }), 500

    @app.route('/api/status')
    def get_system_status():
        """Get comprehensive system status"""
        try:
            # Get mining stats
            mining_stats = mining_service.get_mining_stats()

            # Get MESHNET status
            meshnet_status = meshnet_service.get_mesh_network_status()

            # Get enhanced leaderboard
            leaderboard = meshnet_service.get_enhanced_leaderboard()

            return jsonify({
                'success': True,
                'data': {
                    'mining': mining_stats,
                    'meshnet': meshnet_status,
                    'leaderboard_preview': leaderboard[:5],  # Top 5 miners
                    'system_info': {
                        'xmrt_token': app.config['XMRT_TOKEN_ADDRESS'],
                        'xmrt_ip_nft': app.config['XMRT_IP_NFT_ADDRESS'],
                        'mining_wallet': app.config['MINING_WALLET'],
                        'mesh_connectivity_bonus': '10%'
                    }
                },
                'timestamp': datetime.now().isoformat()
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    @app.route('/api/mining/stats')  
    def get_mining_stats():
        """Get current mining statistics"""
        try:
            stats = mining_service.get_mining_stats()
            return jsonify({
                'success': True,
                'data': stats,
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/mining/leaderboard')
    def get_mining_leaderboard():
        """Get enhanced mining leaderboard with MESHNET connectivity"""
        try:
            leaderboard = meshnet_service.get_enhanced_leaderboard()
            return jsonify({
                'success': True,
                'data': {
                    'leaderboard': leaderboard,
                    'total_participants': len(leaderboard),
                    'mesh_connected': len([e for e in leaderboard if e['mesh_connected']]),
                    'efficiency_bonus': '10% for MESHNET connectivity'
                },
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint not found',
            'available_endpoints': [
                '/',
                '/health', 
                '/api/status',
                '/api/mining/stats',
                '/api/mining/leaderboard',
                '/api/meshnet/status',
                '/api/meshnet/leaderboard',
                '/api/meshnet/nodes',
                '/api/meshnet/health'
            ]
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal server error',
            'message': 'Please check the logs for more details'
        }), 500

    return app

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'

    logger.info(f"🚀 Starting XMRT-DAO-Ecosystem with MESHNET on port {port}")
    logger.info(f"🔗 XMRT Token: {app.config['XMRT_TOKEN_ADDRESS']}")
    logger.info(f"🎨 XMRT IP NFT: {app.config['XMRT_IP_NFT_ADDRESS']}")
    logger.info(f"⛏️  Mining Wallet: {app.config['MINING_WALLET']}")

    app.run(host='0.0.0.0', port=port, debug=debug)
