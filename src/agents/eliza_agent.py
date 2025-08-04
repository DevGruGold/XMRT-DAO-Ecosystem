"""
Eliza Autonomous Agent

This module implements the core Eliza AI agent with autonomous capabilities
for the XMRT DAO Ecosystem, including self-improvement, application creation,
and GitHub operations.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os
import sys

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.redis_service import RedisService
from services.raglight_service import RAGlightService

class ElizaAgent:
    """
    Autonomous Eliza AI Agent for the XMRT DAO Ecosystem.
    
    Capabilities:
    - Autonomous decision-making
    - Application creation and deployment
    - Self-improvement and learning
    - GitHub repository management
    - Multi-agent coordination
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        self.is_active = False
        self.learning_enabled = True
        self.github_access = config.get('github_access', {})
        
        # AI capabilities
        self.consciousness_level = 0.85  # 85% autonomy as per plan
        self.decision_accuracy = 0.0
        self.learning_rate = 0.01
        
        # Memory and state
        self.memory = {}
        self.current_tasks = []
        self.completed_tasks = []
        self.created_applications = []
        
        # Initialize Redis service for memory persistence
        redis_config = config.get('redis', {})
        self.redis_service = RedisService(
            host=redis_config.get('host', 'localhost'),
            port=redis_config.get('port', 6379),
            db=redis_config.get('db', 0),
            password=redis_config.get('password')
        )
        
        # Initialize RAGlight service for enhanced AI capabilities
        raglight_config = config.get('raglight', {})
        self.raglight_service = RAGlightService(
            vector_store_path=raglight_config.get('vector_store_path', './data/vector_store'),
            embedding_model=raglight_config.get('embedding_model', 'all-MiniLM-L6-v2'),
            llm_provider=raglight_config.get('llm_provider', 'openai')
        )
        
        self.agent_id = "eliza_main"
        self.logger.info("Eliza Agent initialized with 85% autonomy level, Redis and RAGlight services")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger('eliza_agent')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def activate(self):
        """Activate the Eliza agent."""
        self.logger.info("Activating Eliza Agent")
        self.is_active = True
        
        # Initialize Redis connection
        if not self.redis_service.connect():
            self.logger.warning("Failed to connect to Redis - continuing without persistence")
        else:
            self.logger.info("Redis connection established")
            # Load previous state if available
            await self._load_agent_state()
        
        # Initialize RAGlight service
        if not self.raglight_service.initialize():
            self.logger.warning("Failed to initialize RAGlight - continuing with basic AI")
        else:
            self.logger.info("RAGlight service initialized")
            # Load knowledge base
            await self._initialize_knowledge_base()
        
        # Initialize AI components
        await self._initialize_ai_components()
        
        # Start autonomous operation
        await self._start_autonomous_operation()
    
    async def deactivate(self):
        """Deactivate the Eliza agent."""
        self.logger.info("Deactivating Eliza Agent")
        self.is_active = False
    
    async def _initialize_ai_components(self):
        """Initialize AI components and capabilities."""
        self.logger.info("Initializing AI components")
        
        # TODO: Initialize MCDA (Multi-Criteria Decision Analysis)
        # TODO: Initialize XAI (Explainable AI) components
        # TODO: Initialize memory systems
        # TODO: Initialize learning algorithms
        
        self.logger.info("AI components initialized")
    
    async def _start_autonomous_operation(self):
        """Start autonomous operation loop."""
        self.logger.info("Starting autonomous operation")
        
        while self.is_active:
            try:
                # Perform autonomous cycle
                await self._autonomous_cycle()
                
                # Wait before next cycle
                await asyncio.sleep(self.config.get('agent_cycle_interval', 60))  # 1 minute default
                
            except Exception as e:
                self.logger.error(f"Error in autonomous cycle: {e}")
                await asyncio.sleep(30)  # Wait 30 seconds on error
    
    async def _autonomous_cycle(self):
        """Perform a single autonomous cycle."""
        # 1. Assess environment and opportunities
        opportunities = await self._assess_opportunities()
        
        # 2. Make autonomous decisions
        decisions = await self._make_decisions(opportunities)
        
        # 3. Execute decisions
        await self._execute_decisions(decisions)
        
        # 4. Learn from outcomes
        if self.learning_enabled:
            await self._learn_from_outcomes()
    
    async def _assess_opportunities(self) -> List[Dict[str, Any]]:
        """Assess current opportunities for autonomous action."""
        opportunities = []
        
        # Check for application creation opportunities
        if len(self.created_applications) < self.config.get('max_applications', 10):
            opportunities.append({
                'type': 'create_application',
                'priority': 'medium',
                'description': 'Opportunity to create new application'
            })
        
        # Check for self-improvement opportunities
        if self.decision_accuracy < 0.9:  # If accuracy is below 90%
            opportunities.append({
                'type': 'self_improvement',
                'priority': 'high',
                'description': 'Opportunity to improve decision accuracy'
            })
        
        # Check for GitHub repository opportunities
        opportunities.append({
            'type': 'github_analysis',
            'priority': 'low',
            'description': 'Analyze GitHub repositories for improvements'
        })
        
        return opportunities
    
    async def _make_decisions(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Make autonomous decisions based on opportunities."""
        decisions = []
        
        # Sort opportunities by priority
        high_priority = [op for op in opportunities if op['priority'] == 'high']
        medium_priority = [op for op in opportunities if op['priority'] == 'medium']
        low_priority = [op for op in opportunities if op['priority'] == 'low']
        
        # Process high priority first
        for opportunity in high_priority:
            decision = await self._evaluate_opportunity(opportunity)
            if decision:
                decisions.append(decision)
        
        # Process medium priority if capacity allows
        if len(decisions) < 3:  # Limit concurrent decisions
            for opportunity in medium_priority:
                decision = await self._evaluate_opportunity(opportunity)
                if decision:
                    decisions.append(decision)
                    if len(decisions) >= 3:
                        break
        
        return decisions
    
    async def _evaluate_opportunity(self, opportunity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate a single opportunity and make a decision."""
        opportunity_type = opportunity['type']
        
        if opportunity_type == 'create_application':
            return await self._decide_application_creation()
        elif opportunity_type == 'self_improvement':
            return await self._decide_self_improvement()
        elif opportunity_type == 'github_analysis':
            return await self._decide_github_analysis()
        
        return None
    
    async def _decide_application_creation(self) -> Dict[str, Any]:
        """Decide on application creation."""
        # TODO: Implement sophisticated decision logic
        app_types = ['dapp', 'utility', 'visualization', 'monitoring']
        selected_type = app_types[len(self.created_applications) % len(app_types)]
        
        return {
            'type': 'create_application',
            'app_type': selected_type,
            'name': f'xmrt_{selected_type}_{len(self.created_applications) + 1}',
            'description': f'Autonomous {selected_type} application for XMRT DAO'
        }
    
    async def _decide_self_improvement(self) -> Dict[str, Any]:
        """Decide on self-improvement actions."""
        return {
            'type': 'self_improvement',
            'action': 'analyze_decision_patterns',
            'target': 'decision_accuracy'
        }
    
    async def _decide_github_analysis(self) -> Dict[str, Any]:
        """Decide on GitHub analysis actions."""
        return {
            'type': 'github_analysis',
            'action': 'scan_repositories',
            'target': 'improvement_opportunities'
        }
    
    async def _execute_decisions(self, decisions: List[Dict[str, Any]]):
        """Execute autonomous decisions."""
        for decision in decisions:
            try:
                await self._execute_single_decision(decision)
            except Exception as e:
                self.logger.error(f"Error executing decision {decision}: {e}")
    
    async def _execute_single_decision(self, decision: Dict[str, Any]):
        """Execute a single decision."""
        decision_type = decision.get('type')
        
        if decision_type == 'create_application':
            await self._create_application(decision)
        elif decision_type == 'self_improvement':
            await self._perform_self_improvement(decision)
        elif decision_type == 'github_analysis':
            await self._perform_github_analysis(decision)
    
    async def _create_application(self, decision: Dict[str, Any]):
        """Create a new application autonomously."""
        app_name = decision.get('name')
        app_type = decision.get('app_type')
        
        self.logger.info(f"Creating application: {app_name} of type {app_type}")
        
        # TODO: Implement application creation logic
        # - Generate application code
        # - Create GitHub repository
        # - Deploy to production
        
        # For now, just track the creation
        self.created_applications.append({
            'name': app_name,
            'type': app_type,
            'created_at': datetime.now().isoformat(),
            'status': 'created'
        })
        
        self.logger.info(f"Application {app_name} created successfully")
    
    async def _perform_self_improvement(self, decision: Dict[str, Any]):
        """Perform self-improvement actions."""
        action = decision.get('action')
        
        if action == 'analyze_decision_patterns':
            # TODO: Implement decision pattern analysis
            self.logger.info("Analyzing decision patterns for improvement")
            
            # Simulate improvement
            self.decision_accuracy += self.learning_rate
            if self.decision_accuracy > 1.0:
                self.decision_accuracy = 1.0
    
    async def _perform_github_analysis(self, decision: Dict[str, Any]):
        """Perform GitHub repository analysis."""
        action = decision.get('action')
        
        if action == 'scan_repositories':
            # TODO: Implement GitHub repository scanning
            self.logger.info("Scanning GitHub repositories for improvement opportunities")
    
    async def _learn_from_outcomes(self):
        """Learn from the outcomes of previous decisions."""
        # TODO: Implement learning algorithms
        # - Analyze success/failure of decisions
        # - Update decision-making parameters
        # - Improve future decision accuracy
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            'is_active': self.is_active,
            'consciousness_level': self.consciousness_level,
            'decision_accuracy': self.decision_accuracy,
            'learning_enabled': self.learning_enabled,
            'current_tasks_count': len(self.current_tasks),
            'completed_tasks_count': len(self.completed_tasks),
            'created_applications_count': len(self.created_applications),
            'memory_size': len(self.memory)
        }
    
    def get_created_applications(self) -> List[Dict[str, Any]]:
        """Get list of applications created by Eliza."""
        return self.created_applications.copy()


    
    async def _load_agent_state(self):
        """Load agent state from Redis."""
        try:
            state = self.redis_service.get_agent_state(self.agent_id)
            if state:
                self.memory = state.get('memory', {})
                self.current_tasks = state.get('current_tasks', [])
                self.completed_tasks = state.get('completed_tasks', [])
                self.created_applications = state.get('created_applications', [])
                self.decision_accuracy = state.get('decision_accuracy', 0.0)
                self.learning_rate = state.get('learning_rate', 0.01)
                self.logger.info("Agent state loaded from Redis")
            else:
                self.logger.info("No previous state found in Redis")
        except Exception as e:
            self.logger.error(f"Failed to load agent state: {e}")
    
    async def _save_agent_state(self):
        """Save agent state to Redis."""
        try:
            state = {
                'memory': self.memory,
                'current_tasks': self.current_tasks,
                'completed_tasks': self.completed_tasks,
                'created_applications': self.created_applications,
                'decision_accuracy': self.decision_accuracy,
                'learning_rate': self.learning_rate,
                'consciousness_level': self.consciousness_level,
                'last_active': datetime.now().isoformat()
            }
            
            if self.redis_service.store_agent_state(self.agent_id, state):
                self.logger.debug("Agent state saved to Redis")
            else:
                self.logger.warning("Failed to save agent state to Redis")
        except Exception as e:
            self.logger.error(f"Failed to save agent state: {e}")
    
    async def _initialize_knowledge_base(self):
        """Initialize RAGlight knowledge base with existing project data."""
        try:
            # Add project documentation to knowledge base
            project_docs = [
                {
                    'id': 'project_readme',
                    'content': 'XMRT DAO Ecosystem Initial Framework - Autonomous AI system',
                    'metadata': {'type': 'documentation', 'source': 'project'}
                },
                {
                    'id': 'agent_capabilities',
                    'content': 'Eliza Agent: 85% autonomy, application creation, self-improvement',
                    'metadata': {'type': 'capabilities', 'source': 'agent'}
                }
            ]
            
            if self.raglight_service.ingest_documents(project_docs):
                self.logger.info("Project documentation added to knowledge base")
            
            # Add memory context if available
            if self.memory:
                self.raglight_service.add_memory_context(self.agent_id, self.memory)
                
        except Exception as e:
            self.logger.error(f"Failed to initialize knowledge base: {e}")
    
    async def _enhanced_decision_making(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced decision-making using RAGlight."""
        try:
            # Use RAT (Retrieval Augmented Thinking) for complex decisions
            query = f"Decision context: {context.get('description', 'Unknown decision')}"
            
            if self.raglight_service.initialized:
                rat_result = self.raglight_service.query_rat(query, reflection_steps=2)
                
                decision = {
                    'action': rat_result.get('final_response', 'No action determined'),
                    'confidence': rat_result.get('confidence', 0.5),
                    'reasoning': rat_result.get('reflections', []),
                    'method': 'RAT_enhanced'
                }
            else:
                # Fallback to basic decision-making
                decision = await self._basic_decision_making(context)
                decision['method'] = 'basic_fallback'
            
            # Store decision in memory
            await self._store_memory('decision', {
                'context': context,
                'decision': decision,
                'timestamp': datetime.now().isoformat()
            })
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Enhanced decision-making failed: {e}")
            return await self._basic_decision_making(context)
    
    async def _basic_decision_making(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Basic decision-making fallback."""
        return {
            'action': 'analyze_and_wait',
            'confidence': 0.6,
            'reasoning': ['Basic analysis of context'],
            'method': 'basic'
        }
    
    async def _store_memory(self, key: str, value: Any):
        """Store memory in both local and Redis."""
        try:
            # Store locally
            self.memory[key] = value
            
            # Store in Redis if available
            if self.redis_service.is_connected():
                self.redis_service.set_memory(self.agent_id, key, value)
                
            # Add to RAGlight knowledge base
            if self.raglight_service.initialized:
                self.raglight_service.add_memory_context(self.agent_id, {key: value})
                
        except Exception as e:
            self.logger.error(f"Failed to store memory: {e}")
    
    async def _retrieve_memory(self, key: str) -> Any:
        """Retrieve memory from Redis or local storage."""
        try:
            # Try Redis first
            if self.redis_service.is_connected():
                value = self.redis_service.get_memory(self.agent_id, key)
                if value is not None:
                    return value
            
            # Fallback to local memory
            return self.memory.get(key)
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve memory: {e}")
            return self.memory.get(key)
    
    async def _self_improvement_cycle(self):
        """Enhanced self-improvement using RAGlight analysis."""
        try:
            # Analyze performance using RAGlight
            performance_query = f"Analyze agent performance: accuracy={self.decision_accuracy}, tasks_completed={len(self.completed_tasks)}"
            
            if self.raglight_service.initialized:
                analysis = self.raglight_service.query_agentic_rag(
                    performance_query,
                    "Provide recommendations for improving agent performance and learning"
                )
                
                # Extract improvement recommendations
                recommendations = analysis.get('response', '')
                
                # Apply improvements
                if 'increase learning rate' in recommendations.lower():
                    self.learning_rate = min(self.learning_rate * 1.1, 0.1)
                    self.logger.info(f"Increased learning rate to {self.learning_rate}")
                
                if 'improve decision accuracy' in recommendations.lower():
                    # Implement decision accuracy improvements
                    self.consciousness_level = min(self.consciousness_level + 0.01, 1.0)
                    self.logger.info(f"Enhanced consciousness level to {self.consciousness_level}")
                
                # Store improvement cycle results
                await self._store_memory('last_improvement', {
                    'timestamp': datetime.now().isoformat(),
                    'analysis': analysis,
                    'learning_rate': self.learning_rate,
                    'consciousness_level': self.consciousness_level
                })
            
            # Save updated state
            await self._save_agent_state()
            
        except Exception as e:
            self.logger.error(f"Self-improvement cycle failed: {e}")
    
    def get_enhanced_status(self) -> Dict[str, Any]:
        """Get enhanced agent status including Redis and RAGlight info."""
        base_status = self.get_status()
        
        # Add Redis status
        redis_status = {
            'connected': self.redis_service.is_connected() if self.redis_service else False,
            'stats': self.redis_service.get_stats() if self.redis_service and self.redis_service.is_connected() else {}
        }
        
        # Add RAGlight status
        raglight_status = {
            'initialized': self.raglight_service.initialized if self.raglight_service else False,
            'stats': self.raglight_service.get_knowledge_base_stats() if self.raglight_service else {}
        }
        
        return {
            **base_status,
            'redis': redis_status,
            'raglight': raglight_status,
            'enhanced_features': True
        }

