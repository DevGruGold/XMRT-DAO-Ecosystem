"""
XMRT Cross-Chain Bridge Service
Enhanced integration with Wormhole and LayerZero protocols for multi-chain operations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from web3 import Web3
import requests

logger = logging.getLogger(__name__)

class ChainId(Enum):
    """Supported blockchain networks"""
    ETHEREUM = 1
    SEPOLIA = 11155111
    POLYGON = 137
    ARBITRUM = 42161
    OPTIMISM = 10
    BASE = 8453
    STARKNET = 0x534e5f4d41494e  # SN_MAIN

@dataclass
class BridgeTransaction:
    """Bridge transaction data structure"""
    source_chain: ChainId
    destination_chain: ChainId
    token_address: str
    amount: int
    recipient: str
    tx_hash: str
    status: str
    timestamp: int
    bridge_fee: int
    wormhole_vaa: Optional[str] = None
    layerzero_message: Optional[str] = None

@dataclass
class ChainConfig:
    """Configuration for each supported chain"""
    chain_id: ChainId
    rpc_url: str
    token_address: str
    bridge_address: str
    wormhole_core: str
    layerzero_endpoint: str
    gas_token: str
    confirmations_required: int

class XMRTCrossChainBridge:
    """
    Enhanced Cross-Chain Bridge Service for XMRT ecosystem
    Supports Wormhole and LayerZero protocols for secure cross-chain transfers
    """

    def __init__(self, config: Dict):
        self.config = config
        self.chain_configs = self._initialize_chain_configs()
        self.active_transactions = {}
        self.supported_routes = self._initialize_bridge_routes()

    def _initialize_chain_configs(self) -> Dict[ChainId, ChainConfig]:
        """Initialize configuration for all supported chains"""
        return {
            ChainId.ETHEREUM: ChainConfig(
                chain_id=ChainId.ETHEREUM,
                rpc_url=self.config.get('ethereum_rpc', ''),
                token_address=self.config.get('ethereum_token', ''),
                bridge_address=self.config.get('ethereum_bridge', ''),
                wormhole_core='0x98f3c9e6E3fAce36bAAd05FE09d375Ef1464288B',
                layerzero_endpoint='0x66A71Dcef29A0fFBDBE3c6a460a3B5BC225Cd675',
                gas_token='ETH',
                confirmations_required=12
            ),
            ChainId.SEPOLIA: ChainConfig(
                chain_id=ChainId.SEPOLIA,
                rpc_url=self.config.get('sepolia_rpc', ''),
                token_address='0x77307DFbc436224d5e6f2048d2b6bDfA66998a15',  # Current XMRT deployment
                bridge_address=self.config.get('sepolia_bridge', ''),
                wormhole_core='0x4a8bc80Ed5a4067f1CCf107057b8270E0cC11A78',
                layerzero_endpoint='0xae92d5aD7583AD66E49A0c67BAd18F6ba52dDDc1',
                gas_token='ETH',
                confirmations_required=3
            ),
            ChainId.POLYGON: ChainConfig(
                chain_id=ChainId.POLYGON,
                rpc_url=self.config.get('polygon_rpc', ''),
                token_address=self.config.get('polygon_token', ''),
                bridge_address=self.config.get('polygon_bridge', ''),
                wormhole_core='0x7A4B5a56256163F07b2C80A7cA55aBE66c4ec4d7',
                layerzero_endpoint='0x3c2269811836af69497E5F486A85D7316753cf62',
                gas_token='MATIC',
                confirmations_required=128
            ),
            ChainId.ARBITRUM: ChainConfig(
                chain_id=ChainId.ARBITRUM,
                rpc_url=self.config.get('arbitrum_rpc', ''),
                token_address=self.config.get('arbitrum_token', ''),
                bridge_address=self.config.get('arbitrum_bridge', ''),
                wormhole_core='0xa5f208e072434bC67592E4C49C1B991BA79BCA46',
                layerzero_endpoint='0x3c2269811836af69497E5F486A85D7316753cf62',
                gas_token='ETH',
                confirmations_required=1
            )
        }

    def _initialize_bridge_routes(self) -> Dict[Tuple[ChainId, ChainId], str]:
        """Initialize supported bridge routes and their protocols"""
        return {
            # Wormhole routes
            (ChainId.ETHEREUM, ChainId.POLYGON): 'wormhole',
            (ChainId.POLYGON, ChainId.ETHEREUM): 'wormhole',
            (ChainId.ETHEREUM, ChainId.ARBITRUM): 'wormhole',
            (ChainId.ARBITRUM, ChainId.ETHEREUM): 'wormhole',

            # LayerZero routes (for smaller amounts, lower fees)
            (ChainId.ETHEREUM, ChainId.POLYGON): 'layerzero',
            (ChainId.POLYGON, ChainId.ARBITRUM): 'layerzero',
            (ChainId.ARBITRUM, ChainId.POLYGON): 'layerzero',

            # Sepolia testnet routes
            (ChainId.SEPOLIA, ChainId.POLYGON): 'layerzero',
            (ChainId.POLYGON, ChainId.SEPOLIA): 'layerzero',
        }

    async def initiate_bridge_transfer(
        self, 
        source_chain: ChainId,
        destination_chain: ChainId,
        amount: int,
        recipient: str,
        sender_private_key: str
    ) -> BridgeTransaction:
        """
        Initiate a cross-chain bridge transfer

        Args:
            source_chain: Source blockchain
            destination_chain: Destination blockchain
            amount: Amount to bridge (in wei/smallest unit)
            recipient: Recipient address on destination chain
            sender_private_key: Private key for transaction signing

        Returns:
            BridgeTransaction object with transaction details
        """
        try:
            # Validate bridge route
            route = (source_chain, destination_chain)
            if route not in self.supported_routes:
                raise ValueError(f"Bridge route {source_chain.name} -> {destination_chain.name} not supported")

            protocol = self.supported_routes[route]
            bridge_fee = await self._calculate_bridge_fee(source_chain, destination_chain, amount)

            # Select appropriate bridge protocol
            if protocol == 'wormhole':
                tx_hash = await self._bridge_via_wormhole(
                    source_chain, destination_chain, amount, recipient, sender_private_key
                )
            elif protocol == 'layerzero':
                tx_hash = await self._bridge_via_layerzero(
                    source_chain, destination_chain, amount, recipient, sender_private_key
                )
            else:
                raise ValueError(f"Unsupported bridge protocol: {protocol}")

            # Create transaction record
            transaction = BridgeTransaction(
                source_chain=source_chain,
                destination_chain=destination_chain,
                token_address=self.chain_configs[source_chain].token_address,
                amount=amount,
                recipient=recipient,
                tx_hash=tx_hash,
                status='pending',
                timestamp=int(asyncio.get_event_loop().time()),
                bridge_fee=bridge_fee
            )

            self.active_transactions[tx_hash] = transaction
            logger.info(f"Bridge transfer initiated: {tx_hash}")

            return transaction

        except Exception as e:
            logger.error(f"Failed to initiate bridge transfer: {e}")
            raise

    async def _bridge_via_wormhole(
        self,
        source_chain: ChainId,
        destination_chain: ChainId,
        amount: int,
        recipient: str,
        sender_private_key: str
    ) -> str:
        """Bridge tokens using Wormhole protocol"""
        source_config = self.chain_configs[source_chain]

        # Connect to source chain
        w3 = Web3(Web3.HTTPProvider(source_config.rpc_url))
        account = w3.eth.account.from_key(sender_private_key)

        # Build Wormhole bridge transaction
        bridge_contract = w3.eth.contract(
            address=source_config.bridge_address,
            abi=self._get_wormhole_bridge_abi()
        )

        # Get destination chain Wormhole ID
        dest_wormhole_id = self._get_wormhole_chain_id(destination_chain)

        # Build transaction
        transaction = bridge_contract.functions.transferTokens(
            source_config.token_address,
            amount,
            dest_wormhole_id,
            recipient,
            0,  # Arbitrary sender sequence
            0   # Consistency level
        ).build_transaction({
            'from': account.address,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address)
        })

        # Sign and send transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, sender_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        return tx_hash.hex()

    async def _bridge_via_layerzero(
        self,
        source_chain: ChainId,
        destination_chain: ChainId,
        amount: int,
        recipient: str,
        sender_private_key: str
    ) -> str:
        """Bridge tokens using LayerZero protocol"""
        source_config = self.chain_configs[source_chain]

        # Connect to source chain
        w3 = Web3(Web3.HTTPProvider(source_config.rpc_url))
        account = w3.eth.account.from_key(sender_private_key)

        # Build LayerZero bridge transaction
        bridge_contract = w3.eth.contract(
            address=source_config.bridge_address,
            abi=self._get_layerzero_bridge_abi()
        )

        # Get destination chain LayerZero ID
        dest_lz_id = self._get_layerzero_chain_id(destination_chain)

        # Build transaction payload
        payload = Web3.keccak(text=f"{recipient}:{amount}")

        # Build transaction
        transaction = bridge_contract.functions.send(
            dest_lz_id,
            recipient,
            amount,
            account.address,  # refund address
            "0x0000000000000000000000000000000000000000",  # zro payment address
            payload
        ).build_transaction({
            'from': account.address,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
            'value': await self._get_layerzero_fee(source_chain, destination_chain, amount)
        })

        # Sign and send transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, sender_private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        return tx_hash.hex()

    async def _calculate_bridge_fee(
        self, 
        source_chain: ChainId, 
        destination_chain: ChainId, 
        amount: int
    ) -> int:
        """Calculate bridge fee for the transfer"""
        # Base fee calculation (simplified)
        base_fee = amount * 30 // 10000  # 0.3% base fee

        # Gas estimation for destination chain
        dest_config = self.chain_configs[destination_chain]
        if dest_config.gas_token == 'MATIC':
            gas_fee = 50000  # Lower gas on Polygon
        elif dest_config.gas_token == 'ETH':
            gas_fee = 200000  # Higher gas on Ethereum L1
        else:
            gas_fee = 100000  # Default gas estimate

        return base_fee + gas_fee

    async def _get_layerzero_fee(
        self, 
        source_chain: ChainId, 
        destination_chain: ChainId, 
        amount: int
    ) -> int:
        """Get LayerZero messaging fee"""
        # Simplified fee calculation
        # In production, this would call LayerZero's estimateFees function
        return 100000000000000  # 0.0001 ETH equivalent

    def _get_wormhole_chain_id(self, chain: ChainId) -> int:
        """Get Wormhole chain ID for blockchain"""
        wormhole_ids = {
            ChainId.ETHEREUM: 2,
            ChainId.SEPOLIA: 10002,
            ChainId.POLYGON: 5,
            ChainId.ARBITRUM: 23
        }
        return wormhole_ids.get(chain, 0)

    def _get_layerzero_chain_id(self, chain: ChainId) -> int:
        """Get LayerZero chain ID for blockchain"""
        layerzero_ids = {
            ChainId.ETHEREUM: 101,
            ChainId.SEPOLIA: 10161,
            ChainId.POLYGON: 109,
            ChainId.ARBITRUM: 110
        }
        return layerzero_ids.get(chain, 0)

    def _get_wormhole_bridge_abi(self) -> List[Dict]:
        """Get Wormhole bridge contract ABI"""
        # Simplified ABI - in production would load full ABI
        return [
            {
                "inputs": [
                    {"name": "token", "type": "address"},
                    {"name": "amount", "type": "uint256"},
                    {"name": "recipientChain", "type": "uint16"},
                    {"name": "recipient", "type": "bytes32"},
                    {"name": "arbiterFee", "type": "uint256"},
                    {"name": "nonce", "type": "uint32"}
                ],
                "name": "transferTokens",
                "outputs": [{"name": "sequence", "type": "uint64"}],
                "type": "function"
            }
        ]

    def _get_layerzero_bridge_abi(self) -> List[Dict]:
        """Get LayerZero bridge contract ABI"""
        # Simplified ABI - in production would load full ABI
        return [
            {
                "inputs": [
                    {"name": "_dstChainId", "type": "uint16"},
                    {"name": "_to", "type": "bytes"},
                    {"name": "_amount", "type": "uint256"},
                    {"name": "_refundAddress", "type": "address"},
                    {"name": "_zroPaymentAddress", "type": "address"},
                    {"name": "_adapterParams", "type": "bytes"}
                ],
                "name": "send",
                "outputs": [],
                "type": "function",
                "payable": True
            }
        ]

    async def get_bridge_status(self, tx_hash: str) -> Optional[BridgeTransaction]:
        """Get status of a bridge transaction"""
        return self.active_transactions.get(tx_hash)

    async def get_supported_chains(self) -> List[ChainId]:
        """Get list of supported blockchain networks"""
        return list(self.chain_configs.keys())

    async def get_bridge_routes(self) -> Dict[str, List[str]]:
        """Get all supported bridge routes"""
        routes = {}
        for (source, dest), protocol in self.supported_routes.items():
            route_key = f"{source.name}_to_{dest.name}"
            routes[route_key] = {
                'protocol': protocol,
                'source_chain': source.name,
                'destination_chain': dest.name
            }
        return routes

    async def health_check(self) -> Dict[str, bool]:
        """Check health status of all bridge components"""
        health_status = {}

        for chain, config in self.chain_configs.items():
            try:
                w3 = Web3(Web3.HTTPProvider(config.rpc_url))
                is_connected = w3.is_connected()
                health_status[f"{chain.name.lower()}_rpc"] = is_connected

                if is_connected:
                    latest_block = w3.eth.block_number
                    health_status[f"{chain.name.lower()}_latest_block"] = latest_block

            except Exception as e:
                logger.error(f"Health check failed for {chain.name}: {e}")
                health_status[f"{chain.name.lower()}_rpc"] = False

        return health_status
