"""
MESHNET API Integration for XMRT-DAO-Ecosystem Flask App
Provides REST API endpoints for MESHNET functionality
"""

from flask import Blueprint, jsonify, request
import asyncio
import json
from datetime import datetime

# Import our MESHNET service
# from src.services.meshnet_service import MESHNETService

meshnet_bp = Blueprint('meshnet', __name__, url_prefix='/api/meshnet')

# Global MESHNET service instance
meshnet_service = None

def init_meshnet_service(config):
    """Initialize the global MESHNET service"""
    global meshnet_service
    meshnet_service = MESHNETService(config)
    return meshnet_service

@meshnet_bp.route('/status', methods=['GET'])
def get_meshnet_status():
    """Get current MESHNET status"""
    try:
        if not meshnet_service:
            return jsonify({
                'success': False,
                'error': 'MESHNET service not initialized'
            }), 500

        status = meshnet_service.get_mesh_network_status()
        return jsonify({
            'success': True,
            'data': status,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@meshnet_bp.route('/leaderboard', methods=['GET'])
def get_enhanced_leaderboard():
    """Get enhanced mining leaderboard with MESHNET connectivity"""
    try:
        if not meshnet_service:
            return jsonify({
                'success': False,
                'error': 'MESHNET service not initialized'
            }), 500

        leaderboard = meshnet_service.get_enhanced_leaderboard()

        # Add ranking
        for i, entry in enumerate(leaderboard, 1):
            entry['rank'] = i

        return jsonify({
            'success': True,
            'data': {
                'leaderboard': leaderboard,
                'total_participants': len(leaderboard),
                'mesh_connected': len([e for e in leaderboard if e['mesh_connected']]),
                'last_updated': datetime.now().isoformat()
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@meshnet_bp.route('/verify/<wallet_address>', methods=['POST'])
def verify_participant(wallet_address):
    """Verify a mining participant's MESHNET connectivity"""
    try:
        if not meshnet_service:
            return jsonify({
                'success': False,
                'error': 'MESHNET service not initialized'
            }), 500

        # Since we can't use async in Flask route directly, we'll simulate
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        result = loop.run_until_complete(
            meshnet_service.verify_participant_connectivity(wallet_address)
        )

        loop.close()

        return jsonify({
            'success': True,
            'data': result,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@meshnet_bp.route('/nodes', methods=['GET'])
def get_mesh_nodes():
    """Get all MESHNET nodes"""
    try:
        if not meshnet_service:
            return jsonify({
                'success': False,
                'error': 'MESHNET service not initialized'
            }), 500

        nodes_data = []
        for node_id, node in meshnet_service.nodes.items():
            nodes_data.append({
                'node_id': node.node_id,
                'user_id': node.user_id,
                'short_name': node.short_name,
                'long_name': node.long_name,
                'hardware_model': node.hardware_model,
                'last_seen': node.last_seen.isoformat(),
                'position': node.position,
                'signal_strength': node.rssi,
                'snr': node.snr,
                'is_mining': node.is_mining,
                'mining_hash_rate': node.mining_hash_rate,
                'xmr_earnings': node.xmr_earnings
            })

        return jsonify({
            'success': True,
            'data': {
                'nodes': nodes_data,
                'total_nodes': len(nodes_data),
                'mining_nodes': len([n for n in nodes_data if n['is_mining']]),
                'last_updated': datetime.now().isoformat()
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@meshnet_bp.route('/mining/stats', methods=['GET'])
def get_mining_meshnet_stats():
    """Get combined mining and MESHNET statistics"""
    try:
        if not meshnet_service:
            return jsonify({
                'success': False,
                'error': 'MESHNET service not initialized'
            }), 500

        # Get MESHNET status
        mesh_status = meshnet_service.get_mesh_network_status()

        # Calculate additional mining stats
        total_hash_rate = sum(m.hash_rate for m in meshnet_service.miners.values())
        total_xmr_earned = sum(m.xmr_earned for m in meshnet_service.miners.values())
        mesh_hash_rate = sum(m.hash_rate for m in meshnet_service.miners.values() if m.is_mesh_verified)

        stats = {
            'meshnet_status': mesh_status,
            'mining_stats': {
                'total_hash_rate': total_hash_rate,
                'mesh_hash_rate': mesh_hash_rate,
                'mesh_hash_percentage': (mesh_hash_rate / total_hash_rate * 100) if total_hash_rate > 0 else 0,
                'total_xmr_earned': total_xmr_earned,
                'mesh_efficiency_bonus': 1.1,  # 10% bonus for mesh connectivity
                'effective_hash_rate': mesh_hash_rate * 1.1 + (total_hash_rate - mesh_hash_rate)
            },
            'network_metrics': {
                'connectivity_score': mesh_status['mesh_connectivity_rate'],
                'network_resilience': 'High' if mesh_status['mesh_connectivity_rate'] > 70 else 'Medium' if mesh_status['mesh_connectivity_rate'] > 40 else 'Low',
                'decentralization_index': len([n for n in meshnet_service.nodes.values() if n.is_mining]) / max(1, len(meshnet_service.nodes))
            }
        }

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

@meshnet_bp.route('/initialize', methods=['POST'])
def initialize_meshnet():
    """Initialize or reinitialize MESHNET service"""
    try:
        data = request.get_json() or {}
        port = data.get('port', 'simulate')

        if not meshnet_service:
            return jsonify({
                'success': False,
                'error': 'MESHNET service not available'
            }), 500

        # Initialize in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(meshnet_service.initialize_mesh_interface(port))
        loop.run_until_complete(meshnet_service.integrate_mining_participants())

        loop.close()

        return jsonify({
            'success': True,
            'message': f'MESHNET initialized with port: {port}',
            'data': meshnet_service.get_mesh_network_status(),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Health check endpoint
@meshnet_bp.route('/health', methods=['GET'])
def meshnet_health():
    """MESHNET service health check"""
    try:
        if not meshnet_service:
            return jsonify({
                'healthy': False,
                'status': 'MESHNET service not initialized'
            }), 503

        status = meshnet_service.get_mesh_network_status()

        return jsonify({
            'healthy': True,
            'status': 'MESHNET service operational',
            'nodes': status['total_nodes'],
            'miners': status['total_miners'],
            'mesh_connectivity': f"{status['mesh_connectivity_rate']:.1f}%",
            'network_health': status['network_health'],
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'healthy': False,
            'status': f'MESHNET service error: {str(e)}'
        }), 500
