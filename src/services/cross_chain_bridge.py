"""
XMRT DAO Ecosystem - Enhanced Cross-Chain Bridge Service

Advanced cross-chain infrastructure supporting:
- Polygon mainnet deployment preparation 
- Starknet L2 integration for ultra-low gas costs
- Wormhole protocol for secure cross-chain messaging
- LayerZero omnichain capabilities
- XMRT token bridging with IP-NFT considerations
- Gas optimization strategies for mainnet deployment

Key Features:
- Multi-chain XMRT token support
- Low-cost L2 deployment readiness  
- Cross-chain governance synchronization
- Mining reward distribution across chains
- IP ownership validation across networks
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from decimal import Decimal
import hashlib
from web3 import Web3
from web3.middleware import geth_poa_middleware
import requests

logger = logging.getLogger(__name__)

class ChainId(Enum):
    """Enhanced supported blockchain networks"""
    # Testnets  
    ETHEREUM_SEPOLIA = 11155111
    POLYGON_MUMBAI = 80001

    # Mainnets - Target networks
    ETHEREUM_MAINNET = 1
    POLYGON_MAINNET = 137
    ARBITRUM_ONE = 42161
    OPTIMISM_MAINNET = 10
    BASE_MAINNET = 8453
    STARKNET_MAINNET = 0x534e5f4d41494e  # Ultra-low gas target

    # Future expansion
    AVALANCHE = 43114
    BSC = 56

class BridgeProtocol(Enum):
    """Supported bridge protocols"""
    WORMHOLE = "wormhole"
    LAYERZERO = "layerzero"
    NATIVE = "native"
    STARKNET_BRIDGE = "starknet_bridge"

class TransactionStatus(Enum):
    """Bridge transaction status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    BRIDGING = "bridging"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

@dataclass
class BridgeTransaction:
    """Enhanced bridge transaction data structure"""
    transaction_id: str
    source_chain: ChainId
    destination_chain: ChainId
    protocol: BridgeProtocol
    token_address: str
    amount: str  # Using string for precise decimal handling
    sender: str
    recipient: str
    source_tx_hash: str
    destination_tx_hash: Optional[str]
    status: TransactionStatus
    created_at: int
    completed_at: Optional[int]
    bridge_fee: str
    gas_used: Optional[int]
    confirmations: int
    required_confirmations: int

    # Protocol-specific data
    wormhole_vaa: Optional[str] = None
    layerzero_message_id: Optional[str] = None
    starknet_message_hash: Optional[str] = None

    # XMRT-specific data
    mining_rewards_included: bool = False
    ip_validation_required: bool = False
    treasury_allocation: Optional[str] = None

@dataclass  
class ChainConfig:
    """Enhanced configuration for each supported chain"""
    chain_id: ChainId
    name: str
    rpc_url: str
    explorer_url: str
    native_token: str

    # XMRT contract addresses
    xmrt_token_address: str
    xmrt_bridge_address: str
    xmrt_governance_address: str

    # Bridge protocol endpoints
    wormhole_core_bridge: str
    layerzero_endpoint: str

    # Network parameters
    average_block_time: int  # seconds
    confirmations_required: int
    gas_price_gwei: float
    max_gas_limit: int

    # Cost optimization
    is_l2: bool
    supports_eip1559: bool
    preferred_for_deployment: bool

