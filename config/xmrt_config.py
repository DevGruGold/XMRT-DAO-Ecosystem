"""
XMRT DAO Ecosystem - Comprehensive Configuration

This configuration file contains all the essential settings for the XMRT DAO Ecosystem
based on the comprehensive XMRT documentation and deployed infrastructure.

Key Features:
- Correct Sepolia contract addresses for XMRT Token and XMRT-IP NFT
- Multi-chain support configuration
- AI agent configuration
- Mining pool integration settings
- Treasury management parameters
- Governance system parameters
- IP ownership rights management
"""

import os
from typing import Dict, Any

class XMRTConfig:
    """Comprehensive configuration for XMRT DAO Ecosystem"""

    # Core XMRT Token Configuration
    TOKEN_CONFIG = {
        "name": "XMRT Token",
        "symbol": "XMRT",
        "decimals": 18,
        "total_supply": 20_999_990,  # Updated from Etherscan data
        "chain_id": 11155111  # Sepolia testnet
    }

    # XMRT Intellectual Property NFT Configuration  
    IP_NFT_CONFIG = {
        "name": "XMRT Intellectual Property",
        "symbol": "XMRT-IP",
        "total_supply": 1,  # Single unique NFT representing IP ownership
        "owner": "Joseph Andrew Lee (DevGruGold)",
        "description": "On-chain representation of intellectual property ownership rights for the XMRT ecosystem",
        "chain_id": 11155111  # Sepolia testnet
    }

    # Blockchain Network Configurations
    NETWORK_CONFIG = {
        "sepolia": {
            "name": "Sepolia Testnet",
            "chain_id": 11155111,
            "rpc_url": os.getenv("SEPOLIA_RPC_URL", "https://sepolia.infura.io/v3/YOUR_INFURA_KEY"),
            "explorer_url": "https://sepolia.etherscan.io",
            "contracts": {
                # Updated with correct deployed addresses from Etherscan
                "xmrt_token": "0x77307DFbc436224d5e6f2048d2b6bDfA66998a15",
                "xmrt_ip_nft": "0x9d691fc136a846d7442d1321a2d1b6aaef494eda",
                "creator_wallet": "0xaE2402dFdD313B8c40AF06d3292B50dE1eD75F68",
                "governor": os.getenv("SEPOLIA_GOVERNOR_ADDRESS", ""),
                "staking": os.getenv("SEPOLIA_STAKING_ADDRESS", ""),
                "treasury": os.getenv("SEPOLIA_TREASURY_ADDRESS", ""),
                "bridge": os.getenv("SEPOLIA_BRIDGE_ADDRESS", "")
            }
        },
        "mainnet": {
            "name": "Ethereum Mainnet",
            "chain_id": 1,
            "rpc_url": os.getenv("MAINNET_RPC_URL", "https://mainnet.infura.io/v3/YOUR_INFURA_KEY"),
            "explorer_url": "https://etherscan.io",
            "contracts": {
                "xmrt_token": os.getenv("MAINNET_TOKEN_ADDRESS", ""),
                "xmrt_ip_nft": os.getenv("MAINNET_IP_NFT_ADDRESS", ""),
                "governor": os.getenv("MAINNET_GOVERNOR_ADDRESS", ""),
                "staking": os.getenv("MAINNET_STAKING_ADDRESS", ""),
                "treasury": os.getenv("MAINNET_TREASURY_ADDRESS", ""),
                "bridge": os.getenv("MAINNET_BRIDGE_ADDRESS", "")
            }
        },
        "polygon": {
            "name": "Polygon",
            "chain_id": 137,
            "rpc_url": os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com"),
            "explorer_url": "https://polygonscan.com",
            "contracts": {
                "xmrt_token": os.getenv("POLYGON_TOKEN_ADDRESS", ""),
                "bridge": os.getenv("POLYGON_BRIDGE_ADDRESS", "")
            }
        },
        "arbitrum": {
            "name": "Arbitrum One",
            "chain_id": 42161,
            "rpc_url": os.getenv("ARBITRUM_RPC_URL", "https://arb1.arbitrum.io/rpc"),
            "explorer_url": "https://arbiscan.io",
            "contracts": {
                "xmrt_token": os.getenv("ARBITRUM_TOKEN_ADDRESS", ""),
                "bridge": os.getenv("ARBITRUM_BRIDGE_ADDRESS", "")
            }
        }
    }

    # Governance System Configuration
    GOVERNANCE_CONFIG = {
        "voting_period": 7 * 24 * 3600,  # 7 days in seconds
        "voting_delay": 1 * 24 * 3600,   # 1 day in seconds
        "proposal_threshold": 100_000,    # XMRT tokens required to create proposal
        "quorum_percentage": 4,           # 4% quorum requirement
        "timelock_delay": 2 * 24 * 3600,  # 2 days execution delay
        "max_operations": 10,             # Maximum operations per proposal
        "grace_period": 14 * 24 * 3600,   # 14 days grace period
        "target_efficiency": 95.0,        # Target governance efficiency %
        "target_participation": 75.7,     # Target participation rate %
        "ip_owner_privileges": {
            "can_veto_proposals": True,
            "emergency_pause": True, 
            "upgrade_authorization": True,
            "treasury_override": False  # Limited for decentralization
        }
    }

    # AI Agent Configuration (Enhanced)
    AI_CONFIG = {
        "eliza_agent": {
            "name": "XMRT-DAO-Agent",
            "autonomy_level": 85,  # 85% autonomy as specified
            "decision_threshold": 0.7,
            "learning_rate": 0.01,
            "max_actions_per_cycle": 5,
            "treasury_limits": {
                "max_transaction": 50_000,  # USD
                "daily_limit": 100_000,     # USD
                "approval_threshold": 25_000  # USD
            },
            "capabilities": [
                "treasury_management",
                "proposal_analysis", 
                "cross_chain_operations",
                "mining_optimization",
                "governance_participation",
                "risk_assessment"
            ]
        },
        "gpt5_orchestrator": {
            "enabled": True,
            "coordination_interval": 300,  # 5 minutes
            "health_check_interval": 60,   # 1 minute
            "max_concurrent_operations": 3
        }
    }

    # Mining Integration Configuration (MobileMonero.com)
    MINING_CONFIG = {
        "pool_url": "https://api.mobilemonero.com/v1",
        "pool_name": "MobileMonero.com",
        "miner_address": os.getenv("XMRT_MINER_ADDRESS", ""),
        "api_key": os.getenv("MOBILE_MONERO_API_KEY", ""),
        "update_interval": 600,  # 10 minutes
        "revenue_targets": {
            "daily_xmr": 2.3,
            "monthly_usd": 45_000
        },
        "treasury_allocation": {
            "mining_rewards": 0.60,    # 60% to treasury
            "staking_rewards": 0.25,   # 25% to staking rewards
            "development": 0.10,       # 10% to development
            "community": 0.05          # 5% to community incentives
        }
    }

    # Treasury Management Configuration
    TREASURY_CONFIG = {
        "total_value_target": 1_500_000,  # $1.5M as per documentation
        "asset_allocation": {
            "ETH": 0.25,     # 25%
            "XMR": 0.15,     # 15% 
            "USDC": 0.50,    # 50%
            "XMRT": 0.10     # 10%
        },
        "rebalancing": {
            "threshold": 0.05,     # 5% deviation triggers rebalancing
            "frequency": "weekly",
            "ai_managed": True
        },
        "security": {
            "multi_sig_threshold": 3,
            "daily_withdrawal_limit": 100_000,  # USD
            "emergency_pause_threshold": 0.20   # 20% loss triggers pause
        }
    }

    # Cross-Chain Configuration
    CROSS_CHAIN_CONFIG = {
        "wormhole": {
            "enabled": True,
            "core_bridge": "0x706abc4E45D419950511e474C7B9Ed348A4a716c",  # Ethereum
            "token_bridge": "0x3ee18B2214AFF97000D974cf647E7C347E8fa585",
            "supported_chains": [1, 137, 42161, 10, 8453]  # Ethereum, Polygon, Arbitrum, Optimism, Base
        },
        "layerzero": {
            "enabled": True,
            "endpoint": os.getenv("LAYERZERO_ENDPOINT", ""),
            "supported_chains": [101, 109, 110, 111, 184]  # LayerZero chain IDs
        },
        "bridge_fees": {
            "ethereum_to_polygon": 0.001,   # ETH
            "ethereum_to_arbitrum": 0.0005, # ETH
            "base_fee_usd": 1.0
        }
    }

    # Zero-Knowledge Privacy Configuration
    ZK_CONFIG = {
        "noir": {
            "enabled": True,
            "circuit_path": "./circuits/governance.nr",
            "proving_key": os.getenv("NOIR_PROVING_KEY", ""),
            "verification_key": os.getenv("NOIR_VERIFICATION_KEY", "")
        },
        "risc_zero": {
            "enabled": True,
            "host_url": os.getenv("RISC_ZERO_HOST", ""),
            "guest_code": "./risc_zero/governance_guest"
        }
    }

    # API Configuration
    API_CONFIG = {
        "rate_limiting": {
            "requests_per_minute": 100,
            "burst_limit": 20
        },
        "authentication": {
            "jwt_secret": os.getenv("JWT_SECRET", "your-secret-key"),
            "token_expiry": 3600  # 1 hour
        },
        "cors": {
            "origins": ["http://localhost:3000", "https://xmrt.io"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_credentials": True
        }
    }

    # Monitoring and Alerting Configuration
    MONITORING_CONFIG = {
        "metrics": {
            "enabled": True,
            "prometheus_port": 9090,
            "collection_interval": 30  # seconds
        },
        "alerts": {
            "treasury_threshold": 0.05,    # 5% change
            "governance_participation": 0.70,  # 70% minimum
            "ai_agent_health": 300,        # 5 minutes offline
            "mining_revenue": 0.20         # 20% decline
        },
        "notifications": {
            "discord_webhook": os.getenv("DISCORD_WEBHOOK", ""),
            "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
            "email_smtp": os.getenv("EMAIL_SMTP", "")
        }
    }

    # Environment-Specific Configurations
    ENVIRONMENT_CONFIGS = {
        "development": {
            "debug": True,
            "auto_reload": True,
            "mock_blockchain": True,
            "test_mode": True
        },
        "staging": {
            "debug": False,
            "auto_reload": False,
            "mock_blockchain": False,
            "test_mode": True
        },
        "production": {
            "debug": False,
            "auto_reload": False,
            "mock_blockchain": False,
            "test_mode": False,
            "ssl_required": True,
            "rate_limiting_strict": True
        }
    }

    @classmethod
    def get_config(cls, env: str = None) -> Dict[str, Any]:
        """Get configuration for specified environment"""
        if env is None:
            env = os.getenv("ENVIRONMENT", "development")

        # Base configuration
        base_config = {
            "token": cls.TOKEN_CONFIG,
            "ip_nft": cls.IP_NFT_CONFIG,
            "networks": cls.NETWORK_CONFIG,
            "governance": cls.GOVERNANCE_CONFIG,
            "ai": cls.AI_CONFIG,
            "mining": cls.MINING_CONFIG,
            "treasury": cls.TREASURY_CONFIG,
            "cross_chain": cls.CROSS_CHAIN_CONFIG,
            "zk": cls.ZK_CONFIG,
            "api": cls.API_CONFIG,
            "monitoring": cls.MONITORING_CONFIG
        }

        # Merge with environment-specific config
        if env in cls.ENVIRONMENT_CONFIGS:
            base_config.update(cls.ENVIRONMENT_CONFIGS[env])

        return base_config

    @classmethod
    def get_contract_address(cls, contract_name: str, network: str = "sepolia") -> str:
        """Get contract address for specified network"""
        config = cls.get_config()
        return config["networks"][network]["contracts"].get(contract_name, "")

    @classmethod
    def is_ip_owner(cls, address: str) -> bool:
        """Check if address is the IP owner (Joseph Andrew Lee)"""
        return address.lower() == cls.NETWORK_CONFIG["sepolia"]["contracts"]["creator_wallet"].lower()

# Export default configuration
config = XMRTConfig.get_config()
