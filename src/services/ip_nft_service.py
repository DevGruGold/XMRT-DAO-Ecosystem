"""
XMRT DAO Ecosystem - IP NFT Service

This service handles intellectual property rights verification and management
for the XMRT ecosystem, including:
- XMRT-IP NFT ownership verification
- Creator privileges and authorization
- IP-based governance permissions
- NFT metadata management
- IP licensing and transfer operations

The XMRT-IP NFT (0x9d691fc136a846d7442d1321a2d1b6aaef494eda) represents
the intellectual property ownership rights held by Joseph Andrew Lee (DevGruGold)
for the entire XMRT ecosystem.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime
import json
import hashlib

from web3 import Web3
from eth_account import Account

class IPNFTService:
    """Service for managing XMRT Intellectual Property NFT operations"""

    def __init__(self, web3_service, config: Dict[str, Any]):
        self.web3_service = web3_service
        self.config = config
        self.logger = logging.getLogger(__name__)

        # IP NFT contract configuration
        self.ip_nft_config = config.get("ip_nft", {})
        self.network_config = config.get("networks", {}).get("sepolia", {})
        self.governance_config = config.get("governance", {})

        # Contract addresses
        self.ip_nft_address = self.network_config.get("contracts", {}).get("xmrt_ip_nft")
        self.creator_wallet = self.network_config.get("contracts", {}).get("creator_wallet")

        # IP owner privileges
        self.ip_privileges = self.governance_config.get("ip_owner_privileges", {})

        self.logger.info(f"IPNFTService initialized for contract: {self.ip_nft_address}")

    async def verify_ip_ownership(self, address: str) -> Dict[str, Any]:
        """
        Verify if an address owns the XMRT-IP NFT

        Args:
            address: Wallet address to check

        Returns:
            Dict containing ownership verification results
        """
        try:
            # Check if address matches known creator wallet
            is_creator = address.lower() == self.creator_wallet.lower()

            # In a full implementation, we would query the NFT contract
            # For now, we use the known creator address
            ownership_result = {
                "is_ip_owner": is_creator,
                "address": address,
                "creator_wallet": self.creator_wallet,
                "ip_nft_contract": self.ip_nft_address,
                "verification_time": datetime.utcnow().isoformat(),
                "privileges": self.ip_privileges if is_creator else {},
                "token_id": 1 if is_creator else None,
                "metadata": {
                    "name": self.ip_nft_config.get("name"),
                    "symbol": self.ip_nft_config.get("symbol"),
                    "description": self.ip_nft_config.get("description"),
                    "owner": self.ip_nft_config.get("owner")
                } if is_creator else None
            }

            self.logger.info(f"IP ownership verification for {address}: {is_creator}")
            return ownership_result

        except Exception as e:
            self.logger.error(f"Failed to verify IP ownership: {e}")
            return {
                "error": str(e),
                "is_ip_owner": False,
                "address": address
            }

    async def get_ip_privileges(self, address: str) -> Dict[str, Any]:
        """
        Get IP-based privileges for an address

        Args:
            address: Wallet address to check privileges for

        Returns:
            Dict containing available privileges
        """
        try:
            ownership = await self.verify_ip_ownership(address)

            if ownership.get("is_ip_owner", False):
                return {
                    "address": address,
                    "has_privileges": True,
                    "privileges": {
                        "can_veto_proposals": self.ip_privileges.get("can_veto_proposals", False),
                        "emergency_pause": self.ip_privileges.get("emergency_pause", False),
                        "upgrade_authorization": self.ip_privileges.get("upgrade_authorization", False),
                        "treasury_override": self.ip_privileges.get("treasury_override", False),
                        "ip_management": True,
                        "contract_deployment": True,
                        "ecosystem_governance": True
                    },
                    "privilege_level": "CREATOR",
                    "authority_score": 100
                }
            else:
                return {
                    "address": address,
                    "has_privileges": False,
                    "privileges": {},
                    "privilege_level": "STANDARD",
                    "authority_score": 0
                }

        except Exception as e:
            self.logger.error(f"Failed to get IP privileges: {e}")
            return {
                "error": str(e),
                "has_privileges": False,
                "address": address
            }

    async def authorize_action(self, address: str, action: str, 
                             proposal_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Authorize an action based on IP ownership privileges

        Args:
            address: Address requesting authorization
            action: Type of action (veto, pause, upgrade, etc.)
            proposal_data: Optional proposal data for context

        Returns:
            Dict containing authorization result
        """
        try:
            privileges = await self.get_ip_privileges(address)

            if not privileges.get("has_privileges", False):
                return {
                    "authorized": False,
                    "reason": "Address does not have IP ownership privileges",
                    "action": action,
                    "address": address
                }

            # Check specific action authorization
            action_privileges = privileges.get("privileges", {})

            authorization_map = {
                "veto_proposal": action_privileges.get("can_veto_proposals", False),
                "emergency_pause": action_privileges.get("emergency_pause", False),
                "upgrade_contract": action_privileges.get("upgrade_authorization", False),
                "treasury_override": action_privileges.get("treasury_override", False),
                "deploy_contract": action_privileges.get("contract_deployment", False),
                "manage_ip": action_privileges.get("ip_management", False)
            }

            is_authorized = authorization_map.get(action, False)

            authorization_result = {
                "authorized": is_authorized,
                "action": action,
                "address": address,
                "privilege_level": privileges.get("privilege_level"),
                "timestamp": datetime.utcnow().isoformat(),
                "proposal_id": proposal_data.get("id") if proposal_data else None,
                "reason": "IP owner authorization granted" if is_authorized else f"Action '{action}' not authorized for this address"
            }

            self.logger.info(f"Authorization for {action} by {address}: {is_authorized}")
            return authorization_result

        except Exception as e:
            self.logger.error(f"Failed to authorize action: {e}")
            return {
                "authorized": False,
                "error": str(e),
                "action": action,
                "address": address
            }

    async def get_ip_nft_metadata(self) -> Dict[str, Any]:
        """
        Get XMRT-IP NFT metadata

        Returns:
            Dict containing NFT metadata
        """
        try:
            metadata = {
                "name": self.ip_nft_config.get("name", "XMRT Intellectual Property"),
                "symbol": self.ip_nft_config.get("symbol", "XMRT-IP"),
                "description": self.ip_nft_config.get("description", ""),
                "contract_address": self.ip_nft_address,
                "chain_id": self.ip_nft_config.get("chain_id", 11155111),
                "total_supply": self.ip_nft_config.get("total_supply", 1),
                "owner": self.ip_nft_config.get("owner", ""),
                "creator_wallet": self.creator_wallet,
                "attributes": [
                    {
                        "trait_type": "IP Type",
                        "value": "Ecosystem Intellectual Property"
                    },
                    {
                        "trait_type": "Ecosystem",
                        "value": "XMRT DAO"
                    },
                    {
                        "trait_type": "Creator",
                        "value": "Joseph Andrew Lee (DevGruGold)"
                    },
                    {
                        "trait_type": "Governance Rights",
                        "value": "Full"
                    },
                    {
                        "trait_type": "Authority Level",
                        "value": "Creator"
                    }
                ],
                "image": "https://xmrt.io/assets/xmrt-ip-nft.png",  # Placeholder
                "external_url": "https://xmrt.io/ip-rights",
                "privileges": self.ip_privileges,
                "created_date": "2025-08-04",  # Based on deployment
                "network": "Sepolia Testnet"
            }

            return metadata

        except Exception as e:
            self.logger.error(f"Failed to get IP NFT metadata: {e}")
            return {"error": str(e)}

    async def validate_ip_transaction(self, from_address: str, to_address: str, 
                                    transaction_type: str) -> Dict[str, Any]:
        """
        Validate IP-related transactions (transfers, burns, etc.)

        Args:
            from_address: Source address
            to_address: Destination address  
            transaction_type: Type of transaction

        Returns:
            Dict containing validation results
        """
        try:
            # Check if this involves the IP NFT owner
            from_ownership = await self.verify_ip_ownership(from_address)
            to_ownership = await self.verify_ip_ownership(to_address)

            validation_result = {
                "valid": False,
                "transaction_type": transaction_type,
                "from_address": from_address,
                "to_address": to_address,
                "from_is_ip_owner": from_ownership.get("is_ip_owner", False),
                "to_is_ip_owner": to_ownership.get("is_ip_owner", False),
                "warnings": [],
                "restrictions": []
            }

            # Apply validation rules based on transaction type
            if transaction_type == "transfer":
                if from_ownership.get("is_ip_owner"):
                    validation_result["warnings"].append("Transferring IP NFT will transfer creator privileges")
                    validation_result["restrictions"].append("Requires governance approval for ecosystem security")

            elif transaction_type == "burn":
                if from_ownership.get("is_ip_owner"):
                    validation_result["warnings"].append("Burning IP NFT will permanently remove creator privileges")
                    validation_result["restrictions"].append("Not recommended - would decentralize control permanently")
                    validation_result["valid"] = False
                    return validation_result

            # For now, allow most transactions but with warnings
            validation_result["valid"] = True

            return validation_result

        except Exception as e:
            self.logger.error(f"Failed to validate IP transaction: {e}")
            return {
                "valid": False,
                "error": str(e),
                "transaction_type": transaction_type
            }

    async def get_creator_analytics(self) -> Dict[str, Any]:
        """
        Get analytics related to creator/IP owner activity

        Returns:
            Dict containing creator analytics
        """
        try:
            analytics = {
                "ip_owner": {
                    "address": self.creator_wallet,
                    "name": self.ip_nft_config.get("owner", ""),
                    "privileges_active": True,
                    "nft_contract": self.ip_nft_address
                },
                "ecosystem_stats": {
                    "token_contract": self.network_config.get("contracts", {}).get("xmrt_token"),
                    "total_supply": self.config.get("token", {}).get("total_supply", 0),
                    "governance_efficiency": self.governance_config.get("target_efficiency", 0),
                    "participation_rate": self.governance_config.get("target_participation", 0)
                },
                "ip_metrics": {
                    "creation_date": "2025-08-04",
                    "days_active": (datetime.utcnow() - datetime(2025, 8, 4)).days,
                    "governance_actions": 0,  # Would be tracked in production
                    "proposals_created": 0,
                    "vetos_used": 0,
                    "emergency_pauses": 0
                },
                "privileges_usage": {
                    "veto_capability": self.ip_privileges.get("can_veto_proposals", False),
                    "emergency_pause": self.ip_privileges.get("emergency_pause", False),
                    "upgrade_auth": self.ip_privileges.get("upgrade_authorization", False),
                    "treasury_override": self.ip_privileges.get("treasury_override", False)
                }
            }

            return analytics

        except Exception as e:
            self.logger.error(f"Failed to get creator analytics: {e}")
            return {"error": str(e)}

    async def check_governance_impact(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if a proposal would impact IP rights or creator privileges

        Args:
            proposal_data: Proposal data to analyze

        Returns:
            Dict containing impact analysis
        """
        try:
            impact_analysis = {
                "proposal_id": proposal_data.get("id"),
                "impacts_ip_rights": False,
                "impact_level": "NONE",
                "concerns": [],
                "recommendations": [],
                "requires_ip_approval": False
            }

            # Analyze proposal content for IP-related impacts
            title = proposal_data.get("title", "").lower()
            description = proposal_data.get("description", "").lower()
            target_contract = proposal_data.get("target_contract", "")

            # Check for sensitive operations
            sensitive_keywords = [
                "upgrade", "pause", "emergency", "ownership", "admin", 
                "governance", "treasury", "contract", "deploy", "mint"
            ]

            for keyword in sensitive_keywords:
                if keyword in title or keyword in description:
                    impact_analysis["impacts_ip_rights"] = True
                    impact_analysis["concerns"].append(f"Proposal involves '{keyword}' operations")

            # Check if targeting core contracts
            core_contracts = [
                self.ip_nft_address,
                self.network_config.get("contracts", {}).get("xmrt_token"),
                self.network_config.get("contracts", {}).get("governor")
            ]

            if target_contract and target_contract.lower() in [addr.lower() for addr in core_contracts if addr]:
                impact_analysis["impacts_ip_rights"] = True
                impact_analysis["concerns"].append("Proposal targets core ecosystem contract")

            # Determine impact level and recommendations
            if impact_analysis["impacts_ip_rights"]:
                impact_analysis["impact_level"] = "HIGH" if len(impact_analysis["concerns"]) > 2 else "MEDIUM"
                impact_analysis["requires_ip_approval"] = True
                impact_analysis["recommendations"].append("Notify IP owner for review")
                impact_analysis["recommendations"].append("Consider extended discussion period")

            return impact_analysis

        except Exception as e:
            self.logger.error(f"Failed to check governance impact: {e}")
            return {
                "error": str(e),
                "proposal_id": proposal_data.get("id"),
                "impacts_ip_rights": True,  # Err on side of caution
                "impact_level": "UNKNOWN"
            }

    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of IP NFT service

        Returns:
            Dict containing service health information
        """
        try:
            health_status = {
                "service": "IPNFTService",
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "configuration": {
                    "ip_nft_address": self.ip_nft_address,
                    "creator_wallet": self.creator_wallet,
                    "privileges_configured": len(self.ip_privileges) > 0,
                    "network": self.network_config.get("name", "Unknown")
                },
                "checks": {
                    "config_loaded": bool(self.ip_nft_config),
                    "addresses_configured": bool(self.ip_nft_address and self.creator_wallet),
                    "privileges_defined": bool(self.ip_privileges),
                    "web3_service_available": bool(self.web3_service)
                }
            }

            # Determine overall health
            all_checks_pass = all(health_status["checks"].values())
            health_status["status"] = "healthy" if all_checks_pass else "degraded"

            return health_status

        except Exception as e:
            self.logger.error(f"Failed to get health status: {e}")
            return {
                "service": "IPNFTService",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
