"""
XMRT DAO Ecosystem - Configuration with Correct Contract Addresses

Updated with accurate contract information from Sepolia testnet:
- XMRT Token (ERC-20): 0x77307DFbc436224d5e6f2048d2b6bDfA66998a15
- XMRT IP NFT (ERC-731): 0x9d691fc136a846d7442d1321a2d1b6aaef494eda  
- Creator Wallet: 0xaE2402dFdD313B8c40AF06d3292B50dE1eD75F68
- SupportXMR Mining Integration
- AI Cost Optimization System
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

    # === NEW: AI Cost Optimization Configuration ===
    # AI API Keys (from environment variables)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    QWEN_API_KEY = os.getenv('QWEN_API_KEY') 
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    
    # AI Model Configuration
    AI_CONFIG = {
        'free_models': {
            'qwen2.5': {
                'cost_per_1k_tokens': 0.0,
                'api_endpoint': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
                'enabled': bool(QWEN_API_KEY),
                'max_tokens': 4000,
                'timeout': 30
            },
            'wan2.1': {
                'cost_per_1k_tokens': 0.0,
                'enabled': True,  # Free model
                'max_tokens': 2000,
                'timeout': 20
            }
        },
        'paid_models': {
            'gpt-5-nano': {
                'input_cost_per_1k': 0.05,
                'output_cost_per_1k': 0.40,
                'model_name': 'gpt-5-nano',
                'enabled': bool(OPENAI_API_KEY),
                'max_tokens': 8000,
                'timeout': 45
            },
            'gpt-5-full': {
                'input_cost_per_1k': 1.25,
                'output_cost_per_1k': 10.00,
                'model_name': 'gpt-5',
                'enabled': bool(OPENAI_API_KEY),
                'max_tokens': 16000,
                'timeout': 60
            }
        },
        'routing': {
            'default_free_model': 'qwen2.5',
            'default_paid_model': 'gpt-5-nano',
            'complexity_threshold_simple': 0.3,
            'complexity_threshold_complex': 0.8,
            'cost_optimization_enabled': True,
            'cache_enabled': True,
            'cache_ttl_seconds': 3600  # 1 hour
        }
    }
    
    # AI Cost Management
    COST_LIMITS = {
        'daily_budget_usd': float(os.getenv('AI_DAILY_BUDGET', 50.0)),
        'monthly_budget_usd': float(os.getenv('AI_MONTHLY_BUDGET', 1000.0)),
        'alert_threshold_percentage': 80.0,
        'emergency_stop_percentage': 95.0,
        'cost_tracking_enabled': True
    }

    # AI Query Classification Patterns
    AI_QUERY_PATTERNS = {
        'simple_patterns': [
            'hello', 'hi', 'what is', 'explain', 'define', 'summary', 
            'list', 'help', 'how are you', 'status', 'ping'
        ],
        'medium_patterns': [
            'dao', 'governance', 'xmrt', 'mining', 'meshnet', 'autonomy', 
            'contract', 'token', 'blockchain', 'treasury', 'vote'
        ],
        'complex_patterns': [
            'analyze strategy', 'optimize', 'security audit', 'cross-chain', 
            'orchestrate', 'advanced governance', 'tokenomics', 'defi integration'
        ]
    }

    # Mining Configuration (SupportXMR)
    MINING_POOL_URL = "https://supportxmr.com"
    MINING_API_BASE = "https://supportxmr.com/api"
    XMRT_MINING_WALLET = "46UxNFuGM2E3UwmZWWJicaRPoRwqwW4byQkaTHkX8yPcVihp91qAVtSFipWUGJJUyTXgzSqxzDQtNLf2bsp2DX2qCCgC5mg"

    # Treasury Allocation
    TREASURY_ALLOCATION_PERCENTAGE = 0.85  # 85% to treasury
    OPERATIONAL_ALLOCATION_PERCENTAGE = 0.15  # 15% for operations

    # AI Agent Configuration (Enhanced with Cost Optimization)
    ELIZA_AGENT_CONFIG = {
        "name": "XMRT-DAO-Agent",
        "model_provider": "cost_optimized",  # Use our AI router
        "autonomy_level": 0.85,  # 85% autonomy
        "treasury_management": True,
        "governance_participation": True,
        "mining_monitoring": True,
        "ai_cost_optimization": True,
        "preferred_tier": "basic"  # Can be upgraded to premium
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

    # Monitoring Thresholds (Enhanced with AI Cost Monitoring)
    MONITORING_CONFIG = {
        "mining_offline_threshold_minutes": 30,
        "min_hashrate_threshold": 1000,  # 1 KH/s
        "api_timeout_seconds": 10,
        "ping_interval_seconds": 300,  # 5 minutes
        "ai_cost_check_interval": 3600,  # Check AI costs hourly
        "ai_usage_alert_threshold": 0.8  # Alert at 80% of budget
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
    def get_ai_config(cls) -> Dict[str, Any]:
        """Get AI configuration with environment variable validation"""
        return {
            'api_keys': {
                'openai': cls.OPENAI_API_KEY,
                'qwen': cls.QWEN_API_KEY,
                'anthropic': cls.ANTHROPIC_API_KEY
            },
            'models': cls.AI_CONFIG,
            'cost_limits': cls.COST_LIMITS,
            'query_patterns': cls.AI_QUERY_PATTERNS,
            'enabled': any([cls.OPENAI_API_KEY, cls.QWEN_API_KEY]),
            'optimization_active': cls.AI_CONFIG['routing']['cost_optimization_enabled']
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
            "ai_optimization": cls.get_ai_config(),
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

    @classmethod
    def validate_ai_config(cls) -> Dict[str, Any]:
        """Validate AI configuration and return status"""
        ai_status = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'available_models': []
        }

        # Check API keys
        if not cls.OPENAI_API_KEY:
            ai_status['warnings'].append('OpenAI API key not configured - paid models disabled')
        else:
            ai_status['available_models'].extend(['gpt-5-nano', 'gpt-5-full'])

        if not cls.QWEN_API_KEY:
            ai_status['warnings'].append('Qwen API key not configured - using fallback free model')
        else:
            ai_status['available_models'].append('qwen2.5')

        # Always available
        ai_status['available_models'].append('wan2.1')

        if not ai_status['available_models']:
            ai_status['valid'] = False
            ai_status['errors'].append('No AI models available - check API configuration')

        return ai_status

# Create configuration instance
config = XMRTConfig()

# Validate configuration on import
if not config.validate_configuration():
    raise ValueError("Invalid XMRT configuration - missing required addresses")

# Validate AI configuration
ai_validation = config.validate_ai_config()

print(f"✅ XMRT Configuration loaded successfully")
print(f"XMRT Token: {config.XMRT_TOKEN_ADDRESS}")
print(f"XMRT IP NFT: {config.XMRT_IP_NFT_ADDRESS}")
print(f"Mining Wallet: {config.XMRT_MINING_WALLET}")

if ai_validation['valid']:
    print(f"🤖 AI Cost Optimization: Enabled")
    print(f"Available Models: {', '.join(ai_validation['available_models'])}")
    if ai_validation['warnings']:
        for warning in ai_validation['warnings']:
            print(f"⚠️  {warning}")
else:
    print(f"❌ AI Configuration Issues:")
    for error in ai_validation['errors']:
        print(f"   {error}")
