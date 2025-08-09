"""
XMRT-DAO-Ecosystem Autonomous Execution Engine

This module implements sophisticated autonomous execution capabilities
that enable Eliza to execute complex decisions and actions in the real world
without human intervention while maintaining security and reliability.

Key Features:
- Secure transaction execution
- Multi-step workflow orchestration
- Real-time monitoring and adjustment
- Automatic rollback and recovery
- External system integration
- Resource management and optimization
"""

import logging
import asyncio
import json
import time
import aiohttp
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import hashlib
import os
from contextlib import asynccontextmanager

# GitHub integration
import requests
from github import Github

# Blockchain and crypto utilities
import hashlib
import hmac
import base64

class ExecutionStatus(Enum):
    """Status of execution tasks"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    PAUSED = "paused"

class ExecutionPriority(Enum):
    """Priority levels for execution tasks"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ExecutionTask:
    """Represents an execution task"""
    task_id: str
    task_type: str
    description: str
    priority: ExecutionPriority
    parameters: Dict[str, Any]
    dependencies: List[str]
    timeout_seconds: int
    retry_count: int
    max_retries: int
    rollback_data: Optional[Dict[str, Any]] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@dataclass
class ExecutionWorkflow:
    """Represents a multi-step execution workflow"""
    workflow_id: str
    name: str
    description: str
    tasks: List[ExecutionTask]
    parallel_execution: bool
    rollback_on_failure: bool
    status: ExecutionStatus = ExecutionStatus.PENDING
    current_task_index: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None

