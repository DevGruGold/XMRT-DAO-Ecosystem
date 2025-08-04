"""
XMRT DAO Ecosystem - Comprehensive Configuration

This configuration file contains all the essential settings for the XMRT DAO Ecosystem
based on the comprehensive XMRT documentation and deployed infrastructure.

Key Features:
- Correct Sepolia contract addresses
- Multi-chain support configuration
- AI agent configuration
- Mining pool integration settings
- Treasury management parameters
- Governance system parameters
"""

import os
from typing import Dict, Any

class XMRTConfig:
    """Comprehensive configuration for XMRT DAO Ecosystem"""

    # Core XMRT Token Configuration
    TOKEN_CONFIG = {
        "name": "XMRT Token",
        "symbol": "XMRT",
        "total_supply": 21_000_000,  # 21 million tokens
        "decimals": 18,
        "description": "XMR Token bridging real-world Monero mining with DeFi governance"
    }

    # Network Configurations
    NETWORKS = {
        "sepolia": {
            "name": "Ethereum Sepolia Testnet",
            "chain_id": 11155111,
            "rpc_url": os.getenv("SEPOLIA_RPC_URL", "https://sepolia.infura.io/v3/YOUR_PROJECT_ID"),
            "explorer_url": "https://sepolia.etherscan.io",
            "contracts": {
                # Updated with correct deployed address
                "xmrt_token": "0x77307DFbc436224d5e6f2048d2b6bDfA66998a15",
                "governor": os.getenv("SEPOLIA_GOVERNOR_ADDRESS", ""),
                "staking": os.getenv("SEPOLIA_STAKING_ADDRESS", ""),
                "treasury": os.getenv("SEPOLIA_TREASURY_ADDRESS", ""),
                "bridge": os.getenv("SEPOLIA_BRIDGE_ADDRESS", "")
            },
            "gas_settings": {
                "gas_price_gwei": 20,
                "gas_limit": 500000,
                "max_fee_per_gas": 50,
                "max_priority_fee_per_gas": 2
            }
        },
        "mainnet": {
            "name": "Ethereum Mainnet",
            "chain_id": 1,
            "rpc_url": os.getenv("MAINNET_RPC_URL", "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"),
            "explorer_url": "https://etherscan.io",
            "contracts": {
                "xmrt_token": os.getenv("MAINNET_TOKEN_ADDRESS", ""),
                "governor": os.getenv("MAINNET_GOVERNOR_ADDRESS", ""),
                "staking": os.getenv("MAINNET_STAKING_ADDRESS", ""),
                "treasury": os.getenv("MAINNET_TREASURY_ADDRESS", ""),
                "bridge": os.getenv("MAINNET_BRIDGE_ADDRESS", "")
            },
            "gas_settings": {
                "gas_price_gwei": 30,
                "gas_limit": 300000,
                "max_fee_per_gas": 100,
                "max_priority_fee_per_gas": 5
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

    # Default network
    DEFAULT_NETWORK = os.getenv("DEFAULT_NETWORK", "sepolia")

    # Treasury Configuration (Based on documentation: $1.5M treasury)
    TREASURY_CONFIG = {
        "total_value_target": 1_500_000,  # $1.5M USD
        "asset_allocation": {
            "ETH": 0.30,      # 30% ETH
            "USDC": 0.40,     # 40% USDC
            "XMR": 0.20,      # 20% XMR
            "XMRT": 0.10      # 10% XMRT
        },
        "rebalancing_threshold": 0.05,  # 5% deviation triggers rebalancing
        "emergency_reserves": 0.15,     # 15% kept as emergency reserves
        "max_single_transaction": 50000  # $50k max per transaction
    }

    # Governance Configuration (95% efficiency target from docs)
    GOVERNANCE_CONFIG = {
        "voting_delay": 1,              # 1 block delay
        "voting_period": 45818,         # ~1 week in blocks
        "proposal_threshold": 0,        # No minimum tokens to propose
        "quorum_fraction": 4,           # 4% quorum required
        "execution_delay": 172800,      # 2 days timelock
        "efficiency_target": 0.95,     # 95% governance efficiency
        "participation_target": 0.70   # 70% participation rate
    }

    # Staking Configuration
    STAKING_CONFIG = {
        "min_stake_period": 7,          # 7 days minimum
        "early_unstaking_penalty": 0.10, # 10% penalty
        "base_apr": 0.125,              # 12.5% base APR
        "max_apr": 0.25,                # 25% maximum APR
        "rewards_distribution_interval": 86400  # Daily rewards
    }

    # Mining Integration (MobileMonero.com)
    MINING_CONFIG = {
        "pool_url": "https://api.mobilemonero.com/v1",
        "pool_name": "MobileMonero.com",
        "miner_address": os.getenv("XMRT_MINER_ADDRESS", ""),
        "api_key": os.getenv("MOBILE_MONERO_API_KEY", ""),
        "update_interval": 600,         # 10 minutes
        "revenue_tracking": True,
        "auto_treasury_deposit": True,
        "min_deposit_amount": 0.1       # 0.1 XMR minimum
    }

    # AI Agent Configuration (Eliza Framework)
    AI_CONFIG = {
        "agent_name": "XMRT-DAO-Agent",
        "autonomy_level": 0.85,         # 85% autonomy
        "decision_confidence_threshold": 0.75,
        "max_treasury_decision": 10000, # $10k max autonomous decision
        "improvement_cycle_interval": 3600,  # 1 hour cycles
        "learning_rate": 0.1,
        "risk_tolerance": 0.3,          # Conservative risk profile
        "models": {
            "primary": "gpt-4",
            "fallback": "gpt-3.5-turbo",
            "embedding": "text-embedding-ada-002"
        },
        "capabilities": [
            "treasury_management",
            "governance_participation", 
            "risk_assessment",
            "performance_reporting",
            "community_engagement",
            "cross_chain_operations"
        ]
    }

    # Cross-Chain Bridge Configuration
    BRIDGE_CONFIG = {
        "protocols": {
            "wormhole": {
                "enabled": True,
                "guardian_rpc": os.getenv("WORMHOLE_RPC", ""),
                "supported_chains": ["ethereum", "polygon", "arbitrum"]
            },
            "layerzero": {
                "enabled": True,
                "endpoint": os.getenv("LAYERZERO_ENDPOINT", ""),
                "supported_chains": ["ethereum", "polygon", "arbitrum", "optimism", "base"]
            }
        },
        "fees": {
            "base_fee": 0.001,          # 0.1% base bridge fee
            "gas_multiplier": 1.5       # 1.5x gas estimation
        },
        "limits": {
            "min_bridge_amount": 10,    # 10 XMRT minimum
            "max_bridge_amount": 100000, # 100k XMRT maximum
            "daily_limit": 500000       # 500k XMRT daily limit
        }
    }

    # API Configuration
    API_CONFIG = {
        "version": "1.0.0",
        "base_url": os.getenv("API_BASE_URL", "http://localhost:5000"),
        "rate_limits": {
            "requests_per_minute": 100,
            "requests_per_hour": 1000
        },
        "authentication": {
            "jwt_secret": os.getenv("JWT_SECRET", "your-secret-key"),
            "token_expiry": 3600,       # 1 hour
            "refresh_token_expiry": 604800  # 7 days
        },
        "cors": {
            "origins": ["http://localhost:3000", "https://xmrt.io"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "headers": ["Content-Type", "Authorization"]
        }
    }

    # Database Configuration
    DATABASE_CONFIG = {
        "postgresql": {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", 5432),
            "database": os.getenv("DB_NAME", "xmrt_dao"),
            "username": os.getenv("DB_USER", "xmrt"),
            "password": os.getenv("DB_PASSWORD", ""),
            "pool_size": 20,
            "max_overflow": 30
        },
        "redis": {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": os.getenv("REDIS_PORT", 6379),
            "password": os.getenv("REDIS_PASSWORD", ""),
            "db": 0,
            "decode_responses": True
        }
    }

    # Monitoring Configuration
    MONITORING_CONFIG = {
        "prometheus": {
            "enabled": True,
            "port": 8000,
            "metrics_path": "/metrics"
        },
        "logging": {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "max_file_size": "100MB",
            "backup_count": 5
        },
        "alerts": {
            "treasury_threshold": 0.05,    # 5% change alert
            "governance_efficiency": 0.90, # Below 90% efficiency alert
            "system_uptime": 0.999,        # Below 99.9% uptime alert
            "response_time": 1.0           # Above 1s response time alert
        }
    }

    # Security Configuration
    SECURITY_CONFIG = {
        "multi_sig": {
            "required_signatures": 3,
            "total_signers": 5,
            "emergency_signatures": 2
        },
        "rate_limiting": {
            "enabled": True,
            "requests_per_second": 10,
            "burst_limit": 50
        },
        "encryption": {
            "algorithm": "AES-256",
            "key_rotation_interval": 2592000  # 30 days
        }
    }

    # Environment-specific configurations
    ENVIRONMENT_CONFIGS = {
        "development": {
            "debug": True,
            "auto_reload": True,
            "log_level": "DEBUG",
            "network": "sepolia"
        },
        "staging": {
            "debug": False,
            "auto_reload": False,
            "log_level": "INFO",
            "network": "sepolia"
        },
        "production": {
            "debug": False,
            "auto_reload": False,
            "log_level": "WARNING",
            "network": "mainnet"
        }
    }

    @classmethod
    def get_config(cls, environment: str = None) -> Dict[str, Any]:
        """Get configuration for specific environment"""
        env = environment or os.getenv("ENVIRONMENT", "development")

        base_config = {
            "token": cls.TOKEN_CONFIG,
            "networks": cls.NETWORKS,
            "default_network": cls.DEFAULT_NETWORK,
            "treasury": cls.TREASURY_CONFIG,
            "governance": cls.GOVERNANCE_CONFIG,
            "staking": cls.STAKING_CONFIG,
            "mining": cls.MINING_CONFIG,
            "ai": cls.AI_CONFIG,
            "bridge": cls.BRIDGE_CONFIG,
            "api": cls.API_CONFIG,
            "database": cls.DATABASE_CONFIG,
            "monitoring": cls.MONITORING_CONFIG,
            "security": cls.SECURITY_CONFIG
        }

        # Merge with environment-specific config
        if env in cls.ENVIRONMENT_CONFIGS:
            base_config.update(cls.ENVIRONMENT_CONFIGS[env])

        return base_config

# Export default configuration
config = XMRTConfig.get_config()
