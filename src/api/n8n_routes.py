"""
N8N API Routes for XMRT DAO Ecosystem
Provides REST API endpoints for n8n workflow management and execution.
"""

import logging
import asyncio
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Create the n8n blueprint
n8n_bp = Blueprint('n8n', __name__)

def get_n8n_service():
    """Get the n8n service from the current app context."""
    return getattr(current_app, 'n8n_service', None)

@n8n_bp.route('/status', methods=['GET'])
def get_n8n_status():
    """Get the status of the n8n service."""
    try:
        n8n_service = get_n8n_service()
        if not n8n_service:
            return jsonify({
                'success': False,
                'error': 'N8N service not available'
            }), 503
        
        status = asyncio.run(n8n_service.get_service_status())
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        logger.error(f"Error getting n8n status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@n8n_bp.route('/health', methods=['GET'])
def n8n_health_check():
    """Health check endpoint for n8n service."""
    try:
        n8n_service = get_n8n_service()
        if not n8n_service:
            return jsonify({
                'healthy': False,
                'status': 'service_unavailable',
                'timestamp': datetime.now().isoformat()
            }), 503
        
        status = asyncio.run(n8n_service.get_service_status())
        is_healthy = status.get('healthy', False)
        
        return jsonify({
            'healthy': is_healthy,
            'status': 'healthy' if is_healthy else 'unhealthy',
            'service': 'n8n',
            'timestamp': datetime.now().isoformat()
        }), 200 if is_healthy else 503
        
    except Exception as e:
        logger.error(f"N8N health check failed: {e}")
        return jsonify({
            'healthy': False,
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@n8n_bp.route('/workflows', methods=['GET'])
def list_workflows():
    """List all available workflows."""
    try:
        n8n_service = get_n8n_service()
        if not n8n_service:
            return jsonify({
                'success': False,
                'error': 'N8N service not available'
            }), 503
        
        workflows = asyncio.run(n8n_service.list_workflows())
        return jsonify({
            'success': True,
            'data': workflows,
            'count': len(workflows)
        })
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@n8n_bp.route('/workflows/<workflow_id>', methods=['GET'])
def get_workflow(workflow_id: str):
    """Get details of a specific workflow."""
    try:
        n8n_service = get_n8n_service()
        if not n8n_service:
            return jsonify({
                'success': False,
                'error': 'N8N service not available'
            }), 503
        
        if not workflow_id:
            return jsonify({
                'success': False,
                'error': 'Workflow ID is required'
            }), 400
        
        # Get workflow from local storage
        workflow = None
        if n8n_service.workflow_manager:
            workflow = asyncio.run(n8n_service.workflow_manager.get_workflow(workflow_id))
        
        if not workflow:
            return jsonify({
                'success': False,
                'error': 'Workflow not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'id': workflow.id,
                'name': workflow.name,
                'active': workflow.active,
                'nodes': workflow.nodes,
                'connections': workflow.connections,
                'settings': workflow.settings,
                'created_at': workflow.created_at.isoformat(),
                'updated_at': workflow.updated_at.isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error getting workflow {workflow_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@n8n_bp.route('/workflows/<workflow_id>/execute', methods=['POST'])
def execute_workflow(workflow_id: str):
    """Execute a specific workflow."""
    try:
        n8n_service = get_n8n_service()
        if not n8n_service:
            return jsonify({
                'success': False,
                'error': 'N8N service not available'
            }), 503
        
        if not workflow_id:
            return jsonify({
                'success': False,
                'error': 'Workflow ID is required'
            }), 400
        
        # Get input data from request
        data = request.get_json() or {}
        input_data = data.get('input_data', {})
        
        # Execute the workflow
        execution_id = asyncio.run(n8n_service.execute_workflow(workflow_id, input_data))
        
        if not execution_id:
            return jsonify({
                'success': False,
                'error': 'Failed to execute workflow'
            }), 500
        
        return jsonify({
            'success': True,
            'data': {
                'execution_id': execution_id,
                'workflow_id': workflow_id,
                'status': 'started',
                'started_at': datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error executing workflow {workflow_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@n8n_bp.route('/executions/<execution_id>', methods=['GET'])
def get_execution_status(execution_id: str):
    """Get the status of a workflow execution."""
    try:
        n8n_service = get_n8n_service()
        if not n8n_service:
            return jsonify({
                'success': False,
                'error': 'N8N service not available'
            }), 503
        
        if not execution_id:
            return jsonify({
                'success': False,
                'error': 'Execution ID is required'
            }), 400
        
        # Get execution status
        execution_status = asyncio.run(n8n_service.get_execution_status(execution_id))
        
        if not execution_status:
            return jsonify({
                'success': False,
                'error': 'Execution not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': execution_status
        })
    except Exception as e:
        logger.error(f"Error getting execution status {execution_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@n8n_bp.route('/executions', methods=['GET'])
def list_executions():
    """List recent workflow executions."""
    try:
        n8n_service = get_n8n_service()
        if not n8n_service:
            return jsonify({
                'success': False,
                'error': 'N8N service not available'
            }), 503
        
        # This would typically get executions from storage
        # For now, return empty list as placeholder
        executions = []
        
        return jsonify({
            'success': True,
            'data': executions,
            'count': len(executions)
        })
    except Exception as e:
        logger.error(f"Error listing executions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@n8n_bp.route('/capabilities', methods=['GET'])
def get_capabilities():
    """Get n8n service capabilities."""
    try:
        n8n_service = get_n8n_service()
        if not n8n_service:
            return jsonify({
                'success': False,
                'error': 'N8N service not available'
            }), 503
        
        capabilities = asyncio.run(n8n_service.get_workflow_capabilities())
        return jsonify({
            'success': True,
            'data': capabilities
        })
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@n8n_bp.route('/integration/demo', methods=['POST'])
def create_demo_workflow():
    """Create a demo workflow for XMRT integration."""
    try:
        n8n_service = get_n8n_service()
        if not n8n_service:
            return jsonify({
                'success': False,
                'error': 'N8N service not available'
            }), 503
        
        workflow_id = asyncio.run(n8n_service.create_xmrt_integration_workflow())
        
        if not workflow_id:
            return jsonify({
                'success': False,
                'error': 'Failed to create demo workflow'
            }), 500
        
        return jsonify({
            'success': True,
            'data': {
                'workflow_id': workflow_id,
                'name': 'XMRT Service Integration Demo',
                'description': 'Demonstrates integration between n8n and XMRT services',
                'created_at': datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error creating demo workflow: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Service integration endpoints for existing XMRT services
@n8n_bp.route('/services/mining/capabilities', methods=['GET'])
def get_mining_capabilities():
    """Get mining service capabilities for n8n integration."""
    try:
        return jsonify({
            'success': True,
            'data': {
                'service': 'mining',
                'endpoints': [
                    {
                        'path': '/api/dashboard',
                        'method': 'GET',
                        'description': 'Get mining dashboard data'
                    }
                ],
                'operations': [
                    'get_mining_status',
                    'get_hashrate',
                    'get_balance',
                    'get_pool_stats'
                ]
            }
        })
    except Exception as e:
        logger.error(f"Error getting mining capabilities: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@n8n_bp.route('/services/meshnet/capabilities', methods=['GET'])
def get_meshnet_capabilities():
    """Get meshnet service capabilities for n8n integration."""
    try:
        return jsonify({
            'success': True,
            'data': {
                'service': 'meshnet',
                'endpoints': [
                    {
                        'path': '/api/meshnet/status',
                        'method': 'GET',
                        'description': 'Get meshnet status'
                    },
                    {
                        'path': '/api/meshnet/peers',
                        'method': 'GET',
                        'description': 'Get connected peers'
                    }
                ],
                'operations': [
                    'get_network_status',
                    'get_peer_count',
                    'get_connection_quality'
                ]
            }
        })
    except Exception as e:
        logger.error(f"Error getting meshnet capabilities: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@n8n_bp.route('/services/agent/capabilities', methods=['GET'])
def get_agent_capabilities():
    """Get Eliza agent capabilities for n8n integration."""
    try:
        return jsonify({
            'success': True,
            'data': {
                'service': 'eliza_agent',
                'endpoints': [
                    {
                        'path': '/api/chat',
                        'method': 'POST',
                        'description': 'Send message to Eliza agent'
                    },
                    {
                        'path': '/api/agent/status',
                        'method': 'GET',
                        'description': 'Get agent status'
                    }
                ],
                'operations': [
                    'process_command',
                    'get_agent_status',
                    'get_capabilities'
                ]
            }
        })
    except Exception as e:
        logger.error(f"Error getting agent capabilities: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Error handlers for the blueprint
@n8n_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors for n8n routes."""
    return jsonify({
        'success': False,
        'error': 'N8N endpoint not found'
    }), 404

@n8n_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors for n8n routes."""
    logger.error(f"N8N API internal error: {error}")
    return jsonify({
        'success': False,
        'error': 'Internal server error in N8N API'
    }), 500

def init_n8n_service(config: Dict[str, Any]):
    """Initialize the n8n service with configuration."""
    try:
        from ..services.n8n_service import N8NService
        service = N8NService(config)
        logger.info("N8N service initialized for API routes")
        return service
    except Exception as e:
        logger.error(f"Failed to initialize n8n service: {e}")
        return None