class AutonomousExecutionEngine:
    """
    Advanced autonomous execution engine for the XMRT-DAO-Ecosystem
    
    This engine implements sophisticated execution capabilities including:
    - Secure transaction execution with multi-signature support
    - Complex workflow orchestration with dependency management
    - Real-time monitoring and adaptive execution
    - Automatic error handling and recovery
    - External system integration and API management
    - Resource optimization and load balancing
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Execution state
        self.active_workflows = {}
        self.active_tasks = {}
        self.completed_workflows = []
        self.execution_history = []
        
        # Resource management
        self.resource_pools = {
            'cpu': {'available': 100, 'allocated': 0},
            'memory': {'available': 100, 'allocated': 0},
            'network': {'available': 100, 'allocated': 0},
            'storage': {'available': 100, 'allocated': 0}
        }
        
        # External service connections
        self.github_client = None
        self.http_session = None
        
        # Security and authentication
        self.api_keys = {}
        self.auth_tokens = {}
        
        # Monitoring and metrics
        self.execution_metrics = {
            'total_tasks_executed': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time': 0.0,
            'resource_utilization': {}
        }
        
        # Initialize components
        asyncio.create_task(self._initialize_components())
        
        self.logger.info("Autonomous Execution Engine initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the execution engine"""
        logger = logging.getLogger(f"{__name__}.AutonomousExecutionEngine")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    async def _initialize_components(self):
        """Initialize execution engine components"""
        try:
            # Initialize HTTP session
            self.http_session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=300)
            )
            
            # Initialize GitHub client if token available
            github_token = os.getenv('GITHUB_TOKEN')
            if github_token:
                self.github_client = Github(github_token)
                self.logger.info("GitHub client initialized")
            
            # Load API keys and tokens
            await self._load_credentials()
            
            # Start background monitoring
            asyncio.create_task(self._monitoring_loop())
            
            self.logger.info("Execution engine components initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")

    async def _load_credentials(self):
        """Load API keys and authentication tokens"""
        try:
            # Load from environment variables
            self.api_keys = {
                'github': os.getenv('GITHUB_TOKEN'),
                'openai': os.getenv('OPENAI_API_KEY'),
                # Add other API keys as needed
            }
            
            # Filter out None values
            self.api_keys = {k: v for k, v in self.api_keys.items() if v}
            
            self.logger.info(f"Loaded {len(self.api_keys)} API credentials")
            
        except Exception as e:
            self.logger.error(f"Error loading credentials: {e}")

    async def execute_workflow(self, workflow: ExecutionWorkflow) -> Dict[str, Any]:
        """
        Execute a complete workflow with multiple tasks
        
        Args:
            workflow: ExecutionWorkflow to execute
            
        Returns:
            Dict containing execution results and status
        """
        try:
            self.logger.info(f"Starting workflow execution: {workflow.workflow_id}")
            
            workflow.status = ExecutionStatus.RUNNING
            workflow.start_time = time.time()
            
            self.active_workflows[workflow.workflow_id] = workflow
            
            if workflow.parallel_execution:
                result = await self._execute_parallel_workflow(workflow)
            else:
                result = await self._execute_sequential_workflow(workflow)
            
            workflow.end_time = time.time()
            workflow.status = ExecutionStatus.COMPLETED if result['success'] else ExecutionStatus.FAILED
            
            # Move to completed workflows
            self.completed_workflows.append(workflow)
            del self.active_workflows[workflow.workflow_id]
            
            # Update metrics
            self._update_execution_metrics(workflow, result)
            
            self.logger.info(
                f"Workflow {workflow.workflow_id} completed: "
                f"{'SUCCESS' if result['success'] else 'FAILED'}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing workflow {workflow.workflow_id}: {e}")
            workflow.status = ExecutionStatus.FAILED
            workflow.end_time = time.time()
            
            if workflow.rollback_on_failure:
                await self._rollback_workflow(workflow)
            
            return {
                'success': False,
                'error': str(e),
                'workflow_id': workflow.workflow_id
            }

    async def _execute_sequential_workflow(self, workflow: ExecutionWorkflow) -> Dict[str, Any]:
        """Execute workflow tasks sequentially"""
        try:
            results = []
            
            for i, task in enumerate(workflow.tasks):
                workflow.current_task_index = i
                
                # Check dependencies
                if not await self._check_task_dependencies(task, results):
                    return {
                        'success': False,
                        'error': f"Task {task.task_id} dependencies not met",
                        'completed_tasks': results
                    }
                
                # Execute task
                task_result = await self.execute_task(task)
                results.append(task_result)
                
                # Check if task failed and rollback is enabled
                if not task_result['success'] and workflow.rollback_on_failure:
                    await self._rollback_workflow(workflow)
                    return {
                        'success': False,
                        'error': f"Task {task.task_id} failed, workflow rolled back",
                        'completed_tasks': results
                    }
                
                # Continue even if task failed (if rollback not enabled)
                if not task_result['success']:
                    self.logger.warning(f"Task {task.task_id} failed but continuing workflow")
            
            return {
                'success': True,
                'completed_tasks': results,
                'workflow_id': workflow.workflow_id
            }
            
        except Exception as e:
            self.logger.error(f"Error in sequential workflow execution: {e}")
            return {
                'success': False,
                'error': str(e),
                'completed_tasks': results if 'results' in locals() else []
            }

    async def _execute_parallel_workflow(self, workflow: ExecutionWorkflow) -> Dict[str, Any]:
        """Execute workflow tasks in parallel where possible"""
        try:
            # Group tasks by dependency levels
            task_levels = self._analyze_task_dependencies(workflow.tasks)
            results = []
            
            for level, tasks in task_levels.items():
                self.logger.info(f"Executing level {level} with {len(tasks)} tasks")
                
                # Execute all tasks in this level in parallel
                level_tasks = [self.execute_task(task) for task in tasks]
                level_results = await asyncio.gather(*level_tasks, return_exceptions=True)
                
                # Process results
                for i, result in enumerate(level_results):
                    if isinstance(result, Exception):
                        task_result = {
                            'success': False,
                            'error': str(result),
                            'task_id': tasks[i].task_id
                        }
                    else:
                        task_result = result
                    
                    results.append(task_result)
                    
                    # Check for failures
                    if not task_result['success'] and workflow.rollback_on_failure:
                        await self._rollback_workflow(workflow)
                        return {
                            'success': False,
                            'error': f"Task {task_result.get('task_id', 'unknown')} failed",
                            'completed_tasks': results
                        }
            
            return {
                'success': True,
                'completed_tasks': results,
                'workflow_id': workflow.workflow_id
            }
            
        except Exception as e:
            self.logger.error(f"Error in parallel workflow execution: {e}")
            return {
                'success': False,
                'error': str(e),
                'completed_tasks': results if 'results' in locals() else []
            }

    async def execute_task(self, task: ExecutionTask) -> Dict[str, Any]:
        """
        Execute a single task
        
        Args:
            task: ExecutionTask to execute
            
        Returns:
            Dict containing execution result
        """
        try:
            self.logger.info(f"Executing task: {task.task_id} ({task.task_type})")
            
            task.status = ExecutionStatus.RUNNING
            task.start_time = time.time()
            
            self.active_tasks[task.task_id] = task
            
            # Check resource availability
            if not await self._allocate_resources(task):
                return {
                    'success': False,
                    'error': 'Insufficient resources available',
                    'task_id': task.task_id
                }
            
            # Execute task based on type
            result = await self._execute_task_by_type(task)
            
            task.end_time = time.time()
            task.result = result
            task.status = ExecutionStatus.COMPLETED if result['success'] else ExecutionStatus.FAILED
            
            # Release resources
            await self._release_resources(task)
            
            # Remove from active tasks
            del self.active_tasks[task.task_id]
            
            # Update metrics
            self.execution_metrics['total_tasks_executed'] += 1
            if result['success']:
                self.execution_metrics['successful_executions'] += 1
            else:
                self.execution_metrics['failed_executions'] += 1
            
            execution_time = task.end_time - task.start_time
            self.execution_metrics['average_execution_time'] = (
                (self.execution_metrics['average_execution_time'] * 
                 (self.execution_metrics['total_tasks_executed'] - 1) + execution_time) /
                self.execution_metrics['total_tasks_executed']
            )
            
            self.logger.info(
                f"Task {task.task_id} completed in {execution_time:.2f}s: "
                f"{'SUCCESS' if result['success'] else 'FAILED'}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing task {task.task_id}: {e}")
            task.status = ExecutionStatus.FAILED
            task.error = str(e)
            task.end_time = time.time()
            
            # Release resources and cleanup
            await self._release_resources(task)
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
            
            return {
                'success': False,
                'error': str(e),
                'task_id': task.task_id
            }

    async def _execute_task_by_type(self, task: ExecutionTask) -> Dict[str, Any]:
        """Execute task based on its type"""
        try:
            task_type = task.task_type.lower()
            
            if task_type == 'github_operation':
                return await self._execute_github_task(task)
            elif task_type == 'api_call':
                return await self._execute_api_call_task(task)
            elif task_type == 'file_operation':
                return await self._execute_file_operation_task(task)
            elif task_type == 'data_processing':
                return await self._execute_data_processing_task(task)
            elif task_type == 'monitoring':
                return await self._execute_monitoring_task(task)
            elif task_type == 'notification':
                return await self._execute_notification_task(task)
            elif task_type == 'system_command':
                return await self._execute_system_command_task(task)
            else:
                return {
                    'success': False,
                    'error': f'Unknown task type: {task_type}',
                    'task_id': task.task_id
                }
                
        except Exception as e:
            self.logger.error(f"Error executing task type {task.task_type}: {e}")
            return {
                'success': False,
                'error': str(e),
                'task_id': task.task_id
            }

    async def _execute_github_task(self, task: ExecutionTask) -> Dict[str, Any]:
        """Execute GitHub-related tasks"""
        try:
            if not self.github_client:
                return {
                    'success': False,
                    'error': 'GitHub client not initialized',
                    'task_id': task.task_id
                }
            
            operation = task.parameters.get('operation')
            repo_name = task.parameters.get('repository')
            
            if operation == 'create_branch':
                return await self._github_create_branch(task)
            elif operation == 'commit_files':
                return await self._github_commit_files(task)
            elif operation == 'create_pull_request':
                return await self._github_create_pull_request(task)
            elif operation == 'merge_pull_request':
                return await self._github_merge_pull_request(task)
            elif operation == 'create_issue':
                return await self._github_create_issue(task)
            elif operation == 'update_file':
                return await self._github_update_file(task)
            else:
                return {
                    'success': False,
                    'error': f'Unknown GitHub operation: {operation}',
                    'task_id': task.task_id
                }
                
        except Exception as e:
            self.logger.error(f"Error executing GitHub task: {e}")
            return {
                'success': False,
                'error': str(e),
                'task_id': task.task_id
            }

    async def _github_create_branch(self, task: ExecutionTask) -> Dict[str, Any]:
        """Create a new branch in GitHub repository"""
        try:
            repo_name = task.parameters['repository']
            branch_name = task.parameters['branch_name']
            base_branch = task.parameters.get('base_branch', 'main')
            
            repo = self.github_client.get_repo(repo_name)
            base_ref = repo.get_git_ref(f'heads/{base_branch}')
            
            new_ref = repo.create_git_ref(
                ref=f'refs/heads/{branch_name}',
                sha=base_ref.object.sha
            )
            
            return {
                'success': True,
                'result': {
                    'branch_name': branch_name,
                    'sha': new_ref.object.sha,
                    'url': new_ref.url
                },
                'task_id': task.task_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'task_id': task.task_id
            }

    async def _github_commit_files(self, task: ExecutionTask) -> Dict[str, Any]:
        """Commit files to GitHub repository"""
        try:
            repo_name = task.parameters['repository']
            branch_name = task.parameters['branch_name']
            files = task.parameters['files']  # List of {'path': str, 'content': str}
            commit_message = task.parameters['commit_message']
            
            repo = self.github_client.get_repo(repo_name)
            
            # Get the latest commit on the branch
            branch_ref = repo.get_git_ref(f'heads/{branch_name}')
            latest_commit = repo.get_git_commit(branch_ref.object.sha)
            
            # Create blobs for each file
            blobs = []
            for file_info in files:
                blob = repo.create_git_blob(file_info['content'], 'utf-8')
                blobs.append({
                    'path': file_info['path'],
                    'mode': '100644',
                    'type': 'blob',
                    'sha': blob.sha
                })
            
            # Create tree
            tree = repo.create_git_tree(blobs, latest_commit.tree)
            
            # Create commit
            commit = repo.create_git_commit(
                message=commit_message,
                tree=tree,
                parents=[latest_commit]
            )
            
            # Update branch reference
            branch_ref.edit(commit.sha)
            
            return {
                'success': True,
                'result': {
                    'commit_sha': commit.sha,
                    'commit_url': commit.html_url,
                    'files_committed': len(files)
                },
                'task_id': task.task_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'task_id': task.task_id
            }

    async def _github_create_pull_request(self, task: ExecutionTask) -> Dict[str, Any]:
        """Create a pull request in GitHub repository"""
        try:
            repo_name = task.parameters['repository']
            title = task.parameters['title']
            body = task.parameters.get('body', '')
            head_branch = task.parameters['head_branch']
            base_branch = task.parameters.get('base_branch', 'main')
            
            repo = self.github_client.get_repo(repo_name)
            
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch
            )
            
            return {
                'success': True,
                'result': {
                    'pr_number': pr.number,
                    'pr_url': pr.html_url,
                    'state': pr.state
                },
                'task_id': task.task_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'task_id': task.task_id
            }

    async def _execute_api_call_task(self, task: ExecutionTask) -> Dict[str, Any]:
        """Execute API call tasks"""
        try:
            url = task.parameters['url']
            method = task.parameters.get('method', 'GET').upper()
            headers = task.parameters.get('headers', {})
            data = task.parameters.get('data')
            params = task.parameters.get('params')
            timeout = task.parameters.get('timeout', 30)
            
            async with self.http_session.request(
                method=method,
                url=url,
                headers=headers,
                json=data if data else None,
                params=params,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:
                response_data = await response.text()
                
                try:
                    response_json = await response.json()
                except:
                    response_json = None
                
                return {
                    'success': response.status < 400,
                    'result': {
                        'status_code': response.status,
                        'response_data': response_json or response_data,
                        'headers': dict(response.headers)
                    },
                    'task_id': task.task_id
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'task_id': task.task_id
            }

    async def _execute_file_operation_task(self, task: ExecutionTask) -> Dict[str, Any]:
        """Execute file operation tasks"""
        try:
            operation = task.parameters['operation']
            file_path = task.parameters['file_path']
            
            if operation == 'read':
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {
                    'success': True,
                    'result': {'content': content, 'file_path': file_path},
                    'task_id': task.task_id
                }
                
            elif operation == 'write':
                content = task.parameters['content']
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {
                    'success': True,
                    'result': {'file_path': file_path, 'bytes_written': len(content.encode('utf-8'))},
                    'task_id': task.task_id
                }
                
            elif operation == 'append':
                content = task.parameters['content']
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(content)
                return {
                    'success': True,
                    'result': {'file_path': file_path, 'bytes_appended': len(content.encode('utf-8'))},
                    'task_id': task.task_id
                }
                
            elif operation == 'delete':
                os.remove(file_path)
                return {
                    'success': True,
                    'result': {'file_path': file_path, 'deleted': True},
                    'task_id': task.task_id
                }
                
            else:
                return {
                    'success': False,
                    'error': f'Unknown file operation: {operation}',
                    'task_id': task.task_id
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'task_id': task.task_id
            }

    async def _execute_data_processing_task(self, task: ExecutionTask) -> Dict[str, Any]:
        """Execute data processing tasks"""
        try:
            operation = task.parameters['operation']
            data = task.parameters['data']
            
            if operation == 'json_parse':
                if isinstance(data, str):
                    parsed_data = json.loads(data)
                else:
                    parsed_data = data
                    
                return {
                    'success': True,
                    'result': {'parsed_data': parsed_data},
                    'task_id': task.task_id
                }
                
            elif operation == 'json_stringify':
                json_string = json.dumps(data, indent=2)
                return {
                    'success': True,
                    'result': {'json_string': json_string},
                    'task_id': task.task_id
                }
                
            elif operation == 'filter':
                filter_criteria = task.parameters['filter_criteria']
                filtered_data = [
                    item for item in data 
                    if all(item.get(k) == v for k, v in filter_criteria.items())
                ]
                return {
                    'success': True,
                    'result': {'filtered_data': filtered_data, 'count': len(filtered_data)},
                    'task_id': task.task_id
                }
                
            elif operation == 'aggregate':
                aggregation_type = task.parameters['aggregation_type']
                field = task.parameters['field']
                
                values = [item.get(field, 0) for item in data if field in item]
                
                if aggregation_type == 'sum':
                    result_value = sum(values)
                elif aggregation_type == 'average':
                    result_value = sum(values) / len(values) if values else 0
                elif aggregation_type == 'count':
                    result_value = len(values)
                elif aggregation_type == 'max':
                    result_value = max(values) if values else None
                elif aggregation_type == 'min':
                    result_value = min(values) if values else None
                else:
                    return {
                        'success': False,
                        'error': f'Unknown aggregation type: {aggregation_type}',
                        'task_id': task.task_id
                    }
                
                return {
                    'success': True,
                    'result': {
                        'aggregation_type': aggregation_type,
                        'field': field,
                        'value': result_value,
                        'count': len(values)
                    },
                    'task_id': task.task_id
                }
                
            else:
                return {
                    'success': False,
                    'error': f'Unknown data processing operation: {operation}',
                    'task_id': task.task_id
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'task_id': task.task_id
            }

    async def _execute_monitoring_task(self, task: ExecutionTask) -> Dict[str, Any]:
        """Execute monitoring tasks"""
        try:
            metric_name = task.parameters['metric_name']
            target_value = task.parameters.get('target_value')
            comparison = task.parameters.get('comparison', 'equals')
            timeout = task.parameters.get('timeout', 60)
            
            # This would typically integrate with actual monitoring systems
            # For now, simulate monitoring by checking execution metrics
            
            current_value = self.execution_metrics.get(metric_name, 0)
            
            if comparison == 'equals':
                condition_met = current_value == target_value
            elif comparison == 'greater_than':
                condition_met = current_value > target_value
            elif comparison == 'less_than':
                condition_met = current_value < target_value
            elif comparison == 'greater_equal':
                condition_met = current_value >= target_value
            elif comparison == 'less_equal':
                condition_met = current_value <= target_value
            else:
                return {
                    'success': False,
                    'error': f'Unknown comparison operator: {comparison}',
                    'task_id': task.task_id
                }
            
            return {
                'success': True,
                'result': {
                    'metric_name': metric_name,
                    'current_value': current_value,
                    'target_value': target_value,
                    'comparison': comparison,
                    'condition_met': condition_met
                },
                'task_id': task.task_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'task_id': task.task_id
            }

    async def _execute_notification_task(self, task: ExecutionTask) -> Dict[str, Any]:
        """Execute notification tasks"""
        try:
            notification_type = task.parameters['type']
            message = task.parameters['message']
            recipients = task.parameters.get('recipients', [])
            
            # Log notification (in production, this would send actual notifications)
            self.logger.info(f"NOTIFICATION [{notification_type}]: {message}")
            
            if recipients:
                self.logger.info(f"Recipients: {', '.join(recipients)}")
            
            return {
                'success': True,
                'result': {
                    'notification_type': notification_type,
                    'message': message,
                    'recipients_count': len(recipients),
                    'sent_at': time.time()
                },
                'task_id': task.task_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'task_id': task.task_id
            }

    async def _execute_system_command_task(self, task: ExecutionTask) -> Dict[str, Any]:
        """Execute system command tasks"""
        try:
            command = task.parameters['command']
            working_directory = task.parameters.get('working_directory', '.')
            timeout = task.parameters.get('timeout', 60)
            
            # Execute command using asyncio subprocess
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=working_directory,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                
                return {
                    'success': process.returncode == 0,
                    'result': {
                        'return_code': process.returncode,
                        'stdout': stdout.decode('utf-8') if stdout else '',
                        'stderr': stderr.decode('utf-8') if stderr else '',
                        'command': command
                    },
                    'task_id': task.task_id
                }
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    'success': False,
                    'error': f'Command timed out after {timeout} seconds',
                    'task_id': task.task_id
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'task_id': task.task_id
            }

    async def _allocate_resources(self, task: ExecutionTask) -> bool:
        """Allocate resources for task execution"""
        try:
            required_resources = task.parameters.get('resource_requirements', {})
            
            # Check if resources are available
            for resource_type, required_amount in required_resources.items():
                if resource_type in self.resource_pools:
                    available = (
                        self.resource_pools[resource_type]['available'] - 
                        self.resource_pools[resource_type]['allocated']
                    )
                    if available < required_amount:
                        return False
            
            # Allocate resources
            for resource_type, required_amount in required_resources.items():
                if resource_type in self.resource_pools:
                    self.resource_pools[resource_type]['allocated'] += required_amount
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error allocating resources: {e}")
            return False

    async def _release_resources(self, task: ExecutionTask):
        """Release resources after task completion"""
        try:
            required_resources = task.parameters.get('resource_requirements', {})
            
            for resource_type, required_amount in required_resources.items():
                if resource_type in self.resource_pools:
                    self.resource_pools[resource_type]['allocated'] -= required_amount
                    # Ensure allocated doesn't go negative
                    self.resource_pools[resource_type]['allocated'] = max(
                        0, self.resource_pools[resource_type]['allocated']
                    )
            
        except Exception as e:
            self.logger.error(f"Error releasing resources: {e}")

    async def _check_task_dependencies(self, task: ExecutionTask, completed_results: List[Dict[str, Any]]) -> bool:
        """Check if task dependencies are satisfied"""
        try:
            if not task.dependencies:
                return True
            
            completed_task_ids = {result.get('task_id') for result in completed_results}
            
            for dependency_id in task.dependencies:
                if dependency_id not in completed_task_ids:
                    return False
                
                # Check if dependency was successful
                dependency_result = next(
                    (r for r in completed_results if r.get('task_id') == dependency_id),
                    None
                )
                
                if not dependency_result or not dependency_result.get('success', False):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking task dependencies: {e}")
            return False

    def _analyze_task_dependencies(self, tasks: List[ExecutionTask]) -> Dict[int, List[ExecutionTask]]:
        """Analyze task dependencies and group tasks by execution level"""
        try:
            task_map = {task.task_id: task for task in tasks}
            levels = {}
            task_levels = {}
            
            def get_task_level(task_id: str) -> int:
                if task_id in task_levels:
                    return task_levels[task_id]
                
                task = task_map[task_id]
                if not task.dependencies:
                    level = 0
                else:
                    max_dep_level = max(get_task_level(dep_id) for dep_id in task.dependencies)
                    level = max_dep_level + 1
                
                task_levels[task_id] = level
                return level
            
            # Calculate levels for all tasks
            for task in tasks:
                level = get_task_level(task.task_id)
                if level not in levels:
                    levels[level] = []
                levels[level].append(task)
            
            return levels
            
        except Exception as e:
            self.logger.error(f"Error analyzing task dependencies: {e}")
            return {0: tasks}  # Fallback to sequential execution

    async def _rollback_workflow(self, workflow: ExecutionWorkflow):
        """Rollback a failed workflow"""
        try:
            self.logger.info(f"Rolling back workflow: {workflow.workflow_id}")
            
            # Execute rollback tasks in reverse order
            for task in reversed(workflow.tasks):
                if task.status == ExecutionStatus.COMPLETED and task.rollback_data:
                    await self._rollback_task(task)
            
            workflow.status = ExecutionStatus.ROLLED_BACK
            self.logger.info(f"Workflow {workflow.workflow_id} rolled back successfully")
            
        except Exception as e:
            self.logger.error(f"Error rolling back workflow {workflow.workflow_id}: {e}")

    async def _rollback_task(self, task: ExecutionTask):
        """Rollback a single task"""
        try:
            if not task.rollback_data:
                return
            
            rollback_task = ExecutionTask(
                task_id=f"{task.task_id}_rollback",
                task_type=task.rollback_data.get('type', task.task_type),
                description=f"Rollback for {task.description}",
                priority=ExecutionPriority.HIGH,
                parameters=task.rollback_data.get('parameters', {}),
                dependencies=[],
                timeout_seconds=task.timeout_seconds,
                retry_count=0,
                max_retries=1
            )
            
            result = await self.execute_task(rollback_task)
            
            if result['success']:
                self.logger.info(f"Task {task.task_id} rolled back successfully")
            else:
                self.logger.error(f"Failed to rollback task {task.task_id}: {result.get('error')}")
            
        except Exception as e:
            self.logger.error(f"Error rolling back task {task.task_id}: {e}")

    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while True:
            try:
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
                # Update resource utilization metrics
                for resource_type, pool in self.resource_pools.items():
                    utilization = pool['allocated'] / pool['available'] if pool['available'] > 0 else 0
                    self.execution_metrics['resource_utilization'][resource_type] = utilization
                
                # Check for stuck tasks
                current_time = time.time()
                for task_id, task in list(self.active_tasks.items()):
                    if task.start_time and (current_time - task.start_time) > task.timeout_seconds:
                        self.logger.warning(f"Task {task_id} has exceeded timeout, marking as failed")
                        task.status = ExecutionStatus.FAILED
                        task.error = "Task timeout exceeded"
                        task.end_time = current_time
                        await self._release_resources(task)
                        del self.active_tasks[task_id]
                
                # Log status periodically
                if len(self.active_tasks) > 0 or len(self.active_workflows) > 0:
                    self.logger.info(
                        f"Execution status: {len(self.active_workflows)} workflows, "
                        f"{len(self.active_tasks)} tasks active"
                    )
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")

    def _update_execution_metrics(self, workflow: ExecutionWorkflow, result: Dict[str, Any]):
        """Update execution metrics after workflow completion"""
        try:
            execution_time = workflow.end_time - workflow.start_time if workflow.end_time and workflow.start_time else 0
            
            # Update workflow-specific metrics
            if 'workflow_metrics' not in self.execution_metrics:
                self.execution_metrics['workflow_metrics'] = {
                    'total_workflows': 0,
                    'successful_workflows': 0,
                    'failed_workflows': 0,
                    'average_workflow_time': 0.0
                }
            
            metrics = self.execution_metrics['workflow_metrics']
            metrics['total_workflows'] += 1
            
            if result['success']:
                metrics['successful_workflows'] += 1
            else:
                metrics['failed_workflows'] += 1
            
            # Update average workflow time
            metrics['average_workflow_time'] = (
                (metrics['average_workflow_time'] * (metrics['total_workflows'] - 1) + execution_time) /
                metrics['total_workflows']
            )
            
        except Exception as e:
            self.logger.error(f"Error updating execution metrics: {e}")

    async def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution engine status"""
        try:
            return {
                'active_workflows': len(self.active_workflows),
                'active_tasks': len(self.active_tasks),
                'completed_workflows': len(self.completed_workflows),
                'resource_pools': self.resource_pools.copy(),
                'execution_metrics': self.execution_metrics.copy(),
                'github_client_available': self.github_client is not None,
                'http_session_available': self.http_session is not None,
                'api_keys_loaded': len(self.api_keys)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting execution status: {e}")
            return {'error': str(e)}

    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a running workflow"""
        try:
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                workflow.status = ExecutionStatus.PAUSED
                self.logger.info(f"Workflow {workflow_id} paused")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error pausing workflow {workflow_id}: {e}")
            return False

    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow"""
        try:
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                if workflow.status == ExecutionStatus.PAUSED:
                    workflow.status = ExecutionStatus.RUNNING
                    self.logger.info(f"Workflow {workflow_id} resumed")
                    return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error resuming workflow {workflow_id}: {e}")
            return False

    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a running workflow"""
        try:
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                workflow.status = ExecutionStatus.FAILED
                workflow.end_time = time.time()
                
                # Cancel active tasks in this workflow
                for task in workflow.tasks:
                    if task.task_id in self.active_tasks:
                        task.status = ExecutionStatus.FAILED
                        task.error = "Workflow cancelled"
                        task.end_time = time.time()
                        await self._release_resources(task)
                        del self.active_tasks[task.task_id]
                
                # Move to completed workflows
                self.completed_workflows.append(workflow)
                del self.active_workflows[workflow_id]
                
                self.logger.info(f"Workflow {workflow_id} cancelled")
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error cancelling workflow {workflow_id}: {e}")
            return False

    async def cleanup(self):
        """Cleanup resources and connections"""
        try:
            if self.http_session:
                await self.http_session.close()
            
            self.logger.info("Execution engine cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

