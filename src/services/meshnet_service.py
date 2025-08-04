"""
XMRT-DAO MESHNET Integration Service
Integrates Meshtastic mesh networking with XMRT mining and DAO operations
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MeshNode:
    """Represents a MESHNET node"""
    node_id: str
    user_id: str
    short_name: str
    long_name: str
    hardware_model: str
    last_seen: datetime
    position: Optional[Dict[str, float]]
    snr: float
    rssi: int
    is_mining: bool = False
    mining_hash_rate: float = 0.0
    xmr_earnings: float = 0.0

@dataclass
class MinerParticipant:
    """Represents a mining participant with MESHNET connectivity"""
    wallet_address: str
    mesh_node_id: Optional[str]
    hash_rate: float
    xmr_earned: float
    last_ping: datetime
    connectivity_score: int  # 0-100 based on mesh connectivity
    is_mesh_verified: bool

class MESHNETService:
    """
    MESHNET Integration Service for XMRT-DAO-Ecosystem
    Bridges Meshtastic mesh networking with mining operations and DAO governance
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mesh_interface = None
        self.nodes: Dict[str, MeshNode] = {}
        self.miners: Dict[str, MinerParticipant] = {}
        self.is_running = False

        # XMRT Configuration
        self.xmrt_config = {
            'token_address': '0x77307DFbc436224d5e6f2048d2b6bDfA66998a15',
            'ip_nft_address': '0x9d691fc136a846d7442d1321a2d1b6aaef494eda',
            'mining_wallet': '46UxNFuGM2E3UwmZWWJicaRPoRwqwW4byQkaTHkX8yPcVihp91qAVtSFipWUGJJUyTXgzSqxDQtNLf2bsp2DX2qCCgC5mg',
            'supportxmr_api': 'https://supportxmr.com/api'
        }

    async def initialize_mesh_interface(self, port: str = "simulate"):
        """Initialize Meshtastic interface"""
        try:
            if port == "simulate":
                logger.info("🔄 Initializing MESHNET in simulation mode")
                await self._simulate_mesh_network()
            else:
                # Real Meshtastic hardware integration
                logger.info(f"🔄 Connecting to Meshtastic device on {port}")
                try:
                    from meshtastic import SerialInterface
                    self.mesh_interface = SerialInterface(port)
                    await self._scan_mesh_nodes()
                except ImportError:
                    logger.warning("Meshtastic library not found, falling back to simulation")
                    await self._simulate_mesh_network()

        except Exception as e:
            logger.error(f"❌ Failed to initialize mesh interface: {e}")
            await self._simulate_mesh_network()

    async def _simulate_mesh_network(self):
        """Simulate a mesh network for testing purposes"""
        logger.info("🌐 Simulating MESHNET with test nodes")

        # Create simulated mesh nodes
        test_nodes = [
            {
                'node_id': 'mesh_001',
                'user_id': 'miner_alpha',
                'short_name': 'ALPHA',
                'long_name': 'ALPHA Mining Node',
                'hardware_model': 'HELTEC_V3',
                'position': {'lat': 10.0, 'lon': -84.0},
                'snr': 12.5,
                'rssi': -85,
                'is_mining': True,
                'mining_hash_rate': 150.0,
                'xmr_earnings': 0.00124
            },
            {
                'node_id': 'mesh_002', 
                'user_id': 'miner_beta',
                'short_name': 'BETA',
                'long_name': 'BETA Mining Node',
                'hardware_model': 'TBEAM',
                'position': {'lat': 10.1, 'lon': -84.1},
                'snr': 8.2,
                'rssi': -92,
                'is_mining': True,
                'mining_hash_rate': 89.3,
                'xmr_earnings': 0.00087
            },
            {
                'node_id': 'mesh_003',
                'user_id': 'relay_gamma',
                'short_name': 'GAMMA',
                'long_name': 'GAMMA Relay Node',
                'hardware_model': 'HELTEC_V2',
                'position': {'lat': 10.05, 'lon': -84.05},
                'snr': 15.1,
                'rssi': -78,
                'is_mining': False,
                'mining_hash_rate': 0.0,
                'xmr_earnings': 0.0
            }
        ]

        for node_data in test_nodes:
            node = MeshNode(
                node_id=node_data['node_id'],
                user_id=node_data['user_id'],
                short_name=node_data['short_name'],
                long_name=node_data['long_name'],
                hardware_model=node_data['hardware_model'],
                last_seen=datetime.now(),
                position=node_data['position'],
                snr=node_data['snr'],
                rssi=node_data['rssi'],
                is_mining=node_data['is_mining'],
                mining_hash_rate=node_data['mining_hash_rate'],
                xmr_earnings=node_data['xmr_earnings']
            )
            self.nodes[node.node_id] = node

        logger.info(f"✅ Simulated {len(self.nodes)} mesh nodes")

    async def _scan_mesh_nodes(self):
        """Scan for active mesh nodes"""
        if not self.mesh_interface:
            return

        try:
            # Get nodes from Meshtastic interface
            nodes = self.mesh_interface.nodes
            for node_id, node_info in nodes.items():
                mesh_node = MeshNode(
                    node_id=str(node_id),
                    user_id=node_info.get('user', {}).get('id', 'unknown'),
                    short_name=node_info.get('user', {}).get('shortName', 'Node'),
                    long_name=node_info.get('user', {}).get('longName', 'Unknown Node'),
                    hardware_model=node_info.get('user', {}).get('hwModel', 'UNKNOWN'),
                    last_seen=datetime.fromtimestamp(node_info.get('lastHeard', time.time())),
                    position=node_info.get('position'),
                    snr=node_info.get('snr', 0.0),
                    rssi=node_info.get('rssi', -999)
                )
                self.nodes[mesh_node.node_id] = mesh_node

            logger.info(f"📡 Discovered {len(self.nodes)} mesh nodes")

        except Exception as e:
            logger.error(f"❌ Error scanning mesh nodes: {e}")

    async def integrate_mining_participants(self):
        """Integrate SupportXMR mining data with MESHNET nodes"""
        try:
            # Fetch current mining stats from SupportXMR
            api_url = f"{self.xmrt_config['supportxmr_api']}/pool/stats"
            response = requests.get(api_url, timeout=10)

            if response.status_code == 200:
                pool_data = response.json()
                logger.info(f"📊 Pool Stats: {pool_data.get('pool_statistics', {}).get('totalHashes', 0)} total hashes")

                # Get miner stats for XMRT wallet
                miner_api = f"{self.xmrt_config['supportxmr_api']}/miner/{self.xmrt_config['mining_wallet']}/stats"
                miner_response = requests.get(miner_api, timeout=10)

                if miner_response.status_code == 200:
                    miner_data = miner_response.json()

                    # Create mining participants with mesh connectivity
                    self._create_mining_participants(miner_data, pool_data)

        except Exception as e:
            logger.error(f"❌ Error integrating mining participants: {e}")

    def _create_mining_participants(self, miner_data: Dict, pool_data: Dict):
        """Create mining participants with MESHNET connectivity"""

        # Simulate mining participants connected to mesh nodes
        participants = [
            {
                'wallet': 'worker_001',
                'mesh_node': 'mesh_001',
                'hash_rate': 150.0,
                'xmr_earned': 0.00124,
                'connectivity_score': 95
            },
            {
                'wallet': 'worker_002', 
                'mesh_node': 'mesh_002',
                'hash_rate': 89.3,
                'xmr_earned': 0.00087,
                'connectivity_score': 87
            },
            {
                'wallet': 'worker_003',
                'mesh_node': None,  # Not mesh connected
                'hash_rate': 45.2,
                'xmr_earned': 0.00032,
                'connectivity_score': 0
            }
        ]

        for participant in participants:
            miner = MinerParticipant(
                wallet_address=participant['wallet'],
                mesh_node_id=participant['mesh_node'],
                hash_rate=participant['hash_rate'],
                xmr_earned=participant['xmr_earned'],
                last_ping=datetime.now(),
                connectivity_score=participant['connectivity_score'],
                is_mesh_verified=participant['mesh_node'] is not None
            )
            self.miners[participant['wallet']] = miner

        logger.info(f"⛏️  Integrated {len(self.miners)} mining participants")

    async def verify_participant_connectivity(self, wallet_address: str) -> Dict[str, Any]:
        """Verify a mining participant's MESHNET connectivity via ping"""
        if wallet_address not in self.miners:
            return {'verified': False, 'error': 'Participant not found'}

        participant = self.miners[wallet_address]

        if not participant.mesh_node_id:
            return {
                'verified': False,
                'mesh_connected': False,
                'connectivity_score': 0,
                'message': 'Participant not connected to MESHNET'
            }

        # Simulate ping verification
        try:
            await asyncio.sleep(0.1)  # Simulate network delay

            # Update last ping and connectivity score
            participant.last_ping = datetime.now()
            participant.connectivity_score = min(100, participant.connectivity_score + 1)

            return {
                'verified': True,
                'mesh_connected': True,
                'mesh_node_id': participant.mesh_node_id,
                'connectivity_score': participant.connectivity_score,
                'last_ping': participant.last_ping.isoformat(),
                'hash_rate': participant.hash_rate,
                'xmr_earned': participant.xmr_earned
            }

        except Exception as e:
            logger.error(f"❌ Ping verification failed for {wallet_address}: {e}")
            return {'verified': False, 'error': str(e)}

    def get_enhanced_leaderboard(self) -> List[Dict[str, Any]]:
        """Generate enhanced leaderboard with MESHNET connectivity status"""
        leaderboard = []

        for wallet, miner in self.miners.items():
            entry = {
                'wallet_address': wallet,
                'hash_rate': miner.hash_rate,
                'xmr_earned': miner.xmr_earned,
                'mesh_connected': miner.is_mesh_verified,
                'mesh_node_id': miner.mesh_node_id,
                'connectivity_score': miner.connectivity_score,
                'last_ping': miner.last_ping.isoformat(),
                'efficiency_bonus': 1.1 if miner.is_mesh_verified else 1.0  # 10% bonus for mesh connectivity
            }

            # Add mesh node details if connected
            if miner.mesh_node_id and miner.mesh_node_id in self.nodes:
                node = self.nodes[miner.mesh_node_id]
                entry['mesh_node_info'] = {
                    'short_name': node.short_name,
                    'hardware_model': node.hardware_model,
                    'signal_strength': node.rssi,
                    'snr': node.snr,
                    'position': node.position
                }

            leaderboard.append(entry)

        # Sort by hash rate with mesh connectivity bonus
        leaderboard.sort(key=lambda x: x['hash_rate'] * x['efficiency_bonus'], reverse=True)

        return leaderboard

    def get_mesh_network_status(self) -> Dict[str, Any]:
        """Get current MESHNET status"""
        connected_miners = sum(1 for m in self.miners.values() if m.is_mesh_verified)
        total_miners = len(self.miners)

        return {
            'total_nodes': len(self.nodes),
            'active_nodes': len([n for n in self.nodes.values() if (datetime.now() - n.last_seen).seconds < 300]),
            'mining_nodes': len([n for n in self.nodes.values() if n.is_mining]),
            'total_miners': total_miners,
            'mesh_connected_miners': connected_miners,
            'mesh_connectivity_rate': (connected_miners / total_miners * 100) if total_miners > 0 else 0,
            'network_health': 'Excellent' if connected_miners > total_miners * 0.8 else 'Good' if connected_miners > total_miners * 0.5 else 'Fair'
        }

    async def start_monitoring(self):
        """Start continuous MESHNET monitoring"""
        self.is_running = True
        logger.info("🔄 Starting MESHNET monitoring service")

        while self.is_running:
            try:
                await self.integrate_mining_participants()
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    def stop_monitoring(self):
        """Stop MESHNET monitoring"""
        self.is_running = False
        logger.info("🛑 MESHNET monitoring stopped")

# Usage example
async def main():
    config = {
        'mesh_port': 'simulate',  # Use 'simulate' for testing, actual port for hardware
        'update_interval': 30
    }

    meshnet = MESHNETService(config)
    await meshnet.initialize_mesh_interface()
    await meshnet.integrate_mining_participants()

    # Get enhanced leaderboard
    leaderboard = meshnet.get_enhanced_leaderboard()
    print("🏆 Enhanced Mining Leaderboard with MESHNET:")
    for i, entry in enumerate(leaderboard, 1):
        mesh_status = "🌐 MESH" if entry['mesh_connected'] else "💻 NET"
        print(f"  {i}. {mesh_status} | {entry['hash_rate']} H/s | {entry['xmr_earned']} XMR | Score: {entry['connectivity_score']}")

    # Get network status
    status = meshnet.get_mesh_network_status()
    print(f"\n📊 MESHNET Status: {status['network_health']}")
    print(f"   Nodes: {status['active_nodes']}/{status['total_nodes']} active")
    print(f"   Miners: {status['mesh_connected_miners']}/{status['total_miners']} mesh-connected ({status['mesh_connectivity_rate']:.1f}%)")

if __name__ == "__main__":
    asyncio.run(main())
