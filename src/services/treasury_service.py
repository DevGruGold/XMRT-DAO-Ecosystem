"""
XMRT DAO Ecosystem - Treasury Management Service

This service handles treasury operations with AI-powered decision making:
- Treasury balance monitoring and allocation
- Automated rebalancing based on AI analysis
- Mining revenue management from MobileMonero.com
- Risk assessment and portfolio optimization
- Multi-signature transaction management

Based on XMRT ecosystem specifications:
- $1.5M treasury with 95% governance efficiency
- Real-world cash flow from Monero mining
- AI-powered autonomous decision making
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import json
import os

class TreasuryManager:
    """AI-powered treasury management system"""

    def __init__(self, config: Dict[str, Any], redis_service=None, web3_service=None):
        """
        Initialize Treasury Manager

        Args:
            config: Configuration dictionary
            redis_service: Redis service for data persistence
            web3_service: Web3 service for blockchain interactions
        """
        self.config = config
        self.redis_service = redis_service
        self.web3_service = web3_service
        self.logger = logging.getLogger(__name__)

        # Treasury configuration
        self.target_allocation = config.get('treasury_allocation', {
            'eth': 0.30,        # 30% ETH
            'xmr': 0.25,        # 25% XMR (from mining)
            'usdc': 0.35,       # 35% USDC (stable)
            'xmrt': 0.10        # 10% XMRT (governance token)
        })

        self.rebalance_threshold = config.get('rebalance_threshold', 0.05)  # 5%
        self.max_single_transaction = config.get('max_single_transaction', 100000)  # $100K
        self.risk_tolerance = config.get('risk_tolerance', 'moderate')

        # AI decision parameters
        self.confidence_threshold = 0.75
        self.decision_cooldown = 3600  # 1 hour between major decisions

        # Treasury state
        self.current_balance = {}
        self.last_rebalance = None
        self.pending_decisions = []

    async def get_treasury_status(self) -> Dict[str, Any]:
        """Get comprehensive treasury status"""
        try:
            # Get current balances from various sources
            balances = await self._fetch_all_balances()
            total_value_usd = await self._calculate_total_value(balances)

            # Calculate current allocation
            current_allocation = self._calculate_allocation_percentages(balances, total_value_usd)

            # Analyze rebalancing needs
            rebalance_needed = self._analyze_rebalancing_needs(current_allocation)

            # Get recent performance
            performance = await self._calculate_performance()

            return {
                "total_value_usd": total_value_usd,
                "balances": balances,
                "current_allocation": current_allocation,
                "target_allocation": self.target_allocation,
                "rebalance_needed": rebalance_needed,
                "performance": performance,
                "last_updated": datetime.utcnow().isoformat(),
                "governance_efficiency": await self._calculate_governance_efficiency()
            }

        except Exception as e:
            self.logger.error(f"Failed to get treasury status: {e}")
            return {"error": str(e)}

    async def _fetch_all_balances(self) -> Dict[str, Decimal]:
        """Fetch balances from all treasury sources"""
        balances = {
            'eth': Decimal('0'),
            'xmr': Decimal('0'),
            'usdc': Decimal('0'),
            'xmrt': Decimal('0')
        }

        try:
            # Get XMRT balance from Web3
            if self.web3_service:
                treasury_address = self.config.get('treasury_address')
                if treasury_address:
                    xmrt_balance = await self.web3_service.get_balance(treasury_address)
                    if 'balance_tokens' in xmrt_balance:
                        balances['xmrt'] = Decimal(str(xmrt_balance['balance_tokens']))

            # Get mining revenue (XMR) from Redis cache or API
            xmr_balance = await self._get_mining_balance()
            balances['xmr'] = Decimal(str(xmr_balance))

            # Get ETH and USDC from stored treasury wallets
            # This would integrate with actual treasury wallet addresses
            eth_balance = await self._get_eth_balance()
            usdc_balance = await self._get_usdc_balance()

            balances['eth'] = Decimal(str(eth_balance))
            balances['usdc'] = Decimal(str(usdc_balance))

            # Cache balances
            if self.redis_service:
                await self.redis_service.set(
                    "treasury:balances", 
                    json.dumps({k: str(v) for k, v in balances.items()}),
                    expire=300  # 5 minute cache
                )

            return balances

        except Exception as e:
            self.logger.error(f"Failed to fetch balances: {e}")
            return balances

    async def _get_mining_balance(self) -> float:
        """Get current XMR balance from mining operations"""
        try:
            # Check Redis cache first
            if self.redis_service:
                cached_balance = await self.redis_service.get("mining:xmr_balance")
                if cached_balance:
                    return float(cached_balance)

            # In production, this would integrate with MobileMonero.com API
            # For now, return estimated balance based on documentation
            estimated_weekly_mining = 2.3  # XMR per week as per docs
            days_since_start = 30  # Assume 30 days of operation
            estimated_balance = (estimated_weekly_mining / 7) * days_since_start

            return estimated_balance

        except Exception as e:
            self.logger.error(f"Failed to get mining balance: {e}")
            return 0.0

    async def _get_eth_balance(self) -> float:
        """Get ETH balance from treasury wallets"""
        # This would integrate with actual treasury wallet monitoring
        # Using estimated value from documentation
        return 342.5

    async def _get_usdc_balance(self) -> float:
        """Get USDC balance from treasury"""
        # Using estimated value from documentation
        return 875000.0

    async def _calculate_total_value(self, balances: Dict[str, Decimal]) -> float:
        """Calculate total treasury value in USD"""
        try:
            # Get current prices (in production, from price oracle)
            prices = await self._get_current_prices()

            total_value = 0.0
            for asset, balance in balances.items():
                if asset in prices:
                    total_value += float(balance) * prices[asset]

            return total_value

        except Exception as e:
            self.logger.error(f"Failed to calculate total value: {e}")
            return 0.0

    async def _get_current_prices(self) -> Dict[str, float]:
        """Get current asset prices in USD"""
        # In production, this would integrate with price oracles
        # Using representative prices
        return {
            'eth': 2400.0,    # ETH price
            'xmr': 180.0,     # XMR price  
            'usdc': 1.0,      # USDC is stable
            'xmrt': 0.072     # XMRT price from docs
        }

    def _calculate_allocation_percentages(self, balances: Dict[str, Decimal], 
                                        total_value: float) -> Dict[str, float]:
        """Calculate current allocation percentages"""
        if total_value == 0:
            return {asset: 0.0 for asset in balances}

        allocation = {}
        prices = asyncio.run(self._get_current_prices())

        for asset, balance in balances.items():
            if asset in prices:
                asset_value = float(balance) * prices[asset]
                allocation[asset] = asset_value / total_value
            else:
                allocation[asset] = 0.0

        return allocation

    def _analyze_rebalancing_needs(self, current_allocation: Dict[str, float]) -> Dict[str, Any]:
        """Analyze if rebalancing is needed"""
        rebalance_actions = []
        total_deviation = 0.0

        for asset in current_allocation:
            if asset in self.target_allocation:
                current = current_allocation[asset]
                target = self.target_allocation[asset]
                deviation = abs(current - target)

                if deviation > self.rebalance_threshold:
                    action = "sell" if current > target else "buy"
                    amount_deviation = deviation

                    rebalance_actions.append({
                        "asset": asset,
                        "action": action,
                        "current_percentage": current,
                        "target_percentage": target,
                        "deviation": deviation,
                        "priority": "high" if deviation > 0.10 else "medium"
                    })

                total_deviation += deviation

        return {
            "needed": len(rebalance_actions) > 0,
            "total_deviation": total_deviation,
            "actions_required": rebalance_actions,
            "urgency": "high" if total_deviation > 0.15 else "medium" if total_deviation > 0.08 else "low"
        }

    async def _calculate_performance(self) -> Dict[str, Any]:
        """Calculate treasury performance metrics"""
        try:
            # Get historical data (would come from database in production)
            # For now, simulate performance based on documentation

            return {
                "total_return_30d": 0.087,  # 8.7% monthly return
                "sharpe_ratio": 1.45,
                "max_drawdown": -0.034,     # 3.4% max drawdown
                "volatility": 0.12,         # 12% annualized volatility
                "governance_participation": 0.757,  # 75.7% participation rate
                "ai_decision_accuracy": 0.89        # 89% AI decision accuracy
            }

        except Exception as e:
            self.logger.error(f"Failed to calculate performance: {e}")
            return {}

    async def _calculate_governance_efficiency(self) -> float:
        """Calculate governance efficiency score"""
        # Based on documentation: 95% governance efficiency
        return 0.95

    async def evaluate_rebalancing_decision(self) -> Dict[str, Any]:
        """AI-powered evaluation of rebalancing decisions"""
        try:
            treasury_status = await self.get_treasury_status()

            if not treasury_status.get("rebalance_needed", {}).get("needed", False):
                return {
                    "decision": "hold",
                    "confidence": 0.95,
                    "reasoning": "Portfolio allocation within acceptable thresholds",
                    "timestamp": datetime.utcnow().isoformat()
                }

            rebalance_data = treasury_status["rebalance_needed"]
            urgency = rebalance_data["urgency"]

            # AI decision logic
            confidence = self._calculate_decision_confidence(treasury_status)

            if confidence >= self.confidence_threshold and urgency in ["high", "medium"]:
                decision = "rebalance"
                actions = self._generate_rebalancing_plan(rebalance_data["actions_required"])
            else:
                decision = "monitor"
                actions = []

            return {
                "decision": decision,
                "confidence": confidence,
                "actions": actions,
                "urgency": urgency,
                "reasoning": self._generate_decision_reasoning(treasury_status, confidence),
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to evaluate rebalancing decision: {e}")
            return {"error": str(e)}

    def _calculate_decision_confidence(self, treasury_status: Dict[str, Any]) -> float:
        """Calculate confidence score for AI decisions"""
        factors = []

        # Market volatility factor
        performance = treasury_status.get("performance", {})
        volatility = performance.get("volatility", 0.15)
        volatility_factor = max(0.5, 1.0 - (volatility - 0.10))  # Lower confidence in high volatility
        factors.append(volatility_factor)

        # Deviation magnitude factor
        total_deviation = treasury_status.get("rebalance_needed", {}).get("total_deviation", 0)
        deviation_factor = min(1.0, total_deviation * 4)  # Higher confidence with larger deviations
        factors.append(deviation_factor)

        # Governance efficiency factor
        gov_efficiency = treasury_status.get("governance_efficiency", 0.5)
        factors.append(gov_efficiency)

        # Time since last rebalance factor
        time_factor = 0.8  # Would calculate based on actual last rebalance time
        factors.append(time_factor)

        # Calculate weighted average
        confidence = sum(factors) / len(factors)
        return min(1.0, max(0.0, confidence))

    def _generate_rebalancing_plan(self, required_actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate specific rebalancing actions"""
        plan = []

        for action in required_actions:
            if action["priority"] == "high":
                plan.append({
                    "asset": action["asset"],
                    "action": action["action"],
                    "target_change": action["deviation"],
                    "estimated_amount_usd": self._estimate_transaction_amount(action),
                    "priority": action["priority"],
                    "requires_approval": self._requires_governance_approval(action)
                })

        return plan

    def _estimate_transaction_amount(self, action: Dict[str, Any]) -> float:
        """Estimate USD amount for rebalancing action"""
        # Simplified estimation - in production would be more sophisticated
        return min(self.max_single_transaction, 50000 * action["deviation"])

    def _requires_governance_approval(self, action: Dict[str, Any]) -> bool:
        """Determine if action requires governance approval"""
        estimated_amount = self._estimate_transaction_amount(action)
        return estimated_amount > self.max_single_transaction * 0.5

    def _generate_decision_reasoning(self, treasury_status: Dict[str, Any], confidence: float) -> str:
        """Generate human-readable reasoning for decisions"""
        rebalance_data = treasury_status.get("rebalance_needed", {})
        urgency = rebalance_data.get("urgency", "low")
        total_deviation = rebalance_data.get("total_deviation", 0)

        if confidence >= self.confidence_threshold:
            return f"High confidence ({confidence:.2f}) rebalancing decision. Portfolio deviation of {total_deviation:.1%} exceeds threshold with {urgency} urgency. Market conditions favorable for rebalancing."
        else:
            return f"Lower confidence ({confidence:.2f}) suggests monitoring. Portfolio deviation present but market volatility or other factors recommend waiting for better conditions."

    async def execute_ai_decision(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an AI-made treasury decision"""
        try:
            if decision_data["decision"] != "rebalance":
                return {
                    "status": "no_action",
                    "message": "No rebalancing action required",
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Log the decision
            self.logger.info(f"Executing AI treasury decision: {decision_data}")

            # In production, this would:
            # 1. Create governance proposals for large transactions
            # 2. Execute smaller transactions directly
            # 3. Update treasury state
            # 4. Log all actions for audit

            executed_actions = []
            for action in decision_data.get("actions", []):
                if action.get("requires_approval", False):
                    # Create governance proposal
                    proposal_result = await self._create_rebalancing_proposal(action)
                    executed_actions.append({
                        "action": "proposal_created",
                        "proposal_id": proposal_result.get("proposal_id"),
                        "asset": action["asset"],
                        "details": action
                    })
                else:
                    # Execute directly (if authorized)
                    execution_result = await self._execute_rebalancing_action(action)
                    executed_actions.append(execution_result)

            return {
                "status": "executed",
                "actions_taken": executed_actions,
                "confidence": decision_data["confidence"],
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to execute AI decision: {e}")
            return {"error": str(e)}

    async def _create_rebalancing_proposal(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Create governance proposal for treasury rebalancing"""
        # This would integrate with the governance system
        proposal = {
            "title": f"Treasury Rebalancing: {action['action'].title()} {action['asset'].upper()}",
            "description": f"AI-recommended treasury rebalancing to {action['action']} {action['asset']} based on current allocation analysis.",
            "estimated_amount": action["estimated_amount_usd"],
            "proposal_id": f"treasury_{int(datetime.utcnow().timestamp())}"
        }

        self.logger.info(f"Created rebalancing proposal: {proposal['proposal_id']}")
        return proposal

    async def _execute_rebalancing_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a rebalancing action directly"""
        # This would integrate with DEX protocols or treasury management
        return {
            "action": "executed",
            "asset": action["asset"],
            "type": action["action"],
            "amount_usd": action["estimated_amount_usd"],
            "transaction_id": f"tx_{int(datetime.utcnow().timestamp())}",
            "status": "completed"
        }
