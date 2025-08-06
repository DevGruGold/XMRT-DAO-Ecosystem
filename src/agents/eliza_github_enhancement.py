"""
Eliza GitHub Enhancement Module

This module extends the existing Eliza agent with GitHub integration capabilities,
enabling autonomous development and deployment of new utilities.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from github_integration_module import GitHubIntegrationService

class ElizaGitHubEnhancement:
    """
    Enhancement module that adds GitHub capabilities to Eliza agent
    """
    
    def __init__(self, eliza_agent, config: Dict[str, Any]):
        self.eliza_agent = eliza_agent
        self.config = config
        self.logger = self._setup_logging()
        
        # Initialize GitHub integration service
        self.github_service = GitHubIntegrationService(config.get('github', {}))
        
        # Track autonomous development activities
        self.development_history = []
        self.active_projects = []
        
        self.logger.info("Eliza GitHub Enhancement initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the enhancement"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def analyze_ecosystem_needs(self) -> List[str]:
        """
        Analyze the XMRT-DAO-Ecosystem to identify potential improvements
        
        Returns:
            List of improvement suggestions
        """
        try:
            # Get current repository information
            repo_info = self.github_service.get_repository_info()
            
            # Analyze based on Eliza's current capabilities and ecosystem state
            suggestions = []
            
            # Check mining performance and suggest optimizations
            if hasattr(self.eliza_agent, 'mining_service'):
                mining_stats = await self.eliza_agent.mining_service.get_current_stats()
                if mining_stats.get('efficiency', 0) < 0.8:
                    suggestions.append(
                        "Mining efficiency optimization utility to improve hash rate distribution and reduce latency"
                    )
            
            # Check treasury management
            if hasattr(self.eliza_agent, 'treasury_service'):
                treasury_health = await self.eliza_agent.treasury_service.get_health_metrics()
                if treasury_health.get('diversification_score', 0) < 0.7:
                    suggestions.append(
                        "Treasury diversification analyzer to optimize asset allocation and risk management"
                    )
            
            # Check governance participation
            if hasattr(self.eliza_agent, 'governance_service'):
                governance_metrics = await self.eliza_agent.governance_service.get_participation_metrics()
                if governance_metrics.get('participation_rate', 0) < 0.9:
                    suggestions.append(
                        "Governance participation enhancer to improve voting efficiency and proposal analysis"
                    )
            
            # Always suggest monitoring improvements
            suggestions.append(
                "Real-time ecosystem health monitor with predictive analytics and automated alerting"
            )
            
            # Suggest MESHNET enhancements
            suggestions.append(
                "MESHNET node discovery optimizer to improve network connectivity and reduce latency"
            )
            
            self.logger.info(f"Identified {len(suggestions)} potential ecosystem improvements")
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to analyze ecosystem needs: {e}")
            return []
    
    async def autonomous_development_cycle(self) -> Dict[str, Any]:
        """
        Execute a complete autonomous development cycle
        
        Returns:
            Results of the development cycle
        """
        try:
            self.logger.info("Starting autonomous development cycle...")
            
            # Step 1: Analyze ecosystem needs
            improvement_suggestions = await self.analyze_ecosystem_needs()
            
            if not improvement_suggestions:
                return {
                    'success': True,
                    'message': 'No immediate improvements identified',
                    'developments': []
                }
            
            # Step 2: Prioritize suggestions based on Eliza's decision criteria
            prioritized_suggestions = self._prioritize_suggestions(improvement_suggestions)
            
            # Step 3: Develop the top priority utility
            top_suggestion = prioritized_suggestions[0]
            self.logger.info(f"Developing utility: {top_suggestion}")
            
            development_result = self.github_service.autonomous_utility_development(top_suggestion)
            
            # Step 4: Track the development
            if development_result['success']:
                self.development_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'specification': top_suggestion,
                    'branch_name': development_result['branch_name'],
                    'pull_request_url': development_result['pull_request_url'],
                    'status': 'pending_review'
                })
                
                self.active_projects.append({
                    'name': development_result['file_path'],
                    'branch': development_result['branch_name'],
                    'pr_number': development_result['pull_request_number'],
                    'created_at': datetime.now().isoformat()
                })
            
            return {
                'success': development_result['success'],
                'development_result': development_result,
                'total_suggestions': len(improvement_suggestions),
                'developed_suggestion': top_suggestion
            }
            
        except Exception as e:
            self.logger.error(f"Autonomous development cycle failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _prioritize_suggestions(self, suggestions: List[str]) -> List[str]:
        """
        Prioritize improvement suggestions based on Eliza's decision criteria
        
        Args:
            suggestions: List of improvement suggestions
        
        Returns:
            Prioritized list of suggestions
        """
        # Simple prioritization based on keywords and Eliza's criteria
        priority_keywords = {
            'mining': 0.20,  # Mining performance weight
            'treasury': 0.25,  # Treasury health weight
            'governance': 0.20,  # Governance participation weight
            'monitor': 0.15,  # Monitoring importance
            'meshnet': 0.10,  # MESHNET priority
            'security': 0.30,  # Security is always high priority
            'optimization': 0.25  # Optimization is important
        }
        
        scored_suggestions = []
        for suggestion in suggestions:
            score = 0
            suggestion_lower = suggestion.lower()
            
            for keyword, weight in priority_keywords.items():
                if keyword in suggestion_lower:
                    score += weight
            
            scored_suggestions.append((score, suggestion))
        
        # Sort by score (descending)
        scored_suggestions.sort(key=lambda x: x[0], reverse=True)
        
        return [suggestion for score, suggestion in scored_suggestions]
    
    async def monitor_active_projects(self) -> Dict[str, Any]:
        """
        Monitor active development projects and their status
        
        Returns:
            Status of active projects
        """
        try:
            project_statuses = []
            
            for project in self.active_projects:
                # Get pull request status
                prs = self.github_service.get_pull_requests(state="all")
                pr_status = None
                
                for pr in prs:
                    if pr['number'] == project['pr_number']:
                        pr_status = {
                            'state': pr['state'],
                            'merged': pr.get('merged', False),
                            'mergeable': pr.get('mergeable'),
                            'comments': pr.get('comments', 0),
                            'review_comments': pr.get('review_comments', 0)
                        }
                        break
                
                project_statuses.append({
                    'project': project,
                    'pr_status': pr_status
                })
            
            return {
                'success': True,
                'active_projects_count': len(self.active_projects),
                'project_statuses': project_statuses
            }
            
        except Exception as e:
            self.logger.error(f"Failed to monitor active projects: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def suggest_repository_improvements(self) -> List[str]:
        """
        Suggest improvements to the repository itself
        
        Returns:
            List of repository improvement suggestions
        """
        suggestions = []
        
        try:
            # Get repository information
            repo_info = self.github_service.get_repository_info()
            
            # Check for missing documentation
            if not repo_info.get('has_wiki'):
                suggestions.append("Enable and populate repository wiki with comprehensive documentation")
            
            # Check for missing GitHub Actions
            suggestions.append("Implement automated testing and deployment workflows using GitHub Actions")
            
            # Suggest security improvements
            suggestions.append("Add security scanning and dependency vulnerability checks")
            
            # Suggest code quality improvements
            suggestions.append("Implement code quality checks and automated formatting")
            
            # Suggest monitoring improvements
            suggestions.append("Add comprehensive logging and monitoring for deployed services")
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to suggest repository improvements: {e}")
            return []
    
    def get_development_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all autonomous development activities
        
        Returns:
            Development activity summary
        """
        return {
            'total_developments': len(self.development_history),
            'active_projects': len(self.active_projects),
            'development_history': self.development_history[-10:],  # Last 10 developments
            'active_projects_list': self.active_projects,
            'last_development': self.development_history[-1] if self.development_history else None
        }
    
    async def execute_github_spark_workflow(self, user_request: str) -> Dict[str, Any]:
        """
        Execute a GitHub Spark-like workflow for user requests
        
        Args:
            user_request: Natural language request for new functionality
        
        Returns:
            Workflow execution result
        """
        try:
            self.logger.info(f"Executing GitHub Spark workflow for request: {user_request}")
            
            # Generate detailed specification from user request
            enhanced_specification = f"""
            User Request: {user_request}
            
            Context: XMRT-DAO-Ecosystem enhancement
            
            Requirements:
            - Integrate with existing XMRT ecosystem components
            - Follow established patterns in the codebase
            - Include proper error handling and logging
            - Ensure compatibility with Redis, mining services, and MESHNET
            - Add appropriate documentation and comments
            - Consider security implications
            - Optimize for performance and scalability
            
            Implementation should be production-ready and follow the existing architecture patterns.
            """
            
            # Execute autonomous development
            result = self.github_service.autonomous_utility_development(enhanced_specification)
            
            if result['success']:
                self.logger.info(f"Successfully created utility for request: {user_request}")
                
                # Add to tracking
                self.development_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'user_request': user_request,
                    'specification': enhanced_specification,
                    'branch_name': result['branch_name'],
                    'pull_request_url': result['pull_request_url'],
                    'status': 'pending_review',
                    'type': 'user_requested'
                })
            
            return result
            
        except Exception as e:
            self.logger.error(f"GitHub Spark workflow failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