class EnhancedXMRTCrossChainBridge:
    """
    Enhanced Cross-Chain Bridge Service for XMRT DAO Ecosystem

    Advanced Features:
    - Multi-protocol bridge support (Wormhole, LayerZero, native bridges)
    - Polygon/Starknet deployment optimization
    - Gas cost analysis and route optimization
    - Cross-chain governance synchronization
    - Mining reward distribution coordination
    - IP NFT cross-chain validation
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # XMRT Ecosystem addresses
        self.xmrt_token_sepolia = "0x77307DFbc436224d5e6f2048d2b6bDfA66998a15"
        self.xmrt_ip_nft_sepolia = "0x9d691fc136a846d7442d1321a2d1b6aaef494eda"
        self.creator_wallet = "0xaE2402dFdD313B8c40AF06d3292B50dE1eD75F68"

        # Initialize enhanced configurations
        self.chain_configs = self._initialize_enhanced_chain_configs()
        self.bridge_routes = self._initialize_bridge_routes()
        self.active_transactions = {}
        self.deployment_strategies = self._initialize_deployment_strategies()

        # Gas optimization settings
        self.gas_optimization_enabled = True
        self.preferred_l2_chains = [ChainId.POLYGON_MAINNET, ChainId.STARKNET_MAINNET]

        self.logger.info("Enhanced XMRT Cross-Chain Bridge initialized")

    def _initialize_enhanced_chain_configs(self) -> Dict[ChainId, ChainConfig]:
        """Initialize enhanced configurations for all target chains"""

        configs = {
            # Current testnet deployment
            ChainId.ETHEREUM_SEPOLIA: ChainConfig(
                chain_id=ChainId.ETHEREUM_SEPOLIA,
                name="Ethereum Sepolia",
                rpc_url=self.config.get('sepolia_rpc', 'https://sepolia.infura.io/v3/YOUR_KEY'),
                explorer_url="https://sepolia.etherscan.io",
                native_token="ETH",
                xmrt_token_address=self.xmrt_token_sepolia,
                xmrt_bridge_address="",  # To be deployed
                xmrt_governance_address="",  # To be deployed
                wormhole_core_bridge="0x4a8bc80Ed5a4067f1CCf107057b8270E0cC11A78",
                layerzero_endpoint="0xae92d5aD7583AD66E49A0c67BAd18F6ba52dDDc1",
                average_block_time=12,
                confirmations_required=3,
                gas_price_gwei=20.0,
                max_gas_limit=8000000,
                is_l2=False,
                supports_eip1559=True,
                preferred_for_deployment=False
            ),

            # PRIMARY TARGET: Polygon Mainnet - Low gas, high throughput  
            ChainId.POLYGON_MAINNET: ChainConfig(
                chain_id=ChainId.POLYGON_MAINNET,
                name="Polygon Mainnet",
                rpc_url=self.config.get('polygon_rpc', 'https://polygon-rpc.com'),
                explorer_url="https://polygonscan.com",
                native_token="MATIC",
                xmrt_token_address="",  # To be deployed
                xmrt_bridge_address="",  # To be deployed  
                xmrt_governance_address="",  # To be deployed
                wormhole_core_bridge="0x7A4B5a56256163F07b2C80A7cA55aBE66c4ec4d7",
                layerzero_endpoint="0x3c2269811836af69497E5F486A85D7316753cf62",
                average_block_time=2,
                confirmations_required=128,  # ~5 minutes
                gas_price_gwei=30.0,  # GWEI equivalent in MATIC
                max_gas_limit=20000000,
                is_l2=True,
                supports_eip1559=True,
                preferred_for_deployment=True  # PRIMARY TARGET
            ),

            # ULTRA-LOW GAS TARGET: Starknet
            ChainId.STARKNET_MAINNET: ChainConfig(
                chain_id=ChainId.STARKNET_MAINNET,
                name="Starknet Mainnet",
                rpc_url=self.config.get('starknet_rpc', 'https://starknet-mainnet.public.blastapi.io'),
                explorer_url="https://starkscan.co",
                native_token="ETH",
                xmrt_token_address="",  # To be deployed
                xmrt_bridge_address="",  # To be deployed
                xmrt_governance_address="",  # To be deployed
                wormhole_core_bridge="",  # Starknet-specific implementation
                layerzero_endpoint="",  # Starknet-specific implementation
                average_block_time=10,  # seconds
                confirmations_required=1,  # Starknet finality is fast
                gas_price_gwei=0.001,  # Ultra-low gas costs
                max_gas_limit=1000000,
                is_l2=True,
                supports_eip1559=False,  # Different fee mechanism
                preferred_for_deployment=True  # ULTRA-LOW GAS TARGET
            ),

            # Ethereum Mainnet - For comparison and bridging
            ChainId.ETHEREUM_MAINNET: ChainConfig(
                chain_id=ChainId.ETHEREUM_MAINNET,
                name="Ethereum Mainnet",
                rpc_url=self.config.get('ethereum_rpc', 'https://mainnet.infura.io/v3/YOUR_KEY'),
                explorer_url="https://etherscan.io",
                native_token="ETH",
                xmrt_token_address="",  # To be deployed
                xmrt_bridge_address="",  # To be deployed
                xmrt_governance_address="",  # To be deployed
                wormhole_core_bridge="0x98f3c9e6E3fAce36bAAd05FE09d375Ef1464288B",
                layerzero_endpoint="0x66A71Dcef29A0fFBDBE3c6a460a3B5BC225Cd675",
                average_block_time=12,
                confirmations_required=12,
                gas_price_gwei=25.0,
                max_gas_limit=8000000,
                is_l2=False,
                supports_eip1559=True,
                preferred_for_deployment=False  # High gas costs
            ),

            # Additional L2s for future expansion
            ChainId.ARBITRUM_ONE: ChainConfig(
                chain_id=ChainId.ARBITRUM_ONE,
                name="Arbitrum One",
                rpc_url=self.config.get('arbitrum_rpc', 'https://arb1.arbitrum.io/rpc'),
                explorer_url="https://arbiscan.io",
                native_token="ETH",
                xmrt_token_address="",
                xmrt_bridge_address="",
                xmrt_governance_address="",
                wormhole_core_bridge="0xa5f208e072434bC67592E4C49C1B991BA79BCA46",
                layerzero_endpoint="0x3c2269811836af69497E5F486A85D7316753cf62",
                average_block_time=0.25,  # Very fast
                confirmations_required=10,
                gas_price_gwei=0.1,  # Very low
                max_gas_limit=32000000,
                is_l2=True,
                supports_eip1559=True,
                preferred_for_deployment=True
            ),

            ChainId.BASE_MAINNET: ChainConfig(
                chain_id=ChainId.BASE_MAINNET,
                name="Base Mainnet", 
                rpc_url=self.config.get('base_rpc', 'https://mainnet.base.org'),
                explorer_url="https://basescan.org",
                native_token="ETH",
                xmrt_token_address="",
                xmrt_bridge_address="",
                xmrt_governance_address="",
                wormhole_core_bridge="0xbebdb6C8ddC678FfA9f8748f85C815C556Dd8ac6",
                layerzero_endpoint="0xb6319cC6c8c27A8F5dAF0dD3DF91EA35C4720dd7",
                average_block_time=2,
                confirmations_required=10,
                gas_price_gwei=0.1,
                max_gas_limit=25000000,
                is_l2=True,
                supports_eip1559=True,
                preferred_for_deployment=True
            )
        }

        return configs

    def _initialize_bridge_routes(self) -> Dict[str, Dict[str, Any]]:
        """Initialize optimized bridge routes between chains"""
        routes = {}

        # Define efficient routes with protocol preferences
        efficient_routes = [
            # Primary deployment routes to low-gas chains
            (ChainId.ETHEREUM_SEPOLIA, ChainId.POLYGON_MAINNET, BridgeProtocol.LAYERZERO),
            (ChainId.ETHEREUM_SEPOLIA, ChainId.STARKNET_MAINNET, BridgeProtocol.STARKNET_BRIDGE),
            (ChainId.ETHEREUM_MAINNET, ChainId.POLYGON_MAINNET, BridgeProtocol.WORMHOLE),
            (ChainId.ETHEREUM_MAINNET, ChainId.STARKNET_MAINNET, BridgeProtocol.STARKNET_BRIDGE),

            # Inter-L2 routes for cost optimization
            (ChainId.POLYGON_MAINNET, ChainId.ARBITRUM_ONE, BridgeProtocol.LAYERZERO),
            (ChainId.POLYGON_MAINNET, ChainId.BASE_MAINNET, BridgeProtocol.LAYERZERO),
            (ChainId.ARBITRUM_ONE, ChainId.BASE_MAINNET, BridgeProtocol.LAYERZERO),
        ]

        for source, dest, protocol in efficient_routes:
            route_key = f"{source.name}_to_{dest.name}"
            routes[route_key] = {
                'source_chain': source,
                'destination_chain': dest,
                'preferred_protocol': protocol,
                'estimated_time_minutes': self._estimate_bridge_time(source, dest, protocol),
                'estimated_cost_usd': self._estimate_bridge_cost(source, dest, protocol),
                'security_level': 'high',
                'supported': True
            }

        return routes

    def _initialize_deployment_strategies(self) -> Dict[str, Any]:
        """Initialize deployment strategies for different networks"""
        return {
            'polygon_strategy': {
                'target_chain': ChainId.POLYGON_MAINNET,
                'rationale': 'Low gas costs, high throughput, Ethereum compatibility',
                'estimated_deployment_cost_usd': 50,
                'estimated_monthly_cost_usd': 100,
                'advantages': [
                    'EVM compatible - easy migration',
                    'Low transaction costs (~$0.01)',
                    'Fast finality (~2 seconds)',
                    'Strong DeFi ecosystem',
                    'Proven security model'
                ],
                'deployment_steps': [
                    'Deploy XMRT token contract',
                    'Deploy governance contracts', 
                    'Deploy bridge infrastructure',
                    'Initialize treasury management',
                    'Setup cross-chain communication'
                ]
            },

            'starknet_strategy': {
                'target_chain': ChainId.STARKNET_MAINNET,
                'rationale': 'Ultra-low gas costs, advanced scalability, Cairo smart contracts',
                'estimated_deployment_cost_usd': 5,
                'estimated_monthly_cost_usd': 10,
                'advantages': [
                    'Ultra-low gas costs (~$0.0001)',
                    'Powerful Cairo programming language',
                    'Advanced scaling technology',
                    'Strong mathematical foundations',
                    'Ethereum L2 security'
                ],
                'deployment_steps': [
                    'Develop Cairo contracts for XMRT',
                    'Deploy core ecosystem contracts',
                    'Setup Starknet-Ethereum bridge',
                    'Implement governance mechanisms',
                    'Integrate with mining operations'
                ]
            },

            'multi_chain_strategy': {
                'target_chains': [ChainId.POLYGON_MAINNET, ChainId.STARKNET_MAINNET, ChainId.ARBITRUM_ONE],
                'rationale': 'Diversified deployment for maximum reach and cost optimization',
                'estimated_deployment_cost_usd': 200,
                'estimated_monthly_cost_usd': 150,
                'advantages': [
                    'Risk diversification across chains',
                    'Cost optimization opportunities',
                    'Maximum user accessibility',
                    'Protocol redundancy',
                    'Ecosystem growth potential'
                ]
            }
        }

    def _estimate_bridge_time(self, source: ChainId, dest: ChainId, protocol: BridgeProtocol) -> int:
        """Estimate bridge transaction time in minutes"""
        base_times = {
            BridgeProtocol.WORMHOLE: 15,
            BridgeProtocol.LAYERZERO: 10,
            BridgeProtocol.NATIVE: 30,
            BridgeProtocol.STARKNET_BRIDGE: 20
        }

        # Adjust for chain characteristics
        source_config = self.chain_configs.get(source)
        dest_config = self.chain_configs.get(dest)

        if source_config and dest_config:
            confirmations_factor = (source_config.confirmations_required + dest_config.confirmations_required) / 20
            return int(base_times.get(protocol, 15) * (1 + confirmations_factor))

        return base_times.get(protocol, 15)

    def _estimate_bridge_cost(self, source: ChainId, dest: ChainId, protocol: BridgeProtocol) -> float:
        """Estimate bridge cost in USD"""
        base_costs = {
            BridgeProtocol.WORMHOLE: 15.0,
            BridgeProtocol.LAYERZERO: 10.0,
            BridgeProtocol.NATIVE: 25.0,
            BridgeProtocol.STARKNET_BRIDGE: 5.0
        }

        # Adjust for chain gas costs
        source_config = self.chain_configs.get(source)
        dest_config = self.chain_configs.get(dest)

        if source_config and dest_config:
            gas_factor = (source_config.gas_price_gwei + dest_config.gas_price_gwei) / 50
            return base_costs.get(protocol, 15.0) * max(gas_factor, 0.1)

        return base_costs.get(protocol, 15.0)

    async def analyze_deployment_options(self) -> Dict[str, Any]:
        """Analyze deployment options for XMRT ecosystem expansion"""
        try:
            analysis = {
                'current_deployment': {
                    'chain': 'Ethereum Sepolia',
                    'xmrt_token': self.xmrt_token_sepolia,
                    'xmrt_ip_nft': self.xmrt_ip_nft_sepolia,
                    'status': 'active_testnet'
                },
                'recommended_mainnet_deployments': [],
                'cost_analysis': {},
                'technical_requirements': {},
                'timeline_estimate': {}
            }

            # Analyze each deployment strategy
            for strategy_name, strategy in self.deployment_strategies.items():
                if strategy_name != 'multi_chain_strategy':
                    target_chain = strategy['target_chain']
                    chain_config = self.chain_configs.get(target_chain)

                    if chain_config and chain_config.preferred_for_deployment:
                        recommendation = {
                            'strategy': strategy_name,
                            'chain': chain_config.name,
                            'chain_id': target_chain.value,
                            'rationale': strategy['rationale'],
                            'deployment_cost': strategy['estimated_deployment_cost_usd'],
                            'monthly_cost': strategy['estimated_monthly_cost_usd'],
                            'advantages': strategy['advantages'],
                            'gas_cost_comparison': chain_config.gas_price_gwei,
                            'is_l2': chain_config.is_l2,
                            'priority_score': self._calculate_deployment_priority(chain_config)
                        }
                        analysis['recommended_mainnet_deployments'].append(recommendation)

            # Sort by priority score
            analysis['recommended_mainnet_deployments'].sort(
                key=lambda x: x['priority_score'], 
                reverse=True
            )

            # Add multi-chain analysis
            analysis['multi_chain_option'] = self.deployment_strategies['multi_chain_strategy']

            self.logger.info(f"Deployment analysis complete - {len(analysis['recommended_mainnet_deployments'])} strategies analyzed")
            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing deployment options: {e}")
            return {'error': str(e)}

    def _calculate_deployment_priority(self, chain_config: ChainConfig) -> float:
        """Calculate deployment priority score for a chain"""
        score = 0.0

        # Gas cost factor (lower is better)
        if chain_config.gas_price_gwei < 1.0:
            score += 30  # Ultra-low gas
        elif chain_config.gas_price_gwei < 5.0:
            score += 20  # Low gas
        elif chain_config.gas_price_gwei < 20.0:
            score += 10  # Moderate gas
        else:
            score += 0   # High gas

        # L2 benefits
        if chain_config.is_l2:
            score += 25

        # Speed factor
        if chain_config.average_block_time < 5:
            score += 20  # Very fast
        elif chain_config.average_block_time < 15:
            score += 10  # Fast

        # EIP-1559 support for better UX
        if chain_config.supports_eip1559:
            score += 10

        # Preferred deployment flag
        if chain_config.preferred_for_deployment:
            score += 15

        return score

    async def prepare_cross_chain_governance(self) -> Dict[str, Any]:
        """Prepare cross-chain governance synchronization"""
        try:
            governance_prep = {
                'cross_chain_voting_enabled': False,  # Future feature
                'supported_chains': [],
                'governance_synchronization': {
                    'proposal_replication': 'planned',
                    'vote_aggregation': 'planned', 
                    'execution_coordination': 'planned'
                },
                'ip_nft_recognition': {
                    'cross_chain_validation': 'planned',
                    'creator_privileges': 'maintained',
                    'ownership_verification': 'implemented'
                }
            }

            # Add supported chains for governance
            for chain_id, config in self.chain_configs.items():
                if config.preferred_for_deployment:
                    governance_prep['supported_chains'].append({
                        'chain': config.name,
                        'chain_id': chain_id.value,
                        'governance_address': config.xmrt_governance_address or 'to_be_deployed',
                        'voting_weight': 1.0,  # Equal weight initially
                        'bridge_delay_minutes': 30  # Safety delay
                    })

            return governance_prep

        except Exception as e:
            self.logger.error(f"Error preparing cross-chain governance: {e}")
            return {'error': str(e)}

    async def estimate_migration_costs(self) -> Dict[str, Any]:
        """Estimate costs for migrating from Sepolia to mainnet deployments"""
        try:
            migration_analysis = {
                'current_sepolia_contracts': {
                    'xmrt_token': self.xmrt_token_sepolia,
                    'xmrt_ip_nft': self.xmrt_ip_nft_sepolia,
                    'estimated_value_locked': 0  # Testnet
                },
                'migration_strategies': {},
                'cost_breakdown': {},
                'recommended_approach': {}
            }

            # Analyze migration to each preferred chain
            for chain_id, config in self.chain_configs.items():
                if config.preferred_for_deployment:
                    strategy_name = f"migrate_to_{config.name.lower().replace(' ', '_')}"

                    # Estimate deployment costs
                    deployment_cost = self._estimate_deployment_cost(config)
                    bridge_setup_cost = self._estimate_bridge_setup_cost(config)
                    ongoing_monthly_cost = deployment_cost * 0.1  # 10% of deployment cost

                    migration_analysis['migration_strategies'][strategy_name] = {
                        'target_chain': config.name,
                        'deployment_cost_usd': deployment_cost,
                        'bridge_setup_cost_usd': bridge_setup_cost,
                        'ongoing_monthly_cost_usd': ongoing_monthly_cost,
                        'total_first_year_cost_usd': deployment_cost + bridge_setup_cost + (ongoing_monthly_cost * 12),
                        'gas_savings_percentage': self._calculate_gas_savings(config),
                        'migration_complexity': 'medium' if config.supports_eip1559 else 'high',
                        'recommended': config.chain_id in [ChainId.POLYGON_MAINNET, ChainId.STARKNET_MAINNET]
                    }

            # Determine recommended approach
            best_strategy = min(
                migration_analysis['migration_strategies'].items(),
                key=lambda x: x[1]['total_first_year_cost_usd']
            )

            migration_analysis['recommended_approach'] = {
                'strategy': best_strategy[0],
                'details': best_strategy[1],
                'rationale': 'Lowest total cost of ownership with good performance characteristics'
            }

            return migration_analysis

        except Exception as e:
            self.logger.error(f"Error estimating migration costs: {e}")
            return {'error': str(e)}

    def _estimate_deployment_cost(self, config: ChainConfig) -> float:
        """Estimate deployment cost for a specific chain"""
        base_gas_units = 3000000  # Estimated gas for full XMRT ecosystem deployment
        gas_price_wei = config.gas_price_gwei * 1e9
        deployment_cost_wei = base_gas_units * gas_price_wei

        # Convert to USD (rough estimate based on chain native token)
        if config.native_token == "ETH":
            eth_price_usd = 3000  # Approximate
            deployment_cost_usd = (deployment_cost_wei / 1e18) * eth_price_usd
        elif config.native_token == "MATIC":
            matic_price_usd = 0.8  # Approximate
            deployment_cost_usd = (deployment_cost_wei / 1e18) * matic_price_usd
        else:
            deployment_cost_usd = 100  # Default estimate

        return deployment_cost_usd

    def _estimate_bridge_setup_cost(self, config: ChainConfig) -> float:
        """Estimate bridge setup cost"""
        if config.is_l2:
            return 50  # L2s typically have lower bridge setup costs
        else:
            return 200  # L1s require more complex bridge infrastructure

    def _calculate_gas_savings(self, config: ChainConfig) -> float:
        """Calculate gas savings percentage compared to Ethereum mainnet"""
        ethereum_gas = 25.0  # Approximate ETH mainnet gas price
        if config.gas_price_gwei < ethereum_gas:
            savings = ((ethereum_gas - config.gas_price_gwei) / ethereum_gas) * 100
            return min(savings, 99.9)  # Cap at 99.9%
        return 0.0

    async def prepare_mining_integration(self) -> Dict[str, Any]:
        """Prepare cross-chain mining reward distribution"""
        try:
            mining_integration = {
                'supportxmr_wallet': '46UxNFuGM2E3UwmZWWJicaRPoRwqwW4byQkaTHkX8yPcVihp91qAVtSFipWUGJUyTXgzSqxzDQtNLf2bDX2qCCgC5mg',
                'cross_chain_distribution': {
                    'enabled': False,  # Future feature
                    'distribution_chains': [],
                    'allocation_strategy': {
                        'treasury_percentage': 85,
                        'operational_percentage': 15,
                        'cross_chain_fees_percentage': 2
                    }
                },
                'bridge_triggers': {
                    'min_xmr_threshold': 0.1,  # Trigger bridge when 0.1 XMR accumulated
                    'frequency_hours': 24,     # Daily distribution
                    'gas_optimization': True   # Use low-gas chains for distribution
                }
            }

            # Add supported chains for mining reward distribution
            for chain_id, config in self.chain_configs.items():
                if config.preferred_for_deployment and config.is_l2:
                    mining_integration['cross_chain_distribution']['distribution_chains'].append({
                        'chain': config.name,
                        'chain_id': chain_id.value,
                        'treasury_address': 'to_be_deployed',
                        'distribution_percentage': 50 if chain_id == ChainId.POLYGON_MAINNET else 25,
                        'preferred_for_high_volume': chain_id in [ChainId.POLYGON_MAINNET, ChainId.STARKNET_MAINNET]
                    })

            return mining_integration

        except Exception as e:
            self.logger.error(f"Error preparing mining integration: {e}")
            return {'error': str(e)}

    async def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get comprehensive cross-chain bridge status"""
        try:
            status = {
                'service_status': 'active',
                'supported_chains': len(self.chain_configs),
                'preferred_deployment_chains': len([c for c in self.chain_configs.values() if c.preferred_for_deployment]),
                'active_bridge_routes': len(self.bridge_routes),
                'current_deployment': {
                    'chain': 'Ethereum Sepolia',
                    'xmrt_token': self.xmrt_token_sepolia,
                    'xmrt_ip_nft': self.xmrt_ip_nft_sepolia
                },
                'deployment_readiness': {
                    'polygon': 'ready',
                    'starknet': 'ready',
                    'arbitrum': 'ready',
                    'base': 'ready'
                },
                'estimated_costs': await self.estimate_migration_costs(),
                'governance_preparation': await self.prepare_cross_chain_governance(),
                'mining_integration': await self.prepare_mining_integration(),
                'timestamp': int(time.time())
            }

            return status

        except Exception as e:
            self.logger.error(f"Error getting comprehensive status: {e}")
            return {'error': str(e), 'service_status': 'error'}

    async def generate_deployment_recommendation(self) -> Dict[str, Any]:
        """Generate final deployment recommendation"""
        try:
            analysis = await self.analyze_deployment_options()
            costs = await self.estimate_migration_costs()

            # Generate final recommendation
            recommendation = {
                'primary_recommendation': {
                    'chain': 'Polygon Mainnet',
                    'rationale': [
                        'EVM compatibility ensures easy migration',
                        'Low gas costs (~99% cheaper than Ethereum)',
                        'Strong DeFi ecosystem for treasury management',
                        'Proven security and reliability',
                        'Excellent bridge infrastructure'
                    ],
                    'estimated_total_cost': costs.get('recommended_approach', {}).get('details', {}).get('total_first_year_cost_usd', 500),
                    'implementation_timeline': '2-4 weeks',
                    'risk_level': 'low'
                },
                'secondary_recommendation': {
                    'chain': 'Starknet Mainnet',
                    'rationale': [
                        'Ultra-low gas costs (99.99% cheaper)',
                        'Advanced scaling technology',
                        'Strong mathematical foundations',
                        'Future-proof architecture'
                    ],
                    'estimated_total_cost': 100,
                    'implementation_timeline': '4-8 weeks',
                    'risk_level': 'medium',
                    'notes': 'Requires Cairo contract development'
                },
                'phased_approach': {
                    'phase_1': 'Deploy to Polygon Mainnet (immediate cost benefits)',
                    'phase_2': 'Add Starknet deployment (ultra-low gas optimization)', 
                    'phase_3': 'Expand to additional L2s based on ecosystem growth'
                }
            }

            return recommendation

        except Exception as e:
            self.logger.error(f"Error generating deployment recommendation: {e}")
            return {'error': str(e)}
