"""
XMRT DAO Ecosystem - Enhanced SupportXMR Mining Integration Service

This service provides comprehensive integration with SupportXMR.com mining pool:

Real API Data Structure:
- Pool Stats: hashRate, miners, totalHashes, lastBlockFoundTime, totalBlocksFound, etc.
- Miner Stats: totalHashes, validShares, amtDue, amtPaid, etc.
- Real-time mining data from XMRT wallet: 46UxNFuGM2E3UwmZWWJicaRPoRwqwW4byQkaTHkX8yPcVihp91qAVtSFipWUGJJUyTXgzSqxDQtNLf2bsp2DX2qCCgC5mg

Features:
- Live mining statistics dashboard
- Worker leaderboard system  
- Participation verification via platform-compatible ping
- Treasury integration (85% allocation)
- Future MESHNET/Meshtastic connectivity
"""

import logging
import asyncio
import aiohttp
import time
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime

class EnhancedSupportXMRService:
    """
    Enhanced SupportXMR Mining Pool Integration Service.
    Refactored to use fully asynchronous network I/O for better performance
    and a platform-compatible ping method.
    """

    def __init__(self, config: Dict[str, Any], redis_service=None):
        """Initialize Enhanced SupportXMR Service"""
        self.config = config
        self.redis_service = redis_service
        self.logger = logging.getLogger(__name__)

        # SupportXMR API configuration
        self.api_base_url = "https://supportxmr.com/api"
        self.pool_stats_url = f"{self.api_base_url}/pool/stats"
        self.miner_stats_url = f"{self.api_base_url}/miner"

        # XMRT mining wallet
        self.mining_wallet = "46UxNFuGM2E3UwmZWWJicaRPoRwqwW4byQkaTHkX8yPcVihp91qAVtSFipWUGJJUyTXgzSqxDQtNLf2bsp2DX2qCCgC5mg"

        # Treasury allocation
        self.treasury_allocation = Decimal('0.85')
        self.operational_allocation = Decimal('0.15')

        # XMR atomic units conversion
        self.atomic_units_per_xmr = Decimal('1e12')

        # Cache settings
        self.cache_ttl = config.get('cache_ttl', 120)  # 2 minutes

        # Monitoring thresholds
        self.min_hashrate_threshold = config.get('min_hashrate', 1000)
        self.offline_threshold_minutes = config.get('offline_threshold', 30)

        self.logger.info("Enhanced SupportXMR Service initialized")
        self.logger.info(f"Mining wallet: {self.mining_wallet}")

    async def get_pool_statistics(self) -> Dict[str, Any]:
        """Get comprehensive pool statistics from SupportXMR using aiohttp."""
        cache_key = "supportxmr:pool_stats"
        if self.redis_service:
            cached_data = await self.redis_service.get_cached_data(cache_key)
            if cached_data:
                self.logger.debug("Returning cached pool statistics")
                return cached_data

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.pool_stats_url, timeout=10) as response:
                    response.raise_for_status()
                    raw_data = await response.json()
            
            pool_stats = raw_data.get('pool_statistics', {})

            enhanced_stats = {
                'pool_hashrate': pool_stats.get('hashRate', 0),
                'pool_hashrate_mhs': round(pool_stats.get('hashRate', 0) / 1e6, 2),
                'total_miners': pool_stats.get('miners', 0),
                'total_hashes': pool_stats.get('totalHashes', 0),
                'total_blocks_found': pool_stats.get('totalBlocksFound', 0),
                'last_block_found_time': pool_stats.get('lastBlockFoundTime', 0),
                'last_block_found_timestamp': datetime.fromtimestamp(pool_stats.get('lastBlockFoundTime', 0)).isoformat() if pool_stats.get('lastBlockFoundTime') else None,
                'total_miners_paid': pool_stats.get('totalMinersPaid', 0),
                'total_payments': pool_stats.get('totalPayments', 0),
                'round_hashes': pool_stats.get('roundHashes', 0),
                'api_timestamp': datetime.now().isoformat(),
                'data_source': 'SupportXMR Live API'
            }

            if self.redis_service:
                await self.redis_service.cache_data(cache_key, enhanced_stats, self.cache_ttl)

            self.logger.info(f"Pool stats retrieved: {enhanced_stats['pool_hashrate_mhs']} MH/s, {enhanced_stats['total_miners']} miners")
            return enhanced_stats

        except Exception as e:
            self.logger.error(f"Error fetching pool statistics: {e}")
            return {'error': str(e), 'status': 'error', 'api_timestamp': datetime.now().isoformat()}

    async def get_xmrt_miner_statistics(self) -> Dict[str, Any]:
        """Get XMRT mining wallet statistics from SupportXMR using aiohttp."""
        cache_key = f"supportxmr:miner:{self.mining_wallet}"
        if self.redis_service:
            cached_data = await self.redis_service.get_cached_data(cache_key)
            if cached_data:
                self.logger.debug("Returning cached XMRT miner statistics")
                return cached_data

        try:
            miner_url = f"{self.miner_stats_url}/{self.mining_wallet}/stats"
            async with aiohttp.ClientSession() as session:
                async with session.get(miner_url, timeout=10) as response:
                    response.raise_for_status()
                    raw_data = await response.json()

            amt_due_xmr = Decimal(raw_data.get('amtDue', 0)) / self.atomic_units_per_xmr
            amt_paid_xmr = Decimal(raw_data.get('amtPaid', 0)) / self.atomic_units_per_xmr

            enhanced_stats = {
                'wallet_address': self.mining_wallet,
                'current_hashrate': raw_data.get('hash', 0),
                'total_hashes': raw_data.get('totalHashes', 0),
                'valid_shares': raw_data.get('validShares', 0),
                'invalid_shares': raw_data.get('invalidShares', 0),
                'last_hash_timestamp': raw_data.get('lastHash', 0),
                'last_hash_datetime': datetime.fromtimestamp(raw_data.get('lastHash', 0)).isoformat() if raw_data.get('lastHash') else None,
                'amount_due_atomic': raw_data.get('amtDue', 0),
                'amount_due_xmr': float(round(amt_due_xmr, 8)),
                'amount_paid_atomic': raw_data.get('amtPaid', 0),
                'amount_paid_xmr': float(round(amt_paid_xmr, 8)),
                'transaction_count': raw_data.get('txnCount', 0),
                'api_timestamp': datetime.now().isoformat(),
                'data_source': 'SupportXMR Live API',
                'treasury_allocation_xmr': float(round(amt_due_xmr * self.treasury_allocation, 8)),
                'operational_allocation_xmr': float(round(amt_due_xmr * self.operational_allocation, 8)),
            }

            last_hash_time = raw_data.get('lastHash', 0)
            minutes_since_last_hash = (time.time() - last_hash_time) / 60
            enhanced_stats['mining_status'] = 'active' if minutes_since_last_hash <= self.offline_threshold_minutes else 'offline'
            enhanced_stats['minutes_since_last_hash'] = round(minutes_since_last_hash, 1)

            if self.redis_service:
                await self.redis_service.cache_data(cache_key, enhanced_stats, self.cache_ttl)

            self.logger.info(f"XMRT miner stats: {enhanced_stats['amount_due_xmr']} XMR due, status: {enhanced_stats['mining_status']}")
            return enhanced_stats

        except Exception as e:
            self.logger.error(f"Error fetching XMRT miner statistics: {e}")
            return {'error': str(e), 'wallet_address': self.mining_wallet, 'mining_status': 'error', 'api_timestamp': datetime.now().isoformat()}

    async def get_comprehensive_mining_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive mining dashboard data by running API calls concurrently."""
        try:
            pool_stats, miner_stats = await asyncio.gather(
                self.get_pool_statistics(),
                self.get_xmrt_miner_statistics()
            )

            dashboard = {
                'dashboard_timestamp': datetime.now().isoformat(),
                'pool_statistics': pool_stats,
                'xmrt_miner_statistics': miner_stats,
                'treasury_projections': {
                    'current_xmr_due': miner_stats.get('amount_due_xmr', 0),
                    'treasury_allocation_xmr': miner_stats.get('treasury_allocation_xmr', 0),
                    'operational_allocation_xmr': miner_stats.get('operational_allocation_xmr', 0),
                },
                'ecosystem_health': {
                    'mining_active': miner_stats.get('mining_status') == 'active',
                    'pool_healthy': pool_stats.get('total_miners', 0) > 1000,
                    'revenue_generating': miner_stats.get('amount_due_xmr', 0) > 0,
                    'api_accessible': not pool_stats.get('error') and not miner_stats.get('error')
                }
            }
            return dashboard

        except Exception as e:
            self.logger.error(f"Error creating comprehensive dashboard: {e}")
            return {'error': str(e), 'status': 'error'}

    async def _ping_host_subprocess(self, host: str, timeout: int = 4) -> Tuple[Optional[float], str]:
        """
        Pings a host using the system's ping command via a non-blocking subprocess.
        This method is compatible with restricted environments like Render.
        """
        command = ['ping', '-c', '1', '-W', str(timeout), host]
        start_time = time.monotonic()
        try:
            proc = await asyncio.create_subprocess_exec(
                *command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            await proc.wait()
            duration_ms = (time.monotonic() - start_time) * 1000

            if proc.returncode == 0:
                return round(duration_ms, 2), 'online'
            else:
                return None, 'offline'
        except FileNotFoundError:
            self.logger.error("The 'ping' command was not found. This feature is unavailable.")
            return None, 'error_command_not_found'
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while pinging {host}: {e}")
            return None, 'error_exception'

    async def ping_mining_infrastructure(self) -> Dict[str, Any]:
        """Ping mining infrastructure for connectivity verification."""
        results = {}
        now_iso = datetime.now().isoformat()

        # Ping SupportXMR pool using subprocess
        ping_time, ping_status = await self._ping_host_subprocess('supportxmr.com')
        results['supportxmr_ping'] = {
            'hostname': 'supportxmr.com',
            'response_time_ms': ping_time,
            'status': ping_status,
            'timestamp': now_iso
        }

        # Test API accessibility using aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                start_time = time.monotonic()
                async with session.get(self.pool_stats_url, timeout=5) as response:
                    duration_ms = (time.monotonic() - start_time) * 1000
                    results['api_accessibility'] = {
                        'status_code': response.status,
                        'response_time_ms': round(duration_ms, 2),
                        'status': 'accessible' if response.status == 200 else 'error',
                        'timestamp': now_iso
                    }
        except Exception as e:
            self.logger.error(f"Error checking API accessibility: {e}")
            results['api_accessibility'] = {
                'error': str(e),
                'status': 'inaccessible',
                'timestamp': now_iso
            }

        return results

    async def prepare_meshnet_integration(self) -> Dict[str, Any]:
        """Prepare for future MESHNET/Meshtastic integration."""
        return {
            'meshnet_status': 'planned',
            'integration_phase': 'future',
            'meshtastic_compatibility': 'pending',
            'mesh_mining_features': [
                'decentralized_mining_coordination',
                'offline_mining_verification', 
                'mesh_network_hashrate_aggregation',
                'distributed_worker_communication'
            ],
            'implementation_timeline': 'Phase 3+',
            'timestamp': datetime.now().isoformat()
        }

