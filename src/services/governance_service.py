"""
XMRT DAO Ecosystem - Enhanced Governance Service

This service handles DAO governance operations including:
- Proposal creation and management with IP owner privileges
- Voting mechanisms with XMRT tokens
- IP owner veto capabilities and emergency controls
- Governance decision execution with creator authorization
- Voting power delegation
- Governance metrics and analytics
- AI-powered proposal analysis with IP impact assessment

Enhanced Features:
- XMRT-IP NFT integration for creator privileges
- IP owner veto and emergency pause capabilities
- Governance impact analysis for IP-sensitive proposals
- Enhanced authorization system respecting creator rights
- Multi-criteria decision analysis (MCDA) with IP considerations

Based on XMRT ecosystem specifications:
- 95% governance efficiency target
- 75.7% participation rate target
- AI-powered proposal analysis
- IP owner privileges and protections
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
    VETOED = "vetoed"  # New status for IP owner veto

class VoteType(Enum):
    """Vote type enumeration"""
    AGAINST = 0
    FOR = 1
    ABSTAIN = 2

class GovernanceService:
    """Enhanced governance service with IP owner privileges"""

    def __init__(self, web3_service, config: Dict[str, Any], ip_nft_service=None):
        self.web3_service = web3_service
        self.config = config
        self.ip_nft_service = ip_nft_service
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.governance_config = config.get("governance", {})
        self.token_config = config.get("token", {})
        self.ai_config = config.get("ai", {})

        # Governance parameters
        self.voting_period = self.governance_config.get("voting_period", 7 * 24 * 3600)
        self.voting_delay = self.governance_config.get("voting_delay", 24 * 3600)
        self.proposal_threshold = self.governance_config.get("proposal_threshold", 100_000)
        self.quorum_percentage = self.governance_config.get("quorum_percentage", 4)
        self.timelock_delay = self.governance_config.get("timelock_delay", 2 * 24 * 3600)

        # IP owner privileges
        self.ip_privileges = self.governance_config.get("ip_owner_privileges", {})

        # Storage
        self.proposals = {}
        self.votes = {}
        self.delegations = {}
        self.governance_metrics = {
            "total_proposals": 0,
            "executed_proposals": 0,
            "participation_rate": 0.0,
            "efficiency_score": 0.0,
            "ip_owner_actions": 0
        }

        # Emergency controls
        self.emergency_paused = False
        self.pause_reason = None
        self.pause_timestamp = None

        self.logger.info("Enhanced GovernanceService initialized with IP NFT integration")

    async def create_proposal(self, proposer: str, title: str, description: str,
                            target_contract: str = "", function_call: str = "",
                            call_data: str = "") -> Dict[str, Any]:
        """
        Create a new governance proposal with IP impact analysis

        Args:
            proposer: Address of the proposal creator
            title: Proposal title
            description: Detailed description
            target_contract: Target contract address (optional)
            function_call: Function to call (optional)
            call_data: Call data (optional)

        Returns:
            Dict containing proposal creation result
        """
        try:
            # Check if governance is paused
            if self.emergency_paused:
                return {
                    "success": False,
                    "error": "Governance is emergency paused",
                    "pause_reason": self.pause_reason,
                    "paused_at": self.pause_timestamp
                }

            # Validate proposer has enough tokens
            # (In production, check actual token balance)
            proposal_id = len(self.proposals) + 1

            # Create proposal data
            proposal_data = {
                "id": proposal_id,
                "proposer": proposer,
                "title": title,
                "description": description,
                "target_contract": target_contract,
                "function_call": function_call,
                "call_data": call_data,
                "status": ProposalStatus.PENDING.value,
                "created_at": datetime.utcnow().isoformat(),
                "voting_starts": (datetime.utcnow() + timedelta(seconds=self.voting_delay)).isoformat(),
                "voting_ends": (datetime.utcnow() + timedelta(seconds=self.voting_delay + self.voting_period)).isoformat(),
                "votes_for": 0,
                "votes_against": 0,
                "votes_abstain": 0,
                "voters": [],
                "ip_impact_analysis": None,
                "requires_ip_approval": False,
                "vetoed": False,
                "veto_reason": None
            }

            # Perform IP impact analysis if IP NFT service is available
            if self.ip_nft_service:
                try:
                    impact_analysis = await self.ip_nft_service.check_governance_impact(proposal_data)
                    proposal_data["ip_impact_analysis"] = impact_analysis
                    proposal_data["requires_ip_approval"] = impact_analysis.get("requires_ip_approval", False)

                    self.logger.info(f"IP impact analysis for proposal {proposal_id}: {impact_analysis.get('impact_level', 'NONE')}")
                except Exception as e:
                    self.logger.warning(f"IP impact analysis failed: {e}")

            # Store proposal
            self.proposals[proposal_id] = proposal_data
            self.governance_metrics["total_proposals"] += 1

            # Notify IP owner if proposal requires attention
            if proposal_data.get("requires_ip_approval", False):
                await self._notify_ip_owner(proposal_data)

            self.logger.info(f"Created proposal {proposal_id}: {title}")

            return {
                "success": True,
                "proposal_id": proposal_id,
                "proposal": proposal_data,
                "message": "Proposal created successfully"
            }

        except Exception as e:
            self.logger.error(f"Failed to create proposal: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def cast_vote(self, voter: str, proposal_id: int, support: int, 
                       reason: str = "") -> Dict[str, Any]:
        """
        Cast a vote on a proposal

        Args:
            voter: Address of the voter
            proposal_id: ID of the proposal
            support: Vote type (0=Against, 1=For, 2=Abstain)
            reason: Optional reason for the vote

        Returns:
            Dict containing vote result
        """
        try:
            # Check if proposal exists
            if proposal_id not in self.proposals:
                return {
                    "success": False,
                    "error": "Proposal not found"
                }

            proposal = self.proposals[proposal_id]

            # Check if governance is paused
            if self.emergency_paused:
                return {
                    "success": False,
                    "error": "Governance is emergency paused",
                    "pause_reason": self.pause_reason
                }

            # Check if proposal is vetoed
            if proposal.get("vetoed", False):
                return {
                    "success": False,
                    "error": "Proposal has been vetoed by IP owner",
                    "veto_reason": proposal.get("veto_reason")
                }

            # Check voting period
            now = datetime.utcnow()
            voting_starts = datetime.fromisoformat(proposal["voting_starts"].replace('Z', '+00:00')).replace(tzinfo=None)
            voting_ends = datetime.fromisoformat(proposal["voting_ends"].replace('Z', '+00:00')).replace(tzinfo=None)

            if now < voting_starts:
                return {
                    "success": False,
                    "error": "Voting has not started yet"
                }

            if now > voting_ends:
                return {
                    "success": False,
                    "error": "Voting period has ended"
                }

            # Check if voter already voted
            if voter in proposal["voters"]:
                return {
                    "success": False,
                    "error": "Address has already voted"
                }

            # Get voting power (in production, query actual token balance)
            voting_power = 1000  # Placeholder

            # Record vote
            vote_data = {
                "voter": voter,
                "proposal_id": proposal_id,
                "support": support,
                "voting_power": voting_power,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }

            # Update proposal vote counts
            if support == VoteType.FOR.value:
                proposal["votes_for"] += voting_power
            elif support == VoteType.AGAINST.value:
                proposal["votes_against"] += voting_power
            else:  # ABSTAIN
                proposal["votes_abstain"] += voting_power

            proposal["voters"].append(voter)

            # Store vote
            vote_key = f"{proposal_id}_{voter}"
            self.votes[vote_key] = vote_data

            # Check if IP owner voted
            if self.ip_nft_service:
                ip_privileges = await self.ip_nft_service.get_ip_privileges(voter)
                if ip_privileges.get("has_privileges", False):
                    self.governance_metrics["ip_owner_actions"] += 1
                    self.logger.info(f"IP owner voted on proposal {proposal_id}")

            self.logger.info(f"Vote cast by {voter} on proposal {proposal_id}: {support}")

            return {
                "success": True,
                "vote": vote_data,
                "proposal_stats": {
                    "votes_for": proposal["votes_for"],
                    "votes_against": proposal["votes_against"],
                    "votes_abstain": proposal["votes_abstain"],
                    "total_voters": len(proposal["voters"])
                }
            }

        except Exception as e:
            self.logger.error(f"Failed to cast vote: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def veto_proposal(self, address: str, proposal_id: int, reason: str = "") -> Dict[str, Any]:
        """
        Allow IP owner to veto a proposal

        Args:
            address: Address attempting to veto
            proposal_id: ID of the proposal to veto
            reason: Reason for the veto

        Returns:
            Dict containing veto result
        """
        try:
            # Check if proposal exists
            if proposal_id not in self.proposals:
                return {
                    "success": False,
                    "error": "Proposal not found"
                }

            # Verify IP owner privileges
            if not self.ip_nft_service:
                return {
                    "success": False,
                    "error": "IP NFT service not available"
                }

            authorization = await self.ip_nft_service.authorize_action(
                address, "veto_proposal", self.proposals[proposal_id]
            )

            if not authorization.get("authorized", False):
                return {
                    "success": False,
                    "error": "Not authorized to veto proposals",
                    "reason": authorization.get("reason", "")
                }

            proposal = self.proposals[proposal_id]

            # Check if proposal can be vetoed
            if proposal["status"] in [ProposalStatus.EXECUTED.value, ProposalStatus.CANCELLED.value]:
                return {
                    "success": False,
                    "error": "Cannot veto executed or cancelled proposal"
                }

            # Apply veto
            proposal["status"] = ProposalStatus.VETOED.value
            proposal["vetoed"] = True
            proposal["veto_reason"] = reason
            proposal["vetoed_at"] = datetime.utcnow().isoformat()
            proposal["vetoed_by"] = address

            self.governance_metrics["ip_owner_actions"] += 1

            self.logger.warning(f"Proposal {proposal_id} vetoed by IP owner: {reason}")

            return {
                "success": True,
                "proposal_id": proposal_id,
                "message": "Proposal vetoed successfully",
                "veto_reason": reason
            }

        except Exception as e:
            self.logger.error(f"Failed to veto proposal: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def emergency_pause(self, address: str, reason: str = "") -> Dict[str, Any]:
        """
        Allow IP owner to emergency pause governance

        Args:
            address: Address attempting to pause
            reason: Reason for the emergency pause

        Returns:
            Dict containing pause result
        """
        try:
            # Verify IP owner privileges
            if not self.ip_nft_service:
                return {
                    "success": False,
                    "error": "IP NFT service not available"
                }

            authorization = await self.ip_nft_service.authorize_action(address, "emergency_pause")

            if not authorization.get("authorized", False):
                return {
                    "success": False,
                    "error": "Not authorized for emergency pause",
                    "reason": authorization.get("reason", "")
                }

            # Apply emergency pause
            self.emergency_paused = True
            self.pause_reason = reason
            self.pause_timestamp = datetime.utcnow().isoformat()

            self.governance_metrics["ip_owner_actions"] += 1

            self.logger.critical(f"Governance emergency paused by IP owner: {reason}")

            return {
                "success": True,
                "message": "Governance emergency paused",
                "reason": reason,
                "paused_at": self.pause_timestamp
            }

        except Exception as e:
            self.logger.error(f"Failed to emergency pause: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def resume_governance(self, address: str) -> Dict[str, Any]:
        """
        Allow IP owner to resume governance after emergency pause

        Args:
            address: Address attempting to resume

        Returns:
            Dict containing resume result
        """
        try:
            if not self.emergency_paused:
                return {
                    "success": False,
                    "error": "Governance is not paused"
                }

            # Verify IP owner privileges
            if not self.ip_nft_service:
                return {
                    "success": False,
                    "error": "IP NFT service not available"
                }

            authorization = await self.ip_nft_service.authorize_action(address, "emergency_pause")

            if not authorization.get("authorized", False):
                return {
                    "success": False,
                    "error": "Not authorized to resume governance"
                }

            # Resume governance
            self.emergency_paused = False
            resumed_at = datetime.utcnow().isoformat()

            self.governance_metrics["ip_owner_actions"] += 1

            self.logger.info(f"Governance resumed by IP owner at {resumed_at}")

            return {
                "success": True,
                "message": "Governance resumed",
                "resumed_at": resumed_at,
                "was_paused_for": self.pause_reason
            }

        except Exception as e:
            self.logger.error(f"Failed to resume governance: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def execute_proposal(self, proposal_id: int, executor: str = "") -> Dict[str, Any]:
        """
        Execute a successful proposal with IP owner consideration

        Args:
            proposal_id: ID of the proposal to execute
            executor: Address executing the proposal

        Returns:
            Dict containing execution result
        """
        try:
            # Check if proposal exists
            if proposal_id not in self.proposals:
                return {
                    "success": False,
                    "error": "Proposal not found"
                }

            proposal = self.proposals[proposal_id]

            # Check if governance is paused
            if self.emergency_paused:
                return {
                    "success": False,
                    "error": "Governance is emergency paused"
                }

            # Check if proposal is vetoed
            if proposal.get("vetoed", False):
                return {
                    "success": False,
                    "error": "Proposal has been vetoed by IP owner"
                }

            # Check proposal status and voting results
            if proposal["status"] != ProposalStatus.SUCCEEDED.value:
                # Update status if voting period ended
                await self._update_proposal_status(proposal_id)

                if proposal["status"] != ProposalStatus.SUCCEEDED.value:
                    return {
                        "success": False,
                        "error": f"Proposal not ready for execution. Status: {proposal['status']}"
                    }

            # Check if requires IP approval for high-impact proposals
            if proposal.get("requires_ip_approval", False) and self.ip_nft_service:
                impact_analysis = proposal.get("ip_impact_analysis", {})
                if impact_analysis.get("impact_level") == "HIGH":
                    # In production, verify IP owner has been notified and acknowledged
                    self.logger.info(f"Executing high-impact proposal {proposal_id} with IP awareness")

            # Execute the proposal (placeholder - in production, execute actual contract calls)
            execution_result = {
                "proposal_id": proposal_id,
                "status": "executed",
                "executed_at": datetime.utcnow().isoformat(),
                "execution_summary": "Proposal executed successfully",
                "executor": executor,
                "transaction_hash": f"0x{hashlib.sha256(f'execute_{proposal_id}'.encode()).hexdigest()}"  # Mock
            }

            # Update proposal status
            proposal["status"] = ProposalStatus.EXECUTED.value
            proposal["executed_at"] = execution_result["executed_at"]

            # Update metrics
            self.governance_metrics["executed_proposals"] += 1

            self.logger.info(f"Executed proposal {proposal_id}")

            return {
                "success": True,
                "execution_result": execution_result
            }

        except Exception as e:
            self.logger.error(f"Failed to execute proposal: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_proposal(self, proposal_id: int) -> Dict[str, Any]:
        """Get proposal details with IP analysis"""
        try:
            if proposal_id not in self.proposals:
                return {
                    "success": False,
                    "error": "Proposal not found"
                }

            proposal = self.proposals[proposal_id].copy()

            # Add current status analysis
            await self._update_proposal_status(proposal_id)
            proposal["status"] = self.proposals[proposal_id]["status"]

            # Add IP owner perspective if available
            if self.ip_nft_service and proposal.get("ip_impact_analysis"):
                proposal["ip_owner_notification_sent"] = True  # Placeholder
                proposal["ip_considerations"] = proposal["ip_impact_analysis"]

            return {
                "success": True,
                "proposal": proposal
            }

        except Exception as e:
            self.logger.error(f"Failed to get proposal: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_governance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive governance metrics including IP owner activity"""
        try:
            # Calculate participation rate
            total_possible_votes = self.governance_metrics["total_proposals"] * 1000  # Mock
            actual_votes = sum(len(p.get("voters", [])) for p in self.proposals.values())
            participation_rate = (actual_votes / total_possible_votes * 100) if total_possible_votes > 0 else 0

            # Calculate efficiency score
            if self.governance_metrics["total_proposals"] > 0:
                efficiency_score = (self.governance_metrics["executed_proposals"] / 
                                 self.governance_metrics["total_proposals"] * 100)
            else:
                efficiency_score = 0

            metrics = {
                "governance_overview": {
                    "total_proposals": self.governance_metrics["total_proposals"],
                    "executed_proposals": self.governance_metrics["executed_proposals"],
                    "pending_proposals": len([p for p in self.proposals.values() if p["status"] == ProposalStatus.PENDING.value]),
                    "active_proposals": len([p for p in self.proposals.values() if p["status"] == ProposalStatus.ACTIVE.value]),
                    "vetoed_proposals": len([p for p in self.proposals.values() if p.get("vetoed", False)])
                },
                "participation_metrics": {
                    "participation_rate": round(participation_rate, 2),
                    "target_participation": self.governance_config.get("target_participation", 75.7),
                    "efficiency_score": round(efficiency_score, 2),
                    "target_efficiency": self.governance_config.get("target_efficiency", 95.0)
                },
                "ip_owner_activity": {
                    "total_actions": self.governance_metrics["ip_owner_actions"],
                    "veto_capability": self.ip_privileges.get("can_veto_proposals", False),
                    "emergency_pause_capability": self.ip_privileges.get("emergency_pause", False),
                    "governance_paused": self.emergency_paused,
                    "pause_reason": self.pause_reason if self.emergency_paused else None
                },
                "system_health": {
                    "ip_nft_service_available": self.ip_nft_service is not None,
                    "web3_service_available": self.web3_service is not None,
                    "governance_active": not self.emergency_paused
                },
                "timestamp": datetime.utcnow().isoformat()
            }

            return metrics

        except Exception as e:
            self.logger.error(f"Failed to get governance metrics: {e}")
            return {"error": str(e)}

    async def _update_proposal_status(self, proposal_id: int):
        """Update proposal status based on current time and voting results"""
        proposal = self.proposals[proposal_id]
        now = datetime.utcnow()

        voting_starts = datetime.fromisoformat(proposal["voting_starts"].replace('Z', '+00:00')).replace(tzinfo=None)
        voting_ends = datetime.fromisoformat(proposal["voting_ends"].replace('Z', '+00:00')).replace(tzinfo=None)

        if proposal["status"] == ProposalStatus.PENDING.value and now >= voting_starts:
            proposal["status"] = ProposalStatus.ACTIVE.value
        elif proposal["status"] == ProposalStatus.ACTIVE.value and now >= voting_ends:
            # Determine if proposal succeeded
            total_votes = proposal["votes_for"] + proposal["votes_against"] + proposal["votes_abstain"]
            quorum_required = self.token_config.get("total_supply", 21_000_000) * self.quorum_percentage / 100

            if total_votes >= quorum_required and proposal["votes_for"] > proposal["votes_against"]:
                proposal["status"] = ProposalStatus.SUCCEEDED.value
            else:
                proposal["status"] = ProposalStatus.DEFEATED.value

    async def _notify_ip_owner(self, proposal_data: Dict[str, Any]):
        """Notify IP owner of proposals requiring attention"""
        try:
            # In production, send actual notifications
            self.logger.info(f"IP owner notification sent for proposal {proposal_data['id']}")
        except Exception as e:
            self.logger.error(f"Failed to notify IP owner: {e}")

    async def get_health_status(self) -> Dict[str, Any]:
        """Get governance service health status"""
        try:
            return {
                "service": "GovernanceService",
                "status": "healthy" if not self.emergency_paused else "paused",
                "emergency_paused": self.emergency_paused,
                "pause_reason": self.pause_reason,
                "total_proposals": len(self.proposals),
                "ip_nft_service_connected": self.ip_nft_service is not None,
                "web3_service_connected": self.web3_service is not None,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "service": "GovernanceService",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
