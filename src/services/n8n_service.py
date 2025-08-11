"""
N8N Service for XMRT DAO Ecosystem
Provides workflow automation and orchestration capabilities using n8n.
"""

import os
import json
import logging
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class WorkflowDefinition:
    """Represents an n8n workflow definition."""
    id: str
    name: str
    active: bool
    nodes: List[Dict[str, Any]]
    connections: Dict[str, Any]
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class WorkflowExecution:
    """Represents a workflow execution."""
    id: str
    workflow_id: str
    status: str  # 'running', 'success', 'error', 'waiting'
    started_at: datetime
    finished_at: Optional[datetime]
    data: Dict[str, Any]
    error: Optional[str]

class N8NAPIClient:
    """Client for communicating with n8n API."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        if self.api_key:
            headers['X-N8N-API-KEY'] = self.api_key
        return headers
    
    async def get_workflows(self) -> List[Dict[str, Any]]:
        """Get all workflows from n8n."""
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/workflows",
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', [])
                else:
                    logger.error(f"Failed to get workflows: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error getting workflows: {e}")
            return []
    
    async def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific workflow by ID."""
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get workflow {workflow_id}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting workflow {workflow_id}: {e}")
            return None
    
    async def execute_workflow(self, workflow_id: str, data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Execute a workflow and return execution ID."""
        try:
            payload = {'workflowData': data} if data else {}
            async with self.session.post(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/execute",
                headers=self._get_headers(),
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('data', {}).get('executionId')
                else:
                    logger.error(f"Failed to execute workflow {workflow_id}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {e}")
            return None
    
    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution details by ID."""
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/executions/{execution_id}",
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get execution {execution_id}: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting execution {execution_id}: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Check if n8n is healthy."""
        try:
            async with self.session.get(
                f"{self.base_url}/healthz",
                headers=self._get_headers()
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"n8n health check failed: {e}")
            return False

class WorkflowManager:
    """Manages workflow definitions and executions."""
    
    def __init__(self, memory_service):
        self.memory_service = memory_service
        self.workflows_key = "n8n:workflows"
        self.executions_key = "n8n:executions"
    
    async def store_workflow(self, workflow: WorkflowDefinition) -> bool:
        """Store a workflow definition."""
        try:
            workflow_data = asdict(workflow)
            # Convert datetime objects to ISO strings for JSON serialization
            workflow_data['created_at'] = workflow.created_at.isoformat()
            workflow_data['updated_at'] = workflow.updated_at.isoformat()
            
            await self.memory_service.store_data(
                f"{self.workflows_key}:{workflow.id}",
                workflow_data
            )
            return True
        except Exception as e:
            logger.error(f"Error storing workflow {workflow.id}: {e}")
            return False
    
    async def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get a workflow definition by ID."""
        try:
            data = await self.memory_service.get_data(f"{self.workflows_key}:{workflow_id}")
            if data:
                # Convert ISO strings back to datetime objects
                data['created_at'] = datetime.fromisoformat(data['created_at'])
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])
                return WorkflowDefinition(**data)
            return None
        except Exception as e:
            logger.error(f"Error getting workflow {workflow_id}: {e}")
            return None
    
    async def list_workflows(self) -> List[WorkflowDefinition]:
        """List all stored workflows."""
        try:
            keys = await self.memory_service.get_keys_pattern(f"{self.workflows_key}:*")
            workflows = []
            for key in keys:
                data = await self.memory_service.get_data(key)
                if data:
                    data['created_at'] = datetime.fromisoformat(data['created_at'])
                    data['updated_at'] = datetime.fromisoformat(data['updated_at'])
                    workflows.append(WorkflowDefinition(**data))
            return workflows
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            return []
    
    async def store_execution(self, execution: WorkflowExecution) -> bool:
        """Store a workflow execution."""
        try:
            execution_data = asdict(execution)
            # Convert datetime objects to ISO strings
            execution_data['started_at'] = execution.started_at.isoformat()
            if execution.finished_at:
                execution_data['finished_at'] = execution.finished_at.isoformat()
            
            await self.memory_service.store_data(
                f"{self.executions_key}:{execution.id}",
                execution_data
            )
            return True
        except Exception as e:
            logger.error(f"Error storing execution {execution.id}: {e}")
            return False
    
    async def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get a workflow execution by ID."""
        try:
            data = await self.memory_service.get_data(f"{self.executions_key}:{execution_id}")
            if data:
                # Convert ISO strings back to datetime objects
                data['started_at'] = datetime.fromisoformat(data['started_at'])
                if data.get('finished_at'):
                    data['finished_at'] = datetime.fromisoformat(data['finished_at'])
                return WorkflowExecution(**data)
            return None
        except Exception as e:
            logger.error(f"Error getting execution {execution_id}: {e}")
            return None

class N8NService:
    """Main n8n service for workflow automation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.n8n_url = config.get('n8n_url', 'http://localhost:5678')
        self.api_key = config.get('n8n_api_key')
        self.memory_service = None
        self.workflow_manager = None
        self.api_client = None
        self.is_healthy = False
        
        logger.info(f"N8NService initialized with URL: {self.n8n_url}")
    
    def set_memory_service(self, memory_service):
        """Set the memory service for workflow storage."""
        self.memory_service = memory_service
        self.workflow_manager = WorkflowManager(memory_service)
        logger.info("Memory service connected to N8NService")
    
    async def initialize(self) -> bool:
        """Initialize the n8n service."""
        try:
            self.api_client = N8NAPIClient(self.n8n_url, self.api_key)
            await self.api_client.__aenter__()
            
            # Check n8n health
            self.is_healthy = await self.api_client.health_check()
            
            if self.is_healthy:
                logger.info("N8NService successfully initialized and connected to n8n")
                # Sync workflows from n8n to local storage
                await self._sync_workflows()
            else:
                logger.warning("N8NService initialized but n8n is not healthy")
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize N8NService: {e}")
            self.is_healthy = False
            return False
    
    async def shutdown(self):
        """Shutdown the n8n service."""
        if self.api_client:
            await self.api_client.__aexit__(None, None, None)
        logger.info("N8NService shutdown complete")
    
    async def _sync_workflows(self):
        """Sync workflows from n8n to local storage."""
        try:
            if not self.workflow_manager:
                return
            
            workflows = await self.api_client.get_workflows()
            for workflow_data in workflows:
                workflow = WorkflowDefinition(
                    id=workflow_data.get('id', ''),
                    name=workflow_data.get('name', ''),
                    active=workflow_data.get('active', False),
                    nodes=workflow_data.get('nodes', []),
                    connections=workflow_data.get('connections', {}),
                    settings=workflow_data.get('settings', {}),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                await self.workflow_manager.store_workflow(workflow)
            
            logger.info(f"Synced {len(workflows)} workflows from n8n")
        except Exception as e:
            logger.error(f"Error syncing workflows: {e}")
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get the status of the n8n service."""
        status = {
            'service': 'n8n',
            'healthy': self.is_healthy,
            'n8n_url': self.n8n_url,
            'timestamp': datetime.now().isoformat()
        }
        
        if self.api_client:
            status['n8n_healthy'] = await self.api_client.health_check()
        
        if self.workflow_manager:
            workflows = await self.workflow_manager.list_workflows()
            status['workflow_count'] = len(workflows)
        
        return status
    
    async def list_workflows(self) -> List[Dict[str, Any]]:
        """List all available workflows."""
        try:
            if not self.workflow_manager:
                return []
            
            workflows = await self.workflow_manager.list_workflows()
            return [
                {
                    'id': w.id,
                    'name': w.name,
                    'active': w.active,
                    'created_at': w.created_at.isoformat(),
                    'updated_at': w.updated_at.isoformat()
                }
                for w in workflows
            ]
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            return []
    
    async def execute_workflow(self, workflow_id: str, input_data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Execute a workflow and return execution ID."""
        try:
            if not self.api_client or not self.is_healthy:
                logger.error("Cannot execute workflow: n8n service not healthy")
                return None
            
            execution_id = await self.api_client.execute_workflow(workflow_id, input_data)
            
            if execution_id and self.workflow_manager:
                # Store execution record
                execution = WorkflowExecution(
                    id=execution_id,
                    workflow_id=workflow_id,
                    status='running',
                    started_at=datetime.now(),
                    finished_at=None,
                    data=input_data or {},
                    error=None
                )
                await self.workflow_manager.store_execution(execution)
            
            return execution_id
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {e}")
            return None
    
    async def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a workflow execution."""
        try:
            if not self.api_client:
                return None
            
            execution_data = await self.api_client.get_execution(execution_id)
            if execution_data:
                return {
                    'id': execution_id,
                    'status': execution_data.get('status', 'unknown'),
                    'started_at': execution_data.get('startedAt'),
                    'finished_at': execution_data.get('stoppedAt'),
                    'data': execution_data.get('data', {})
                }
            return None
        except Exception as e:
            logger.error(f"Error getting execution status {execution_id}: {e}")
            return None
    
    async def get_workflow_capabilities(self) -> Dict[str, Any]:
        """Get available workflow capabilities for integration."""
        return {
            'workflow_management': {
                'list_workflows': True,
                'execute_workflow': True,
                'get_execution_status': True
            },
            'service_integration': {
                'xmr_mining': True,
                'meshnet': True,
                'eliza_agent': True,
                'memory_service': True,
                'speech_service': True,
                'autonomy_service': True
            },
            'external_integrations': {
                'http_requests': True,
                'webhooks': True,
                'scheduled_tasks': True,
                'data_transformation': True
            }
        }
    
    async def create_xmrt_integration_workflow(self) -> Optional[str]:
        """Create a sample workflow for XMRT service integration."""
        try:
            # This would create a basic workflow that demonstrates integration
            # with XMRT services. In a real implementation, this would use
            # the n8n API to create the workflow programmatically.
            
            workflow_definition = {
                "name": "XMRT Service Integration Demo",
                "active": True,
                "nodes": [
                    {
                        "id": "start",
                        "type": "n8n-nodes-base.start",
                        "typeVersion": 1,
                        "position": [240, 300]
                    },
                    {
                        "id": "http_request",
                        "type": "n8n-nodes-base.httpRequest",
                        "typeVersion": 1,
                        "position": [460, 300],
                        "parameters": {
                            "url": "http://localhost:5000/api/dashboard",
                            "method": "GET"
                        }
                    }
                ],
                "connections": {
                    "start": {
                        "main": [
                            [
                                {
                                    "node": "http_request",
                                    "type": "main",
                                    "index": 0
                                }
                            ]
                        ]
                    }
                }
            }
            
            logger.info("Sample XMRT integration workflow definition created")
            return "sample_workflow_id"
            
        except Exception as e:
            logger.error(f"Error creating integration workflow: {e}")
            return None

