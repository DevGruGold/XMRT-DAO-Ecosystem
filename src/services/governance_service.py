"""
XMRT DAO Ecosystem - Governance Service

This service handles DAO governance operations including:
- Proposal creation and management
- Voting mechanisms with XMRT tokens
- Governance decision execution
- Voting power delegation
- Governance metrics and analytics

Based on XMRT ecosystem specifications:
- 95% governance efficiency
- 75.7% participation rate
- AI-powered proposal analysis
- Multi-criteria decision analysis (MCDA)
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import json
import hashlib
from enum import Enum

class ProposalStatus(Enum):
    """Proposal status enumeration"""
    PENDING = "pending"
    ACTIVE = "active"
    SUCCEEDED = "succeeded"
    DEFEATED = "defeated"
    QUEUED = "queued"
    EXECUTED = "executed"
    CANCELLED = "cancelled"

class VoteChoice(Enum):
    """Vote choice enumeration"""
    AGAINST = 0
    FOR = 1
    ABSTAIN = 2

class GovernanceService:
    """Service for managing DAO governance operations"""

    def __init__(self, config: Dict[str, Any], web3_service=None, redis_service=None):
        """
        Initialize Governance Service

        Args:
            config: Configuration dictionary
            web3_service: Web3 service for blockchain interactions
            redis_service: Redis service for caching
        """
        self.config = config
        self.web3_service = web3_service
        self.redis_service = redis_service
        self.logger = logging.getLogger(__name__)

        # Governance parameters
        self.voting_delay = config.get('voting_delay_blocks', 1)  # 1 block delay
        self.voting_period = config.get('voting_period_blocks', 45818)  # ~1 week
        self.proposal_threshold = config.get('proposal_threshold', 0)  # No threshold
        self.quorum_fraction = config.get('quorum_fraction', 4)  # 4% quorum

        # AI analysis parameters
        self.ai_analysis_enabled = config.get('ai_analysis_enabled', True)
        self.mcda_weights = config.get('mcda_weights', {
            'technical_feasibility': 0.25,
            'economic_impact': 0.25,
            'community_benefit': 0.20,
            'risk_assessment': 0.15,
            'implementation_complexity': 0.15
        })

        # Cache settings
        self.cache_duration = {
            'proposals': 300,      # 5 minutes
            'votes': 120,          # 2 minutes
            'metrics': 600         # 10 minutes
        }

        # In-memory storage for demonstration (production would use database)
        self.proposals = {}
        self.votes = {}
        self.delegations = {}

    async def create_proposal(self, proposer: str, title: str, description: str,
                            targets: List[str] = None, values: List[int] = None,
                            calldatas: List[str] = None) -> Dict[str, Any]:
        """Create a new governance proposal"""
        try:
            # Validate proposer has sufficient voting power
            voting_power = await self._get_voting_power(proposer)
            if voting_power < self.proposal_threshold:
                return {"error": "Insufficient voting power to create proposal"}

            # Generate proposal ID
            proposal_id = self._generate_proposal_id(targets or [], values or [], calldatas or [])

            # Check if proposal already exists
            if proposal_id in self.proposals:
                return {"error": "Proposal already exists"}

            # Create proposal
            current_block = await self._get_current_block()
            proposal = {
                "id": proposal_id,
                "proposer": proposer,
                "title": title,
                "description": description,
                "targets": targets or [],
                "values": values or [],
                "calldatas": calldatas or [],
                "start_block": current_block + self.voting_delay,
                "end_block": current_block + self.voting_delay + self.voting_period,
                "status": ProposalStatus.PENDING.value,
                "votes_for": 0,
                "votes_against": 0,
                "votes_abstain": 0,
                "created_at": datetime.utcnow().isoformat(),
                "ai_analysis": await self._analyze_proposal_with_ai(title, description) if self.ai_analysis_enabled else {}
            }

            self.proposals[proposal_id] = proposal

            # Cache the proposal
            if self.redis_service:
                await self.redis_service.set(
                    f"governance:proposal:{proposal_id}",
                    json.dumps(proposal),
                    expire=self.cache_duration['proposals']
                )

            self.logger.info(f"Created proposal {proposal_id}: {title}")

            return {
                "proposal_id": proposal_id,
                "status": "created",
                "proposal": proposal
            }

        except Exception as e:
            self.logger.error(f"Failed to create proposal: {e}")
            return {"error": str(e)}

    async def cast_vote(self, voter: str, proposal_id: str, support: int, 
                       reason: str = "") -> Dict[str, Any]:
        """Cast a vote on a proposal"""
        try:
            # Get proposal
            proposal = await self.get_proposal(proposal_id)
            if not proposal or "error" in proposal:
                return {"error": "Proposal not found"}

            # Check if voting is active
            current_block = await self._get_current_block()
            if current_block < proposal["start_block"]:
                return {"error": "Voting has not started"}
            if current_block > proposal["end_block"]:
                return {"error": "Voting has ended"}

            # Check if voter has already voted
            vote_key = f"{proposal_id}:{voter}"
            if vote_key in self.votes:
                return {"error": "Already voted on this proposal"}

            # Get voting power
            voting_power = await self._get_voting_power(voter, proposal["start_block"])
            if voting_power == 0:
                return {"error": "No voting power"}

            # Cast vote
            vote = {
                "proposal_id": proposal_id,
                "voter": voter,
                "support": support,
                "voting_power": voting_power,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
                "block_number": current_block
            }

            self.votes[vote_key] = vote

            # Update proposal vote counts
            if support == VoteChoice.FOR.value:
                self.proposals[proposal_id]["votes_for"] += voting_power
            elif support == VoteChoice.AGAINST.value:
                self.proposals[proposal_id]["votes_against"] += voting_power
            else:  # ABSTAIN
                self.proposals[proposal_id]["votes_abstain"] += voting_power

            # Cache the vote
            if self.redis_service:
                await self.redis_service.set(
                    f"governance:vote:{vote_key}",
                    json.dumps(vote),
                    expire=self.cache_duration['votes']
                )

            self.logger.info(f"Vote cast by {voter} on proposal {proposal_id}: {support}")

            return {
                "status": "voted",
                "vote": vote
            }

        except Exception as e:
            self.logger.error(f"Failed to cast vote: {e}")
            return {"error": str(e)}

    async def get_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Get proposal details"""
        try:
            # Check cache first
            if self.redis_service:
                cached_proposal = await self.redis_service.get(f"governance:proposal:{proposal_id}")
                if cached_proposal:
                    return json.loads(cached_proposal)

            # Get from memory
            if proposal_id not in self.proposals:
                return {"error": "Proposal not found"}

            proposal = self.proposals[proposal_id].copy()

            # Update status based on current state
            proposal = await self._update_proposal_status(proposal)

            return proposal

        except Exception as e:
            self.logger.error(f"Failed to get proposal: {e}")
            return {"error": str(e)}

    async def get_all_proposals(self, status_filter: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all proposals with optional status filtering"""
        try:
            proposals = []

            for proposal_id, proposal in list(self.proposals.items()):
                updated_proposal = await self._update_proposal_status(proposal.copy())

                if status_filter and updated_proposal["status"] != status_filter:
                    continue

                proposals.append(updated_proposal)

            # Sort by creation date (newest first)
            proposals.sort(key=lambda x: x["created_at"], reverse=True)

            return proposals[:limit]

        except Exception as e:
            self.logger.error(f"Failed to get proposals: {e}")
            return []

    async def get_votes_for_proposal(self, proposal_id: str) -> List[Dict[str, Any]]:
        """Get all votes for a specific proposal"""
        try:
            proposal_votes = []

            for vote_key, vote in self.votes.items():
                if vote["proposal_id"] == proposal_id:
                    proposal_votes.append(vote)

            # Sort by voting power (highest first)
            proposal_votes.sort(key=lambda x: x["voting_power"], reverse=True)

            return proposal_votes

        except Exception as e:
            self.logger.error(f"Failed to get votes: {e}")
            return []

    async def get_governance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive governance metrics"""
        try:
            cache_key = "governance:metrics"

            # Check cache
            if self.redis_service:
                cached_metrics = await self.redis_service.get(cache_key)
                if cached_metrics:
                    return json.loads(cached_metrics)

            # Calculate metrics
            total_proposals = len(self.proposals)
            active_proposals = len([p for p in self.proposals.values() 
                                 if p["status"] == ProposalStatus.ACTIVE.value])

            # Vote participation
            total_votes = len(self.votes)
            unique_voters = len(set(vote["voter"] for vote in self.votes.values()))

            # Proposal outcomes
            passed_proposals = len([p for p in self.proposals.values() 
                                  if p["status"] == ProposalStatus.SUCCEEDED.value])

            executed_proposals = len([p for p in self.proposals.values() 
                                    if p["status"] == ProposalStatus.EXECUTED.value])

            # Calculate participation rate (using simulated data from docs)
            total_token_holders = 2847  # From documentation
            participation_rate = min(1.0, unique_voters / total_token_holders) if total_token_holders > 0 else 0

            # Calculate governance efficiency (from docs: 95%)
            governance_efficiency = 0.95

            # Average voting power
            avg_voting_power = sum(vote["voting_power"] for vote in self.votes.values()) / total_votes if total_votes > 0 else 0

            metrics = {
                "total_proposals": total_proposals,
                "active_proposals": active_proposals,
                "passed_proposals": passed_proposals,
                "executed_proposals": executed_proposals,
                "total_votes": total_votes,
                "unique_voters": unique_voters,
                "participation_rate": participation_rate,
                "governance_efficiency": governance_efficiency,
                "average_voting_power": avg_voting_power,
                "success_rate": passed_proposals / total_proposals if total_proposals > 0 else 0,
                "execution_rate": executed_proposals / passed_proposals if passed_proposals > 0 else 0,
                "last_updated": datetime.utcnow().isoformat()
            }

            # Cache metrics
            if self.redis_service:
                await self.redis_service.set(
                    cache_key,
                    json.dumps(metrics),
                    expire=self.cache_duration['metrics']
                )

            return metrics

        except Exception as e:
            self.logger.error(f"Failed to get governance metrics: {e}")
            return {"error": str(e)}

    async def delegate_voting_power(self, delegator: str, delegatee: str) -> Dict[str, Any]:
        """Delegate voting power to another address"""
        try:
            # Validate addresses
            if delegator == delegatee:
                return {"error": "Cannot delegate to self"}

            # Record delegation
            self.delegations[delegator] = {
                "delegatee": delegatee,
                "timestamp": datetime.utcnow().isoformat(),
                "active": True
            }

            self.logger.info(f"Voting power delegated from {delegator} to {delegatee}")

            return {
                "status": "delegated",
                "delegator": delegator,
                "delegatee": delegatee
            }

        except Exception as e:
            self.logger.error(f"Failed to delegate voting power: {e}")
            return {"error": str(e)}

    async def _get_voting_power(self, address: str, block_number: int = None) -> int:
        """Get voting power for an address at a specific block"""
        try:
            # In production, this would query the token contract for historical balance
            # Using simulated voting power based on token holdings

            # Check if this address has delegated power
            if address in self.delegations and self.delegations[address]["active"]:
                base_power = 1000  # Reduced power for delegating address
            else:
                base_power = 10000  # Base voting power

            # Add delegated power from others
            delegated_power = sum(
                5000 for delegator, delegation in self.delegations.items()
                if delegation["delegatee"] == address and delegation["active"]
            )

            return base_power + delegated_power

        except Exception as e:
            self.logger.error(f"Failed to get voting power: {e}")
            return 0

    async def _get_current_block(self) -> int:
        """Get current block number"""
        try:
            if self.web3_service:
                return self.web3_service.web3.eth.block_number
            else:
                # Simulate block progression
                return int(datetime.utcnow().timestamp() // 12)  # ~12 second blocks
        except:
            return int(datetime.utcnow().timestamp() // 12)

    def _generate_proposal_id(self, targets: List[str], values: List[int], calldatas: List[str]) -> str:
        """Generate unique proposal ID"""
        proposal_data = f"{targets}{values}{calldatas}{datetime.utcnow()}"
        return hashlib.sha256(proposal_data.encode()).hexdigest()[:16]

    async def _update_proposal_status(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Update proposal status based on current state"""
        try:
            current_block = await self._get_current_block()
            proposal_id = proposal["id"]

            # Check if voting period has started
            if current_block < proposal["start_block"]:
                proposal["status"] = ProposalStatus.PENDING.value
            elif current_block <= proposal["end_block"]:
                proposal["status"] = ProposalStatus.ACTIVE.value
            else:
                # Voting has ended, determine outcome
                total_votes = proposal["votes_for"] + proposal["votes_against"] + proposal["votes_abstain"]

                # Calculate quorum (simplified)
                total_supply = 21000000  # 21M XMRT tokens
                quorum_required = total_supply * (self.quorum_fraction / 100)

                if total_votes >= quorum_required and proposal["votes_for"] > proposal["votes_against"]:
                    proposal["status"] = ProposalStatus.SUCCEEDED.value
                else:
                    proposal["status"] = ProposalStatus.DEFEATED.value

            # Update in storage
            self.proposals[proposal_id] = proposal

            return proposal

        except Exception as e:
            self.logger.error(f"Failed to update proposal status: {e}")
            return proposal

    async def _analyze_proposal_with_ai(self, title: str, description: str) -> Dict[str, Any]:
        """AI analysis of proposal using MCDA"""
        try:
            # Simulate AI analysis with MCDA scoring
            # In production, this would use actual AI/ML models

            import random

            # MCDA criteria scoring (0-100)
            criteria_scores = {
                'technical_feasibility': random.randint(60, 95),
                'economic_impact': random.randint(50, 90),
                'community_benefit': random.randint(70, 95),
                'risk_assessment': random.randint(40, 80),
                'implementation_complexity': random.randint(30, 70)
            }

            # Calculate weighted score
            weighted_score = sum(
                score * self.mcda_weights.get(criterion, 0)
                for criterion, score in criteria_scores.items()
            )

            # Generate recommendation
            if weighted_score >= 80:
                recommendation = "STRONGLY_SUPPORT"
                confidence = "high"
            elif weighted_score >= 65:
                recommendation = "SUPPORT"
                confidence = "medium"
            elif weighted_score >= 50:
                recommendation = "NEUTRAL"
                confidence = "medium"
            else:
                recommendation = "OPPOSE"
                confidence = "low"

            analysis = {
                "mcda_scores": criteria_scores,
                "weighted_score": round(weighted_score, 2),
                "recommendation": recommendation,
                "confidence": confidence,
                "key_considerations": [
                    f"Technical feasibility rated at {criteria_scores['technical_feasibility']}/100",
                    f"Economic impact assessment: {criteria_scores['economic_impact']}/100",
                    f"Community benefit score: {criteria_scores['community_benefit']}/100"
                ],
                "analysis_timestamp": datetime.utcnow().isoformat()
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Failed to analyze proposal with AI: {e}")
            return {"error": "AI analysis unavailable"}

    async def execute_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Execute a successful proposal"""
        try:
            proposal = await self.get_proposal(proposal_id)
            if not proposal or "error" in proposal:
                return {"error": "Proposal not found"}

            if proposal["status"] != ProposalStatus.SUCCEEDED.value:
                return {"error": "Proposal has not succeeded"}

            # In production, this would execute the actual proposal calls
            # For now, just mark as executed

            self.proposals[proposal_id]["status"] = ProposalStatus.EXECUTED.value
            self.proposals[proposal_id]["executed_at"] = datetime.utcnow().isoformat()

            execution_result = {
                "proposal_id": proposal_id,
                "status": "executed",
                "executed_at": datetime.utcnow().isoformat(),
                "execution_summary": "Proposal executed successfully"
            }

            self.logger.info(f"Executed proposal {proposal_id}")

            return execution_result

        except Exception as e:
            self.logger.error(f"Failed to execute proposal: {e}")
            return {"error": str(e)}
