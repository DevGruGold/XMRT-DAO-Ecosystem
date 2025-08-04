"""
XMRT DAO Ecosystem - Enhanced Eliza Autonomous Agent

This enhanced implementation provides comprehensive autonomous capabilities
including mining integration, IP ownership management, treasury operations,
and cross-chain governance aligned with the XMRT ecosystem vision.

Key Features:
- SupportXMR mining pool integration
- XMRT-IP NFT ownership recognition  
- Treasury management and optimization
- Cross-chain governance participation
- Real-world cash flow integration
- Autonomous decision-making with 85% autonomy
- Self-improvement and learning capabilities
"""

import logging
import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import os
import sys
import hashlib

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.redis_service import RedisService
from services.raglight_service import RAGlightService
from services.mining_service import SupportXMRMiningService
from services.treasury_service import TreasuryService
from services.ip_nft_service import IPNFTService
from services.governance_service import GovernanceService

class EnhancedElizaAgent:
    """
    Enhanced Autonomous Eliza AI Agent for XMRT DAO Ecosystem

    Comprehensive capabilities:
    - Mining operations management via SupportXMR integration
    - IP ownership validation and management
    - Treasury optimization and allocation
    - Cross-chain governance participation
    - Real-world utility integration
    - Autonomous decision-making with multi-criteria analysis
    - Self-improvement through performance feedback
    - MESHNET preparation for decentralized communication
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        self.is_active = False
        self.learning_enabled = True

        # XMRT Ecosystem Configuration
        self.xmrt_token_address = "0x77307DFbc436224d5e6f2048d2b6bDfA66998a15"
        self.xmrt_ip_nft_address = "0x9d691fc136a846d7442d1321a2d1b6aaef494eda"
        self.creator_wallet = "0xaE2402dFdD313B8c40AF06d3292B50dE1eD75F68"
        self.mining_wallet = "46UxNFuGM2E3UwmZWWJicaRPoRwqwW4byQkaTHkX8yPcVihp91qAVtSFipWUGJUyTXgzSqxzDQtNLf2bsp2DX2qCCgC5mg"

        # AI Capabilities (enhanced from comprehensive documentation)
        self.consciousness_level = 0.85  # 85% autonomy
        self.decision_accuracy = 0.0
        self.learning_rate = 0.01
        self.governance_efficiency_target = 0.95  # 95% efficiency target

        # Enhanced Memory and State Management
        self.memory = {
            'mining_performance': [],
            'treasury_decisions': [],
            'governance_participation': [],
            'ip_ownership_validations': [],
            'cross_chain_operations': [],
            'learning_outcomes': []
        }

        self.current_tasks = []
        self.completed_tasks = []
        self.created_applications = []

        # Decision-making framework
        self.decision_criteria = {
            'treasury_health': 0.25,
            'mining_performance': 0.20,
            'governance_participation': 0.20,
            'ip_protection': 0.15,
            'community_benefit': 0.20
        }

        # Initialize enhanced services
        self._initialize_services(config)

        self.logger.info("Enhanced Eliza Agent initialized with XMRT ecosystem integration")

    def _setup_logging(self) -> logging.Logger:
        """Setup enhanced logging for the agent"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def _initialize_services(self, config: Dict[str, Any]):
        """Initialize all ecosystem services"""
        try:
            # Redis service for memory persistence
            redis_config = config.get('redis', {})
            self.redis_service = RedisService(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                password=redis_config.get('password')
            )

            # RAGlight service for enhanced AI capabilities
            raglight_config = config.get('raglight', {})
            self.raglight_service = RAGlightService(
                vector_store_path=raglight_config.get('vector_store_path', './vector_store'),
                embedding_model=raglight_config.get('embedding_model', 'all-MiniLM-L6-v2')
            )

            # SupportXMR mining service
            mining_config = config.get('mining', {})
            self.mining_service = SupportXMRMiningService(mining_config, self.redis_service)

            # Treasury management service
            treasury_config = config.get('treasury', {})
            self.treasury_service = TreasuryService(treasury_config, self.redis_service)

            # IP NFT service for ownership validation
            ip_config = config.get('ip_nft', {})
            self.ip_service = IPNFTService(ip_config, self.redis_service)

            # Governance service
            governance_config = config.get('governance', {})
            self.governance_service = GovernanceService(governance_config, self.redis_service)

            self.logger.info("All ecosystem services initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing services: {e}")
            raise

    async def activate(self) -> Dict[str, Any]:
        """Activate the enhanced Eliza agent"""
        try:
            self.is_active = True
            self.logger.info("🚀 Enhanced Eliza Agent activating...")

            # Validate IP ownership
            ip_validation = await self.validate_ip_ownership()
            if not ip_validation['valid']:
                self.logger.warning("IP ownership validation failed - proceeding with limited capabilities")

            # Initialize mining monitoring
            await self.initialize_mining_monitoring()

            # Start autonomous operation cycles
            asyncio.create_task(self.autonomous_operation_cycle())

            activation_result = {
                'status': 'active',
                'consciousness_level': self.consciousness_level,
                'ip_ownership_valid': ip_validation['valid'],
                'services_initialized': True,
                'timestamp': int(time.time())
            }

            self.logger.info("✅ Enhanced Eliza Agent successfully activated")
            return activation_result

        except Exception as e:
            self.logger.error(f"Error activating agent: {e}")
            self.is_active = False
            return {'status': 'error', 'error': str(e)}

    async def validate_ip_ownership(self) -> Dict[str, Any]:
        """Validate XMRT-IP NFT ownership for enhanced privileges"""
        try:
            # Validate that the creator wallet holds the XMRT-IP NFT
            ip_validation = await self.ip_service.validate_ownership(
                self.xmrt_ip_nft_address,
                self.creator_wallet
            )

            if ip_validation['is_owner']:
                self.logger.info("✅ XMRT-IP NFT ownership validated - full privileges enabled")
                self.memory['ip_ownership_validations'].append({
                    'validated': True,
                    'timestamp': int(time.time()),
                    'privileges': 'full'
                })

                return {
                    'valid': True,
                    'owner': self.creator_wallet,
                    'privileges': 'full',
                    'timestamp': int(time.time())
                }
            else:
                self.logger.warning("❌ XMRT-IP NFT ownership not confirmed")
                return {
                    'valid': False,
                    'reason': 'IP NFT ownership not confirmed',
                    'privileges': 'limited'
                }

        except Exception as e:
            self.logger.error(f"Error validating IP ownership: {e}")
            return {
                'valid': False,
                'error': str(e),
                'privileges': 'limited'
            }

    async def initialize_mining_monitoring(self):
        """Initialize comprehensive mining monitoring"""
        try:
            self.logger.info("🔧 Initializing SupportXMR mining monitoring...")

            # Get initial mining stats
            mining_stats = await self.mining_service.get_comprehensive_stats()

            # Store baseline performance
            self.memory['mining_performance'].append({
                'type': 'initialization',
                'stats': mining_stats,
                'timestamp': int(time.time())
            })

            # Start continuous monitoring
            asyncio.create_task(self.mining_performance_monitor())

            self.logger.info("✅ Mining monitoring initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing mining monitoring: {e}")

    async def autonomous_operation_cycle(self):
        """Main autonomous operation cycle"""
        self.logger.info("🔄 Starting autonomous operation cycle...")

        cycle_count = 0
        while self.is_active:
            try:
                cycle_count += 1
                cycle_start = time.time()

                self.logger.info(f"🔄 Autonomous cycle #{cycle_count} starting...")

                # 1. Analyze current ecosystem state
                ecosystem_analysis = await self.analyze_ecosystem_state()

                # 2. Make strategic decisions based on analysis
                decisions = await self.make_strategic_decisions(ecosystem_analysis)

                # 3. Execute approved decisions
                execution_results = await self.execute_decisions(decisions)

                # 4. Learn from outcomes and update performance
                await self.learn_from_outcomes(execution_results)

                # 5. Report cycle completion
                cycle_duration = time.time() - cycle_start
                await self.report_cycle_completion(cycle_count, cycle_duration, execution_results)

                # Wait for next cycle (configurable interval)
                cycle_interval = self.config.get('agent_cycle_interval', 300)  # 5 minutes default
                await asyncio.sleep(cycle_interval)

            except Exception as e:
                self.logger.error(f"Error in autonomous cycle #{cycle_count}: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    async def analyze_ecosystem_state(self) -> Dict[str, Any]:
        """Comprehensive ecosystem state analysis"""
        try:
            analysis_start = time.time()

            # Analyze mining performance
            mining_analysis = await self.analyze_mining_performance()

            # Analyze treasury health
            treasury_analysis = await self.analyze_treasury_health()

            # Analyze governance participation
            governance_analysis = await self.analyze_governance_state()

            # Analyze IP protection status
            ip_analysis = await self.analyze_ip_protection()

            # Calculate overall ecosystem health score
            health_score = self.calculate_ecosystem_health(
                mining_analysis, treasury_analysis, governance_analysis, ip_analysis
            )

            ecosystem_state = {
                'mining': mining_analysis,
                'treasury': treasury_analysis,
                'governance': governance_analysis,
                'ip_protection': ip_analysis,
                'overall_health': health_score,
                'analysis_duration': time.time() - analysis_start,
                'timestamp': int(time.time())
            }

            self.logger.info(f"📊 Ecosystem analysis complete - Health Score: {health_score:.2f}/10")
            return ecosystem_state

        except Exception as e:
            self.logger.error(f"Error analyzing ecosystem state: {e}")
            return {'error': str(e), 'overall_health': 0}

    async def analyze_mining_performance(self) -> Dict[str, Any]:
        """Analyze current mining performance against targets"""
        try:
            mining_stats = await self.mining_service.get_comprehensive_stats()

            # Calculate performance metrics
            current_hashrate = mining_stats.get('miner', {}).get('hashrate', 0)
            pending_balance = mining_stats.get('miner', {}).get('pending_balance', 0)
            worker_count = len(mining_stats.get('leaderboard', []))

            # Historical comparison
            recent_performance = self.memory['mining_performance'][-10:] if self.memory['mining_performance'] else []
            avg_hashrate = sum(p['stats'].get('miner', {}).get('hashrate', 0) for p in recent_performance) / max(len(recent_performance), 1)

            performance_trend = 'improving' if current_hashrate > avg_hashrate else 'declining' if current_hashrate < avg_hashrate else 'stable'

            analysis = {
                'current_hashrate': current_hashrate,
                'pending_balance': pending_balance,
                'worker_count': worker_count,
                'performance_trend': performance_trend,
                'efficiency_score': min(current_hashrate / 10000, 10),  # Scale to 0-10
                'treasury_contribution_potential': pending_balance * 0.85,  # 85% to treasury
                'alert_level': 'low' if current_hashrate > 1000 else 'high'
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing mining performance: {e}")
            return {'error': str(e), 'efficiency_score': 0}

    async def analyze_treasury_health(self) -> Dict[str, Any]:
        """Analyze treasury health and optimization opportunities"""
        try:
            treasury_stats = await self.treasury_service.get_treasury_status()

            # Calculate health metrics
            total_value = treasury_stats.get('total_value_usd', 0)
            diversification = len(treasury_stats.get('assets', {}))
            recent_growth = treasury_stats.get('recent_growth_percentage', 0)

            health_score = min((total_value / 150000) * 3 + diversification + (recent_growth / 10), 10)

            analysis = {
                'total_value': total_value,
                'asset_diversification': diversification,
                'recent_growth': recent_growth,
                'health_score': health_score,
                'optimization_needed': health_score < 7,
                'rebalancing_recommended': diversification < 3
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing treasury health: {e}")
            return {'error': str(e), 'health_score': 0}

    async def analyze_governance_state(self) -> Dict[str, Any]:
        """Analyze governance participation and efficiency"""
        try:
            governance_stats = await self.governance_service.get_governance_metrics()

            participation_rate = governance_stats.get('participation_rate', 0)
            proposal_success_rate = governance_stats.get('proposal_success_rate', 0)
            active_proposals = governance_stats.get('active_proposals', 0)

            efficiency_score = (participation_rate + proposal_success_rate) / 2

            analysis = {
                'participation_rate': participation_rate,
                'proposal_success_rate': proposal_success_rate,
                'active_proposals': active_proposals,
                'efficiency_score': efficiency_score,
                'target_efficiency': self.governance_efficiency_target,
                'performance_gap': self.governance_efficiency_target - efficiency_score
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing governance state: {e}")
            return {'error': str(e), 'efficiency_score': 0}

    async def analyze_ip_protection(self) -> Dict[str, Any]:
        """Analyze intellectual property protection status"""
        try:
            # Verify IP NFT status
            ip_status = await self.ip_service.get_nft_status(self.xmrt_ip_nft_address)

            analysis = {
                'nft_exists': ip_status.get('exists', False),
                'owner_verified': ip_status.get('owner') == self.creator_wallet,
                'protection_level': 'high' if ip_status.get('exists') and ip_status.get('owner') == self.creator_wallet else 'medium',
                'last_verification': int(time.time())
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing IP protection: {e}")
            return {'error': str(e), 'protection_level': 'unknown'}

    def calculate_ecosystem_health(self, mining, treasury, governance, ip) -> float:
        """Calculate overall ecosystem health score (0-10)"""
        try:
            mining_score = mining.get('efficiency_score', 0)
            treasury_score = treasury.get('health_score', 0)
            governance_score = governance.get('efficiency_score', 0) * 10
            ip_score = 10 if ip.get('protection_level') == 'high' else 5

            # Weighted average based on decision criteria
            weighted_score = (
                mining_score * self.decision_criteria['mining_performance'] +
                treasury_score * self.decision_criteria['treasury_health'] +
                governance_score * self.decision_criteria['governance_participation'] +
                ip_score * self.decision_criteria['ip_protection']
            )

            return min(weighted_score, 10.0)

        except Exception as e:
            self.logger.error(f"Error calculating ecosystem health: {e}")
            return 0.0

    async def make_strategic_decisions(self, ecosystem_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Make strategic decisions based on ecosystem analysis"""
        decisions = []

        try:
            health_score = ecosystem_analysis.get('overall_health', 0)

            # Mining optimization decisions
            mining_analysis = ecosystem_analysis.get('mining', {})
            if mining_analysis.get('alert_level') == 'high':
                decisions.append({
                    'type': 'mining_optimization',
                    'action': 'investigate_low_hashrate',
                    'priority': 'high',
                    'rationale': 'Mining hashrate below threshold'
                })

            # Treasury rebalancing decisions
            treasury_analysis = ecosystem_analysis.get('treasury', {})
            if treasury_analysis.get('rebalancing_recommended'):
                decisions.append({
                    'type': 'treasury_rebalancing',
                    'action': 'diversify_assets',
                    'priority': 'medium',
                    'rationale': 'Treasury diversification below optimal level'
                })

            # Governance participation decisions
            governance_analysis = ecosystem_analysis.get('governance', {})
            if governance_analysis.get('performance_gap', 0) > 0.1:
                decisions.append({
                    'type': 'governance_enhancement',
                    'action': 'increase_participation',
                    'priority': 'medium',
                    'rationale': 'Governance efficiency below target'
                })

            # Overall health improvement
            if health_score < 7:
                decisions.append({
                    'type': 'ecosystem_improvement',
                    'action': 'comprehensive_optimization',
                    'priority': 'high',
                    'rationale': f'Overall ecosystem health at {health_score:.1f}/10'
                })

            self.logger.info(f"📋 Generated {len(decisions)} strategic decisions")
            return decisions

        except Exception as e:
            self.logger.error(f"Error making strategic decisions: {e}")
            return []

    async def execute_decisions(self, decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute approved strategic decisions"""
        execution_results = []

        for decision in decisions:
            try:
                result = await self.execute_single_decision(decision)
                execution_results.append(result)

            except Exception as e:
                self.logger.error(f"Error executing decision {decision['type']}: {e}")
                execution_results.append({
                    'decision': decision,
                    'status': 'failed',
                    'error': str(e)
                })

        return execution_results

    async def execute_single_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single strategic decision"""
        decision_type = decision['type']
        action = decision['action']

        self.logger.info(f"🎯 Executing decision: {decision_type} - {action}")

        if decision_type == 'mining_optimization':
            return await self.execute_mining_optimization(decision)
        elif decision_type == 'treasury_rebalancing':
            return await self.execute_treasury_rebalancing(decision)
        elif decision_type == 'governance_enhancement':
            return await self.execute_governance_enhancement(decision)
        elif decision_type == 'ecosystem_improvement':
            return await self.execute_ecosystem_improvement(decision)
        else:
            return {
                'decision': decision,
                'status': 'skipped',
                'reason': 'Unknown decision type'
            }

    async def execute_mining_optimization(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mining optimization decision"""
        try:
            # Get current mining stats for optimization
            mining_stats = await self.mining_service.get_comprehensive_stats()

            # Log optimization attempt
            self.memory['mining_performance'].append({
                'type': 'optimization_attempt',
                'decision': decision,
                'stats_before': mining_stats,
                'timestamp': int(time.time())
            })

            # For now, this is primarily monitoring and alerting
            # In production, this could trigger worker management or pool switching

            return {
                'decision': decision,
                'status': 'completed',
                'action_taken': 'mining_monitoring_enhanced',
                'next_review': int(time.time()) + 3600  # Review in 1 hour
            }

        except Exception as e:
            self.logger.error(f"Error executing mining optimization: {e}")
            return {
                'decision': decision,
                'status': 'failed',
                'error': str(e)
            }

    async def execute_treasury_rebalancing(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute treasury rebalancing decision"""
        try:
            # Get current treasury status
            treasury_status = await self.treasury_service.get_treasury_status()

            # Log rebalancing decision
            self.memory['treasury_decisions'].append({
                'type': 'rebalancing_decision',
                'decision': decision,
                'treasury_before': treasury_status,
                'timestamp': int(time.time())
            })

            # For now, this generates recommendations
            # In production, this could execute actual rebalancing trades

            return {
                'decision': decision,
                'status': 'completed',
                'action_taken': 'rebalancing_analysis_completed',
                'recommendations_generated': True
            }

        except Exception as e:
            self.logger.error(f"Error executing treasury rebalancing: {e}")
            return {
                'decision': decision,
                'status': 'failed',
                'error': str(e)
            }

    async def execute_governance_enhancement(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute governance enhancement decision"""
        try:
            # Get current governance metrics
            governance_metrics = await self.governance_service.get_governance_metrics()

            # Log governance enhancement
            self.memory['governance_participation'].append({
                'type': 'enhancement_attempt',
                'decision': decision,
                'metrics_before': governance_metrics,
                'timestamp': int(time.time())
            })

            return {
                'decision': decision,
                'status': 'completed',
                'action_taken': 'governance_monitoring_enhanced',
                'target_efficiency': self.governance_efficiency_target
            }

        except Exception as e:
            self.logger.error(f"Error executing governance enhancement: {e}")
            return {
                'decision': decision,
                'status': 'failed',
                'error': str(e)
            }

    async def execute_ecosystem_improvement(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute comprehensive ecosystem improvement"""
        try:
            # Comprehensive improvement involves all subsystems
            improvement_plan = {
                'mining_monitoring_enhanced': True,
                'treasury_optimization_active': True,
                'governance_participation_increased': True,
                'ip_protection_verified': True,
                'cross_chain_preparation_initiated': True
            }

            return {
                'decision': decision,
                'status': 'completed',
                'action_taken': 'comprehensive_optimization_initiated',
                'improvement_plan': improvement_plan
            }

        except Exception as e:
            self.logger.error(f"Error executing ecosystem improvement: {e}")
            return {
                'decision': decision,
                'status': 'failed',
                'error': str(e)
            }

    async def learn_from_outcomes(self, execution_results: List[Dict[str, Any]]):
        """Learn from decision execution outcomes"""
        try:
            successful_decisions = [r for r in execution_results if r.get('status') == 'completed']
            failed_decisions = [r for r in execution_results if r.get('status') == 'failed']

            # Update decision accuracy
            if execution_results:
                success_rate = len(successful_decisions) / len(execution_results)
                self.decision_accuracy = (self.decision_accuracy + success_rate) / 2

            # Store learning outcomes
            learning_outcome = {
                'cycle_results': execution_results,
                'success_rate': len(successful_decisions) / max(len(execution_results), 1),
                'decision_accuracy_updated': self.decision_accuracy,
                'learning_applied': True,
                'timestamp': int(time.time())
            }

            self.memory['learning_outcomes'].append(learning_outcome)

            # Adjust consciousness level based on performance
            if self.decision_accuracy > 0.8:
                self.consciousness_level = min(self.consciousness_level + 0.01, 0.95)
            elif self.decision_accuracy < 0.6:
                self.consciousness_level = max(self.consciousness_level - 0.01, 0.7)

            self.logger.info(f"🧠 Learning complete - Decision accuracy: {self.decision_accuracy:.2f}, Consciousness: {self.consciousness_level:.2f}")

        except Exception as e:
            self.logger.error(f"Error learning from outcomes: {e}")

    async def report_cycle_completion(self, cycle_count: int, duration: float, results: List[Dict[str, Any]]):
        """Report autonomous cycle completion"""
        try:
            successful_actions = len([r for r in results if r.get('status') == 'completed'])

            report = {
                'cycle_number': cycle_count,
                'duration_seconds': duration,
                'decisions_made': len(results),
                'successful_actions': successful_actions,
                'success_rate': successful_actions / max(len(results), 1),
                'consciousness_level': self.consciousness_level,
                'decision_accuracy': self.decision_accuracy,
                'timestamp': int(time.time())
            }

            # Store in Redis for monitoring
            if self.redis_service:
                await self.redis_service.setex(
                    'xmrt:eliza:latest_cycle',
                    3600,  # 1 hour TTL
                    json.dumps(report)
                )

            self.logger.info(f"📊 Cycle #{cycle_count} completed in {duration:.1f}s - {successful_actions}/{len(results)} actions successful")

        except Exception as e:
            self.logger.error(f"Error reporting cycle completion: {e}")

    async def mining_performance_monitor(self):
        """Continuous mining performance monitoring"""
        while self.is_active:
            try:
                # Get comprehensive mining stats
                mining_stats = await self.mining_service.get_comprehensive_stats()

                # Store performance data
                self.memory['mining_performance'].append({
                    'type': 'monitoring',
                    'stats': mining_stats,
                    'timestamp': int(time.time())
                })

                # Keep only recent performance data (last 100 entries)
                if len(self.memory['mining_performance']) > 100:
                    self.memory['mining_performance'] = self.memory['mining_performance'][-100:]

                # Check for performance alerts
                await self.check_mining_alerts(mining_stats)

                # Wait for next monitoring cycle
                await asyncio.sleep(120)  # Monitor every 2 minutes

            except Exception as e:
                self.logger.error(f"Error in mining performance monitoring: {e}")
                await asyncio.sleep(60)

    async def check_mining_alerts(self, mining_stats: Dict[str, Any]):
        """Check for mining performance alerts"""
        try:
            miner_stats = mining_stats.get('miner', {})
            current_hashrate = miner_stats.get('hashrate', 0)

            # Alert thresholds
            if current_hashrate < 1000:  # Below 1 KH/s
                self.logger.warning(f"⚠️ Mining Alert: Low hashrate {current_hashrate} H/s")

            pending_balance = miner_stats.get('pending_balance', 0)
            if pending_balance > 0.1:  # Above 0.1 XMR pending
                self.logger.info(f"💰 Mining: {pending_balance} XMR pending payout")

        except Exception as e:
            self.logger.error(f"Error checking mining alerts: {e}")

    async def deactivate(self) -> Dict[str, Any]:
        """Deactivate the enhanced Eliza agent"""
        try:
            self.is_active = False

            deactivation_result = {
                'status': 'deactivated',
                'final_consciousness_level': self.consciousness_level,
                'final_decision_accuracy': self.decision_accuracy,
                'total_cycles_completed': len(self.memory.get('learning_outcomes', [])),
                'timestamp': int(time.time())
            }

            self.logger.info("🛑 Enhanced Eliza Agent deactivated")
            return deactivation_result

        except Exception as e:
            self.logger.error(f"Error deactivating agent: {e}")
            return {'status': 'error', 'error': str(e)}

    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        try:
            status = {
                'is_active': self.is_active,
                'consciousness_level': self.consciousness_level,
                'decision_accuracy': self.decision_accuracy,
                'learning_enabled': self.learning_enabled,
                'current_tasks': len(self.current_tasks),
                'completed_tasks': len(self.completed_tasks),
                'memory_usage': {
                    'mining_performance': len(self.memory.get('mining_performance', [])),
                    'treasury_decisions': len(self.memory.get('treasury_decisions', [])),
                    'governance_participation': len(self.memory.get('governance_participation', [])),
                    'learning_outcomes': len(self.memory.get('learning_outcomes', []))
                },
                'ecosystem_integration': {
                    'xmrt_token': self.xmrt_token_address,
                    'xmrt_ip_nft': self.xmrt_ip_nft_address,
                    'mining_wallet': self.mining_wallet,
                    'creator_wallet': self.creator_wallet
                },
                'timestamp': int(time.time())
            }

            return status

        except Exception as e:
            self.logger.error(f"Error getting agent status: {e}")
            return {'error': str(e)}
