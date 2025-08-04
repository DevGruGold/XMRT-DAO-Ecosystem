"""
XMRT DAO Ecosystem - Configuration with Correct Contract Addresses

Updated with accurate contract information from Sepolia testnet:
- XMRT Token (ERC-20): 0x77307DFbc436224d5e6f2048d2b6bDfA66998a15
- XMRT IP NFT (ERC-731): 0x9d691fc136a846d7442d1321a2d1b6aaef494eda  
- Creator Wallet: 0xaE2402dFdD313B8c40AF06d3292B50dE1eD75F68
- SupportXMR Mining Integration
"""

import os
from typing import Dict, Any

class XMRTConfig:
    """Enhanced XMRT DAO Ecosystem Configuration"""

    # Correct Contract Addresses (Sepolia Testnet)
    XMRT_TOKEN_ADDRESS = "0x77307DFbc436224d5e6f2048d2b6bDfA66998a15"
    XMRT_IP_NFT_ADDRESS = "0x9d691fc136a846d7442d1321a2d1b6aaef494eda"
    CREATOR_WALLET_ADDRESS = "0xaE2402dFdD313B8c40AF06d3292B50dE1eD75F68"

    # Network Configuration
    SEPOLIA_TESTNET_ID = 11155111
    SEPOLIA_RPC_URL = "https://sepolia.infura.io/v3/YOUR_INFURA_KEY"

    # Mining Configuration (SupportXMR)
    MINING_POOL_URL = "https://supportxmr.com"
    MINING_API_BASE = "https://supportxmr.com/api"
    XMRT_MINING_WALLET = "46UxNFuGM2E3UwmZWWJicaRPoRwqwW4byQkaTHkX8yPcVihp91qAVtSFipWUGJJUyTXgzSqxzDQtNLf2bsp2DX2qCCgC5mg"

    # Treasury Allocation
    TREASURY_ALLOCATION_PERCENTAGE = 0.85  # 85% to treasury
    OPERATIONAL_ALLOCATION_PERCENTAGE = 0.15  # 15% for operations

    # AI Agent Configuration
    ELIZA_AGENT_CONFIG = {
        "name": "XMRT-DAO-Agent",
        "model_provider": "openai",
        "autonomy_level": 0.85,  # 85% autonomy
        "treasury_management": True,
        "governance_participation": True,
        "mining_monitoring": True
    }

    # Redis Configuration
    REDIS_CONFIG = {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", 6379)),
        "db": int(os.getenv("REDIS_DB", 0)),
        "password": os.getenv("REDIS_PASSWORD"),
        "cache_ttl": 120  # 2 minutes default
    }

    # API Configuration
    API_CONFIG = {
        "cors_origins": ["*"],
        "rate_limit": "100/hour",
        "websocket_enabled": True,
        "monitoring_interval": 60  # seconds
    }

    # Monitoring Thresholds
    MONITORING_CONFIG = {
        "mining_offline_threshold_minutes": 30,
        "min_hashrate_threshold": 1000,  # 1 KH/s
        "api_timeout_seconds": 10,
        "ping_interval_seconds": 300  # 5 minutes
    }

    # Future Network Configuration (Mainnet Deployment)
    FUTURE_NETWORKS = {
        "polygon": {
            "chain_id": 137,
            "rpc_url": "https://polygon-rpc.com",
            "gas_price_strategy": "fast",
            "deployment_planned": True
        },
        "starknet": {
            "chain_id": "mainnet",
            "rpc_url": "https://alpha-mainnet.starknet.io",
            "deployment_planned": True,
            "gas_optimization": True
        }
    }

    @classmethod
    def get_complete_config(cls) -> Dict[str, Any]:
        """Get complete configuration dictionary"""
        return {
            "contracts": {
                "xmrt_token": cls.XMRT_TOKEN_ADDRESS,
                "xmrt_ip_nft": cls.XMRT_IP_NFT_ADDRESS,
                "creator_wallet": cls.CREATOR_WALLET_ADDRESS
            },
            "mining": {
                "pool_url": cls.MINING_POOL_URL,
                "api_base": cls.MINING_API_BASE,
                "wallet": cls.XMRT_MINING_WALLET,
                "treasury_allocation": cls.TREASURY_ALLOCATION_PERCENTAGE,
                "operational_allocation": cls.OPERATIONAL_ALLOCATION_PERCENTAGE
            },
            "ai_agent": cls.ELIZA_AGENT_CONFIG,
            "redis": cls.REDIS_CONFIG,
            "api": cls.API_CONFIG,
            "monitoring": cls.MONITORING_CONFIG,
            "future_networks": cls.FUTURE_NETWORKS
        }

    @classmethod
    def validate_configuration(cls) -> bool:
        """Validate that all required configuration is present"""
        required_addresses = [
            cls.XMRT_TOKEN_ADDRESS,
            cls.XMRT_IP_NFT_ADDRESS,
            cls.CREATOR_WALLET_ADDRESS,
            cls.XMRT_MINING_WALLET
        ]

        for address in required_addresses:
            if not address or len(address) < 10:
                return False

        return True

# Create configuration instance
config = XMRTConfig()

# Validate configuration on import
if not config.validate_configuration():
    raise ValueError("Invalid XMRT configuration - missing required addresses")

print(f"✅ XMRT Configuration loaded successfully")
print(f"XMRT Token: {config.XMRT_TOKEN_ADDRESS}")
print(f"XMRT IP NFT: {config.XMRT_IP_NFT_ADDRESS}")
print(f"Mining Wallet: {config.XMRT_MINING_WALLET}")
