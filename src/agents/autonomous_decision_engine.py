"""
XMRT-DAO-Ecosystem Autonomous Decision Engine

This module implements sophisticated autonomous decision-making capabilities
that enable Eliza to make complex strategic and operational decisions without
human intervention while maintaining alignment with ecosystem objectives.

Key Features:
- Multi-criteria decision analysis
- Dynamic goal adaptation
- Risk-aware decision making
- Stakeholder preference integration
- Continuous learning and improvement
- Strategic planning and execution
"""

import logging
import asyncio
import json
import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import hashlib
import os

# Decision-making frameworks
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pandas as pd

class DecisionType(Enum):
    """Types of decisions the autonomous system can make"""
    MINING_OPTIMIZATION = "mining_optimization"
    TREASURY_REBALANCING = "treasury_rebalancing"
    GOVERNANCE_PARTICIPATION = "governance_participation"
    STRATEGIC_INITIATIVE = "strategic_initiative"
    RISK_MITIGATION = "risk_mitigation"
    RESOURCE_ALLOCATION = "resource_allocation"
    EMERGENCY_RESPONSE = "emergency_response"

class DecisionPriority(Enum):
    """Priority levels for autonomous decisions"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class DecisionContext:
    """Context information for decision-making"""
    ecosystem_state: Dict[str, Any]
    market_conditions: Dict[str, Any]
    stakeholder_preferences: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    historical_performance: List[Dict[str, Any]]
    available_resources: Dict[str, Any]
    time_constraints: Optional[Dict[str, Any]] = None

@dataclass
class DecisionOption:
    """Represents a potential decision option"""
    option_id: str
    description: str
    expected_outcomes: Dict[str, float]
    resource_requirements: Dict[str, float]
    risk_level: float
    confidence_score: float
    implementation_complexity: float
    stakeholder_alignment: float

@dataclass
class DecisionResult:
    """Result of an autonomous decision"""
    decision_id: str
    decision_type: DecisionType
    selected_option: DecisionOption
    rationale: str
    confidence_level: float
    expected_impact: Dict[str, float]
    implementation_plan: List[Dict[str, Any]]
    monitoring_metrics: List[str]
    rollback_plan: Optional[Dict[str, Any]] = None

class AutonomousDecisionEngine:
    """
    Advanced autonomous decision-making engine for the XMRT-DAO-Ecosystem
    
    This engine implements sophisticated decision-making capabilities including:
    - Multi-criteria decision analysis (MCDA)
    - Dynamic goal adaptation based on performance
    - Risk-aware decision making with uncertainty quantification
    - Stakeholder preference integration and consensus building
    - Continuous learning from decision outcomes
    - Strategic planning with long-term optimization
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Decision-making parameters
        self.decision_criteria = {
            'financial_impact': 0.25,
            'strategic_alignment': 0.20,
            'risk_level': 0.20,
            'stakeholder_satisfaction': 0.15,
            'implementation_feasibility': 0.10,
            'learning_opportunity': 0.10
        }
        
        # Dynamic goal weights (can be adapted based on performance)
        self.goal_weights = {
            'ecosystem_growth': 0.30,
            'financial_optimization': 0.25,
            'risk_management': 0.20,
            'stakeholder_satisfaction': 0.15,
            'innovation_development': 0.10
        }
        
        # Learning and adaptation parameters
        self.learning_rate = 0.01
        self.adaptation_threshold = 0.1
        self.confidence_threshold = 0.7
        
        # Decision history and learning data
        self.decision_history = []
        self.performance_history = []
        self.stakeholder_feedback = []
        
        # Machine learning models for decision support
        self.outcome_predictor = None
        self.risk_assessor = None
        self.stakeholder_preference_model = None
        
        # Initialize models
        self._initialize_ml_models()
        
        self.logger.info("Autonomous Decision Engine initialized")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the decision engine"""
        logger = logging.getLogger(f"{__name__}.AutonomousDecisionEngine")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    def _initialize_ml_models(self):
        """Initialize machine learning models for decision support"""
        try:
            # Outcome prediction model
            self.outcome_predictor = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            # Risk assessment model
            self.risk_assessor = RandomForestClassifier(
                n_estimators=100,
                max_depth=8,
                random_state=42
            )
            
            # Stakeholder preference model
            self.stakeholder_preference_model = GradientBoostingRegressor(
                n_estimators=50,
                learning_rate=0.1,
                max_depth=4,
                random_state=42
            )
            
            self.logger.info("ML models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing ML models: {e}")
            raise

    async def make_autonomous_decision(
        self, 
        decision_type: DecisionType,
        context: DecisionContext,
        options: List[DecisionOption]
    ) -> DecisionResult:
        """
        Make an autonomous decision using multi-criteria analysis
        
        Args:
            decision_type: Type of decision to make
            context: Decision context and environment information
            options: Available decision options to choose from
            
        Returns:
            DecisionResult with selected option and implementation plan
        """
        try:
            self.logger.info(f"Making autonomous decision: {decision_type.value}")
            
            # Generate decision ID
            decision_id = self._generate_decision_id(decision_type)
            
            # Analyze decision context
            context_analysis = await self._analyze_decision_context(context)
            
            # Evaluate all options
            option_evaluations = await self._evaluate_options(
                options, context, context_analysis
            )
            
            # Select best option using multi-criteria analysis
            selected_option = await self._select_best_option(
                option_evaluations, context_analysis
            )
            
            # Generate implementation plan
            implementation_plan = await self._generate_implementation_plan(
                selected_option, context
            )
            
            # Create rollback plan
            rollback_plan = await self._create_rollback_plan(
                selected_option, context
            )
            
            # Calculate confidence level
            confidence_level = self._calculate_confidence_level(
                selected_option, context_analysis
            )
            
            # Generate rationale
            rationale = self._generate_decision_rationale(
                selected_option, context_analysis, option_evaluations
            )
            
            # Create decision result
            decision_result = DecisionResult(
                decision_id=decision_id,
                decision_type=decision_type,
                selected_option=selected_option,
                rationale=rationale,
                confidence_level=confidence_level,
                expected_impact=selected_option.expected_outcomes,
                implementation_plan=implementation_plan,
                monitoring_metrics=self._define_monitoring_metrics(selected_option),
                rollback_plan=rollback_plan
            )
            
            # Store decision for learning
            await self._store_decision(decision_result, context)
            
            self.logger.info(
                f"Decision made: {decision_id} - {selected_option.description} "
                f"(confidence: {confidence_level:.2f})"
            )
            
            return decision_result
            
        except Exception as e:
            self.logger.error(f"Error making autonomous decision: {e}")
            raise

    async def _analyze_decision_context(self, context: DecisionContext) -> Dict[str, Any]:
        """Analyze the decision context to inform option evaluation"""
        try:
            analysis = {
                'ecosystem_health_score': self._calculate_ecosystem_health(
                    context.ecosystem_state
                ),
                'market_volatility': self._assess_market_volatility(
                    context.market_conditions
                ),
                'stakeholder_alignment': self._assess_stakeholder_alignment(
                    context.stakeholder_preferences
                ),
                'risk_tolerance': self._determine_risk_tolerance(
                    context.risk_assessment
                ),
                'resource_availability': self._assess_resource_availability(
                    context.available_resources
                ),
                'urgency_level': self._assess_urgency(context.time_constraints),
                'historical_performance': self._analyze_historical_performance(
                    context.historical_performance
                )
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing decision context: {e}")
            return {}

    async def _evaluate_options(
        self, 
        options: List[DecisionOption], 
        context: DecisionContext,
        context_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Evaluate all decision options using multiple criteria"""
        try:
            evaluations = []
            
            for option in options:
                evaluation = {
                    'option': option,
                    'scores': {},
                    'weighted_score': 0.0,
                    'risk_adjusted_score': 0.0
                }
                
                # Financial impact score
                evaluation['scores']['financial_impact'] = self._score_financial_impact(
                    option, context_analysis
                )
                
                # Strategic alignment score
                evaluation['scores']['strategic_alignment'] = self._score_strategic_alignment(
                    option, context_analysis
                )
                
                # Risk level score (inverted - lower risk = higher score)
                evaluation['scores']['risk_level'] = 1.0 - min(option.risk_level, 1.0)
                
                # Stakeholder satisfaction score
                evaluation['scores']['stakeholder_satisfaction'] = option.stakeholder_alignment
                
                # Implementation feasibility score
                evaluation['scores']['implementation_feasibility'] = self._score_implementation_feasibility(
                    option, context_analysis
                )
                
                # Learning opportunity score
                evaluation['scores']['learning_opportunity'] = self._score_learning_opportunity(
                    option, context_analysis
                )
                
                # Calculate weighted score
                evaluation['weighted_score'] = sum(
                    evaluation['scores'][criterion] * weight
                    for criterion, weight in self.decision_criteria.items()
                )
                
                # Apply risk adjustment
                risk_adjustment = 1.0 - (option.risk_level * 0.3)
                evaluation['risk_adjusted_score'] = evaluation['weighted_score'] * risk_adjustment
                
                evaluations.append(evaluation)
            
            # Sort by risk-adjusted score
            evaluations.sort(key=lambda x: x['risk_adjusted_score'], reverse=True)
            
            return evaluations
            
        except Exception as e:
            self.logger.error(f"Error evaluating options: {e}")
            return []

    async def _select_best_option(
        self, 
        evaluations: List[Dict[str, Any]], 
        context_analysis: Dict[str, Any]
    ) -> DecisionOption:
        """Select the best option based on evaluation scores and context"""
        try:
            if not evaluations:
                raise ValueError("No options to evaluate")
            
            # Get top options (within 10% of best score)
            best_score = evaluations[0]['risk_adjusted_score']
            threshold = best_score * 0.9
            
            top_options = [
                eval_data for eval_data in evaluations 
                if eval_data['risk_adjusted_score'] >= threshold
            ]
            
            # If multiple top options, apply additional selection criteria
            if len(top_options) > 1:
                selected_evaluation = self._apply_tiebreaker_criteria(
                    top_options, context_analysis
                )
            else:
                selected_evaluation = top_options[0]
            
            return selected_evaluation['option']
            
        except Exception as e:
            self.logger.error(f"Error selecting best option: {e}")
            return evaluations[0]['option'] if evaluations else None

    def _apply_tiebreaker_criteria(
        self, 
        top_options: List[Dict[str, Any]], 
        context_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply tiebreaker criteria when multiple options have similar scores"""
        try:
            # Tiebreaker criteria based on context
            urgency_level = context_analysis.get('urgency_level', 0.5)
            risk_tolerance = context_analysis.get('risk_tolerance', 0.5)
            
            best_option = None
            best_tiebreaker_score = -1
            
            for option_eval in top_options:
                option = option_eval['option']
                
                # Calculate tiebreaker score
                tiebreaker_score = 0
                
                # Prefer higher confidence options
                tiebreaker_score += option.confidence_score * 0.3
                
                # Consider urgency - if urgent, prefer simpler implementation
                if urgency_level > 0.7:
                    tiebreaker_score += (1.0 - option.implementation_complexity) * 0.3
                else:
                    tiebreaker_score += option.implementation_complexity * 0.1
                
                # Consider risk tolerance
                if risk_tolerance > 0.6:
                    tiebreaker_score += option.risk_level * 0.2  # Higher risk tolerance
                else:
                    tiebreaker_score += (1.0 - option.risk_level) * 0.2  # Lower risk tolerance
                
                # Prefer options with better stakeholder alignment
                tiebreaker_score += option.stakeholder_alignment * 0.2
                
                if tiebreaker_score > best_tiebreaker_score:
                    best_tiebreaker_score = tiebreaker_score
                    best_option = option_eval
            
            return best_option or top_options[0]
            
        except Exception as e:
            self.logger.error(f"Error applying tiebreaker criteria: {e}")
            return top_options[0]

    async def _generate_implementation_plan(
        self, 
        option: DecisionOption, 
        context: DecisionContext
    ) -> List[Dict[str, Any]]:
        """Generate detailed implementation plan for selected option"""
        try:
            implementation_plan = []
            
            # Phase 1: Preparation and validation
            implementation_plan.append({
                'phase': 1,
                'name': 'Preparation and Validation',
                'duration_hours': 2,
                'tasks': [
                    'Validate resource availability',
                    'Confirm stakeholder alignment',
                    'Prepare implementation environment',
                    'Set up monitoring and alerting'
                ],
                'success_criteria': [
                    'All resources confirmed available',
                    'Implementation environment ready',
                    'Monitoring systems active'
                ],
                'rollback_triggers': [
                    'Resource unavailability',
                    'Critical system failures'
                ]
            })
            
            # Phase 2: Initial implementation
            implementation_plan.append({
                'phase': 2,
                'name': 'Initial Implementation',
                'duration_hours': 6,
                'tasks': [
                    'Execute primary implementation steps',
                    'Monitor initial performance metrics',
                    'Validate expected outcomes',
                    'Adjust parameters if needed'
                ],
                'success_criteria': [
                    'Implementation completed without errors',
                    'Initial metrics within expected ranges',
                    'No critical issues detected'
                ],
                'rollback_triggers': [
                    'Implementation failures',
                    'Performance below minimum thresholds',
                    'Critical errors or security issues'
                ]
            })
            
            # Phase 3: Monitoring and optimization
            implementation_plan.append({
                'phase': 3,
                'name': 'Monitoring and Optimization',
                'duration_hours': 24,
                'tasks': [
                    'Continuous performance monitoring',
                    'Stakeholder feedback collection',
                    'Performance optimization',
                    'Documentation and reporting'
                ],
                'success_criteria': [
                    'Performance meets or exceeds expectations',
                    'Stakeholder satisfaction maintained',
                    'No significant issues detected'
                ],
                'rollback_triggers': [
                    'Sustained performance degradation',
                    'Significant stakeholder dissatisfaction',
                    'Unexpected negative impacts'
                ]
            })
            
            return implementation_plan
            
        except Exception as e:
            self.logger.error(f"Error generating implementation plan: {e}")
            return []

    async def _create_rollback_plan(
        self, 
        option: DecisionOption, 
        context: DecisionContext
    ) -> Dict[str, Any]:
        """Create rollback plan in case implementation fails"""
        try:
            rollback_plan = {
                'triggers': [
                    'Implementation failure',
                    'Performance below minimum thresholds',
                    'Critical errors or security issues',
                    'Stakeholder intervention request'
                ],
                'steps': [
                    {
                        'step': 1,
                        'action': 'Immediate halt of implementation',
                        'duration_minutes': 5,
                        'validation': 'Confirm implementation stopped'
                    },
                    {
                        'step': 2,
                        'action': 'Restore previous configuration',
                        'duration_minutes': 15,
                        'validation': 'Previous state restored successfully'
                    },
                    {
                        'step': 3,
                        'action': 'Validate system stability',
                        'duration_minutes': 30,
                        'validation': 'All systems operating normally'
                    },
                    {
                        'step': 4,
                        'action': 'Notify stakeholders and log incident',
                        'duration_minutes': 10,
                        'validation': 'Notifications sent and incident logged'
                    }
                ],
                'success_criteria': [
                    'System restored to stable state',
                    'No data loss or corruption',
                    'All stakeholders notified',
                    'Incident properly documented'
                ],
                'estimated_rollback_time_minutes': 60
            }
            
            return rollback_plan
            
        except Exception as e:
            self.logger.error(f"Error creating rollback plan: {e}")
            return {}

    def _calculate_confidence_level(
        self, 
        option: DecisionOption, 
        context_analysis: Dict[str, Any]
    ) -> float:
        """Calculate confidence level for the selected decision"""
        try:
            confidence_factors = []
            
            # Option's inherent confidence score
            confidence_factors.append(option.confidence_score)
            
            # Context stability (higher stability = higher confidence)
            ecosystem_health = context_analysis.get('ecosystem_health_score', 0.5)
            confidence_factors.append(ecosystem_health)
            
            # Market volatility (lower volatility = higher confidence)
            market_volatility = context_analysis.get('market_volatility', 0.5)
            confidence_factors.append(1.0 - market_volatility)
            
            # Stakeholder alignment (higher alignment = higher confidence)
            stakeholder_alignment = context_analysis.get('stakeholder_alignment', 0.5)
            confidence_factors.append(stakeholder_alignment)
            
            # Historical performance (better history = higher confidence)
            historical_performance = context_analysis.get('historical_performance', {})
            success_rate = historical_performance.get('success_rate', 0.5)
            confidence_factors.append(success_rate)
            
            # Calculate weighted average
            confidence_level = np.mean(confidence_factors)
            
            # Apply risk adjustment
            risk_adjustment = 1.0 - (option.risk_level * 0.2)
            confidence_level *= risk_adjustment
            
            return max(0.0, min(1.0, confidence_level))
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence level: {e}")
            return 0.5

    def _generate_decision_rationale(
        self, 
        option: DecisionOption, 
        context_analysis: Dict[str, Any],
        evaluations: List[Dict[str, Any]]
    ) -> str:
        """Generate human-readable rationale for the decision"""
        try:
            rationale_parts = []
            
            # Primary reason for selection
            rationale_parts.append(
                f"Selected '{option.description}' based on comprehensive multi-criteria analysis."
            )
            
            # Key strengths
            strengths = []
            if option.confidence_score > 0.8:
                strengths.append("high confidence in outcomes")
            if option.stakeholder_alignment > 0.8:
                strengths.append("strong stakeholder alignment")
            if option.risk_level < 0.3:
                strengths.append("low risk profile")
            
            if strengths:
                rationale_parts.append(f"Key strengths include: {', '.join(strengths)}.")
            
            # Context considerations
            ecosystem_health = context_analysis.get('ecosystem_health_score', 0.5)
            if ecosystem_health > 0.8:
                rationale_parts.append("Current ecosystem health supports this decision.")
            elif ecosystem_health < 0.4:
                rationale_parts.append("Decision accounts for current ecosystem challenges.")
            
            # Expected outcomes
            expected_outcomes = option.expected_outcomes
            if expected_outcomes:
                outcome_descriptions = []
                for outcome, value in expected_outcomes.items():
                    if value > 0.1:
                        outcome_descriptions.append(f"{outcome} improvement of {value:.1%}")
                
                if outcome_descriptions:
                    rationale_parts.append(
                        f"Expected outcomes include: {', '.join(outcome_descriptions)}."
                    )
            
            # Risk considerations
            if option.risk_level > 0.5:
                rationale_parts.append(
                    f"While this option carries moderate risk ({option.risk_level:.1%}), "
                    "the potential benefits justify the risk given current conditions."
                )
            
            return " ".join(rationale_parts)
            
        except Exception as e:
            self.logger.error(f"Error generating decision rationale: {e}")
            return f"Selected '{option.description}' based on autonomous analysis."

    def _define_monitoring_metrics(self, option: DecisionOption) -> List[str]:
        """Define metrics to monitor after decision implementation"""
        try:
            metrics = []
            
            # Standard metrics for all decisions
            metrics.extend([
                'implementation_success_rate',
                'performance_vs_baseline',
                'stakeholder_satisfaction',
                'risk_realization_rate'
            ])
            
            # Outcome-specific metrics
            for outcome in option.expected_outcomes.keys():
                metrics.append(f"{outcome}_actual_vs_expected")
            
            # Resource utilization metrics
            for resource in option.resource_requirements.keys():
                metrics.append(f"{resource}_utilization_efficiency")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error defining monitoring metrics: {e}")
            return ['implementation_success_rate', 'performance_vs_baseline']

    async def _store_decision(self, decision: DecisionResult, context: DecisionContext):
        """Store decision for learning and future reference"""
        try:
            decision_record = {
                'decision_id': decision.decision_id,
                'timestamp': int(time.time()),
                'decision_type': decision.decision_type.value,
                'selected_option_id': decision.selected_option.option_id,
                'confidence_level': decision.confidence_level,
                'context_summary': {
                    'ecosystem_health': context.ecosystem_state.get('overall_health', 0),
                    'market_conditions': context.market_conditions,
                    'stakeholder_preferences': context.stakeholder_preferences
                },
                'expected_outcomes': decision.expected_impact,
                'implementation_plan': decision.implementation_plan
            }
            
            self.decision_history.append(decision_record)
            
            # Keep only recent decisions (last 1000)
            if len(self.decision_history) > 1000:
                self.decision_history = self.decision_history[-1000:]
            
            self.logger.info(f"Decision {decision.decision_id} stored for learning")
            
        except Exception as e:
            self.logger.error(f"Error storing decision: {e}")

    # Scoring methods for option evaluation
    def _score_financial_impact(self, option: DecisionOption, context: Dict[str, Any]) -> float:
        """Score the financial impact of an option"""
        try:
            financial_outcomes = {
                k: v for k, v in option.expected_outcomes.items() 
                if 'financial' in k.lower() or 'revenue' in k.lower() or 'cost' in k.lower()
            }
            
            if not financial_outcomes:
                return 0.5  # Neutral score if no financial impact specified
            
            # Calculate weighted financial impact
            total_impact = sum(financial_outcomes.values())
            
            # Normalize to 0-1 scale
            return max(0.0, min(1.0, (total_impact + 1.0) / 2.0))
            
        except Exception as e:
            self.logger.error(f"Error scoring financial impact: {e}")
            return 0.5

    def _score_strategic_alignment(self, option: DecisionOption, context: Dict[str, Any]) -> float:
        """Score how well an option aligns with strategic goals"""
        try:
            # This would typically involve comparing option outcomes with strategic objectives
            # For now, use a simplified approach based on expected outcomes
            
            strategic_outcomes = {
                k: v for k, v in option.expected_outcomes.items()
                if any(term in k.lower() for term in ['growth', 'efficiency', 'innovation', 'strategic'])
            }
            
            if not strategic_outcomes:
                return 0.5
            
            alignment_score = sum(strategic_outcomes.values()) / len(strategic_outcomes)
            return max(0.0, min(1.0, (alignment_score + 1.0) / 2.0))
            
        except Exception as e:
            self.logger.error(f"Error scoring strategic alignment: {e}")
            return 0.5

    def _score_implementation_feasibility(self, option: DecisionOption, context: Dict[str, Any]) -> float:
        """Score the feasibility of implementing an option"""
        try:
            # Consider implementation complexity and resource availability
            complexity_score = 1.0 - option.implementation_complexity
            
            # Check resource availability
            available_resources = context.get('resource_availability', {})
            required_resources = option.resource_requirements
            
            resource_feasibility = 1.0
            for resource, required_amount in required_resources.items():
                available_amount = available_resources.get(resource, 0)
                if available_amount < required_amount:
                    resource_feasibility *= (available_amount / required_amount)
            
            # Combine complexity and resource feasibility
            feasibility_score = (complexity_score + resource_feasibility) / 2.0
            
            return max(0.0, min(1.0, feasibility_score))
            
        except Exception as e:
            self.logger.error(f"Error scoring implementation feasibility: {e}")
            return 0.5

    def _score_learning_opportunity(self, option: DecisionOption, context: Dict[str, Any]) -> float:
        """Score the learning opportunity provided by an option"""
        try:
            # Higher complexity and novelty provide more learning opportunities
            complexity_score = option.implementation_complexity
            
            # Check if this is a novel type of decision
            historical_decisions = context.get('historical_performance', [])
            similar_decisions = [
                d for d in historical_decisions 
                if d.get('option_type') == option.option_id
            ]
            
            novelty_score = 1.0 - min(len(similar_decisions) / 10.0, 1.0)
            
            learning_score = (complexity_score + novelty_score) / 2.0
            
            return max(0.0, min(1.0, learning_score))
            
        except Exception as e:
            self.logger.error(f"Error scoring learning opportunity: {e}")
            return 0.5

    # Context analysis helper methods
    def _calculate_ecosystem_health(self, ecosystem_state: Dict[str, Any]) -> float:
        """Calculate overall ecosystem health score"""
        try:
            health_factors = []
            
            # Mining performance
            mining_health = ecosystem_state.get('mining', {}).get('efficiency_score', 0.5)
            health_factors.append(mining_health)
            
            # Treasury health
            treasury_health = ecosystem_state.get('treasury', {}).get('health_score', 0.5)
            health_factors.append(treasury_health)
            
            # Governance efficiency
            governance_health = ecosystem_state.get('governance', {}).get('efficiency_score', 0.5)
            health_factors.append(governance_health)
            
            # Overall system health
            overall_health = ecosystem_state.get('overall_health', 0.5)
            health_factors.append(overall_health)
            
            return np.mean(health_factors)
            
        except Exception as e:
            self.logger.error(f"Error calculating ecosystem health: {e}")
            return 0.5

    def _assess_market_volatility(self, market_conditions: Dict[str, Any]) -> float:
        """Assess current market volatility"""
        try:
            volatility_indicators = []
            
            # Price volatility
            price_volatility = market_conditions.get('price_volatility', 0.5)
            volatility_indicators.append(price_volatility)
            
            # Volume volatility
            volume_volatility = market_conditions.get('volume_volatility', 0.5)
            volatility_indicators.append(volume_volatility)
            
            # Market sentiment volatility
            sentiment_volatility = market_conditions.get('sentiment_volatility', 0.5)
            volatility_indicators.append(sentiment_volatility)
            
            return np.mean(volatility_indicators)
            
        except Exception as e:
            self.logger.error(f"Error assessing market volatility: {e}")
            return 0.5

    def _assess_stakeholder_alignment(self, stakeholder_preferences: Dict[str, Any]) -> float:
        """Assess overall stakeholder alignment"""
        try:
            alignment_scores = []
            
            for stakeholder_group, preferences in stakeholder_preferences.items():
                satisfaction = preferences.get('satisfaction_level', 0.5)
                alignment_scores.append(satisfaction)
            
            if not alignment_scores:
                return 0.5
            
            return np.mean(alignment_scores)
            
        except Exception as e:
            self.logger.error(f"Error assessing stakeholder alignment: {e}")
            return 0.5

    def _determine_risk_tolerance(self, risk_assessment: Dict[str, Any]) -> float:
        """Determine current risk tolerance based on ecosystem state"""
        try:
            # Higher ecosystem health allows for higher risk tolerance
            current_health = risk_assessment.get('ecosystem_health', 0.5)
            
            # Recent performance affects risk tolerance
            recent_performance = risk_assessment.get('recent_performance', 0.5)
            
            # Stakeholder risk appetite
            stakeholder_risk_appetite = risk_assessment.get('stakeholder_risk_appetite', 0.5)
            
            # Calculate weighted risk tolerance
            risk_tolerance = (
                current_health * 0.4 +
                recent_performance * 0.3 +
                stakeholder_risk_appetite * 0.3
            )
            
            return max(0.0, min(1.0, risk_tolerance))
            
        except Exception as e:
            self.logger.error(f"Error determining risk tolerance: {e}")
            return 0.5

    def _assess_resource_availability(self, available_resources: Dict[str, Any]) -> Dict[str, float]:
        """Assess availability of different types of resources"""
        try:
            resource_availability = {}
            
            for resource_type, amount in available_resources.items():
                # Normalize resource availability to 0-1 scale
                # This would typically involve comparing to historical usage patterns
                normalized_amount = min(amount / 100.0, 1.0)  # Simplified normalization
                resource_availability[resource_type] = normalized_amount
            
            return resource_availability
            
        except Exception as e:
            self.logger.error(f"Error assessing resource availability: {e}")
            return {}

    def _assess_urgency(self, time_constraints: Optional[Dict[str, Any]]) -> float:
        """Assess urgency level based on time constraints"""
        try:
            if not time_constraints:
                return 0.5  # Medium urgency if no constraints specified
            
            deadline = time_constraints.get('deadline')
            if not deadline:
                return 0.5
            
            current_time = time.time()
            time_remaining = deadline - current_time
            
            # Convert to urgency score (less time = higher urgency)
            if time_remaining <= 3600:  # 1 hour
                return 1.0  # Critical urgency
            elif time_remaining <= 86400:  # 24 hours
                return 0.8  # High urgency
            elif time_remaining <= 604800:  # 1 week
                return 0.6  # Medium urgency
            else:
                return 0.3  # Low urgency
            
        except Exception as e:
            self.logger.error(f"Error assessing urgency: {e}")
            return 0.5

    def _analyze_historical_performance(self, historical_performance: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze historical performance data"""
        try:
            if not historical_performance:
                return {'success_rate': 0.5, 'average_performance': 0.5}
            
            # Calculate success rate
            successful_decisions = [
                d for d in historical_performance 
                if d.get('outcome', 'unknown') == 'success'
            ]
            success_rate = len(successful_decisions) / len(historical_performance)
            
            # Calculate average performance
            performance_scores = [
                d.get('performance_score', 0.5) 
                for d in historical_performance
            ]
            average_performance = np.mean(performance_scores)
            
            # Calculate trend
            recent_performance = historical_performance[-10:] if len(historical_performance) >= 10 else historical_performance
            recent_scores = [d.get('performance_score', 0.5) for d in recent_performance]
            
            if len(recent_scores) >= 2:
                trend = 'improving' if recent_scores[-1] > recent_scores[0] else 'declining'
            else:
                trend = 'stable'
            
            return {
                'success_rate': success_rate,
                'average_performance': average_performance,
                'trend': trend,
                'total_decisions': len(historical_performance)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing historical performance: {e}")
            return {'success_rate': 0.5, 'average_performance': 0.5}

    def _generate_decision_id(self, decision_type: DecisionType) -> str:
        """Generate unique decision ID"""
        timestamp = str(int(time.time()))
        type_prefix = decision_type.value[:4].upper()
        hash_input = f"{decision_type.value}_{timestamp}_{os.urandom(8).hex()}"
        hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        
        return f"{type_prefix}_{timestamp}_{hash_suffix}"

    async def adapt_decision_criteria(self, performance_feedback: Dict[str, Any]):
        """Adapt decision criteria based on performance feedback"""
        try:
            # This would implement learning algorithms to adjust decision criteria
            # based on the success/failure of previous decisions
            
            # For now, implement a simple adaptation mechanism
            if performance_feedback.get('overall_success_rate', 0.5) < 0.7:
                # If success rate is low, increase weight on risk management
                self.decision_criteria['risk_level'] = min(
                    self.decision_criteria['risk_level'] + 0.05, 0.4
                )
                self.decision_criteria['implementation_feasibility'] = min(
                    self.decision_criteria['implementation_feasibility'] + 0.05, 0.2
                )
            
            elif performance_feedback.get('overall_success_rate', 0.5) > 0.85:
                # If success rate is high, can afford to take more risks for learning
                self.decision_criteria['learning_opportunity'] = min(
                    self.decision_criteria['learning_opportunity'] + 0.02, 0.15
                )
            
            self.logger.info("Decision criteria adapted based on performance feedback")
            
        except Exception as e:
            self.logger.error(f"Error adapting decision criteria: {e}")

    async def get_decision_status(self) -> Dict[str, Any]:
        """Get current status of the decision engine"""
        try:
            recent_decisions = self.decision_history[-10:] if self.decision_history else []
            
            status = {
                'total_decisions_made': len(self.decision_history),
                'recent_decisions': len(recent_decisions),
                'current_decision_criteria': self.decision_criteria.copy(),
                'current_goal_weights': self.goal_weights.copy(),
                'learning_rate': self.learning_rate,
                'confidence_threshold': self.confidence_threshold,
                'models_initialized': {
                    'outcome_predictor': self.outcome_predictor is not None,
                    'risk_assessor': self.risk_assessor is not None,
                    'stakeholder_preference_model': self.stakeholder_preference_model is not None
                }
            }
            
            if recent_decisions:
                avg_confidence = np.mean([
                    d.get('confidence_level', 0.5) for d in recent_decisions
                ])
                status['average_recent_confidence'] = avg_confidence
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting decision status: {e}")
            return {'error': str(e)}

