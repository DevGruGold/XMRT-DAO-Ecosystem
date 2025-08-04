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
- Participation verification via ping
- Treasury integration (85% allocation)
- Future MESHNET/Meshtastic connectivity
"""

import logging
import asyncio
import aiohttp
import requests
import json
import time
import ping3
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta

class EnhancedSupportXMRService:
    """Enhanced SupportXMR Mining Pool Integration Service"""

    def __init__(self, config: Dict[str, Any], redis_service=None):
        """Initialize Enhanced SupportXMR Service"""
        self.config = config
        self.redis_service = redis_service
        self.logger = logging.getLogger(__name__)

        # SupportXMR API configuration based on actual testing
        self.api_base_url = "https://supportxmr.com/api"
        self.pool_stats_url = f"{self.api_base_url}/pool/stats"
        self.miner_stats_url = f"{self.api_base_url}/miner"

        # XMRT mining wallet (from screenshot and testing)
        self.mining_wallet = "46UxNFuGM2E3UwmZWWJicaRPoRwqwW4byQkaTHkX8yPcVihp91qAVtSFipWUGJJUyTXgzSqxzDQtNLf2bsp2DX2qCCgC5mg"

        # Treasury allocation based on XMRT ecosystem specs
        self.treasury_allocation = 0.85  # 85% to treasury
        self.operational_allocation = 0.15  # 15% for operations

        # XMR atomic units conversion (1 XMR = 1e12 atomic units)
        self.atomic_units_per_xmr = 1e12

        # Cache settings
        self.cache_ttl = config.get('cache_ttl', 120)  # 2 minutes

        # Monitoring thresholds
        self.min_hashrate_threshold = config.get('min_hashrate', 1000)  # 1 KH/s
        self.offline_threshold_minutes = config.get('offline_threshold', 30)

        self.logger.info("Enhanced SupportXMR Service initialized")
        self.logger.info(f"Mining wallet: {self.mining_wallet}")

    async def get_pool_statistics(self) -> Dict[str, Any]:
        """Get comprehensive pool statistics from SupportXMR"""
        try:
            # Check Redis cache first
            cache_key = "supportxmr:pool_stats"
            if self.redis_service:
                cached_data = await self.redis_service.get_cached_data(cache_key)
                if cached_data:
                    self.logger.debug("Returning cached pool statistics")
                    return cached_data

            # Fetch fresh data from API
            response = requests.get(self.pool_stats_url, timeout=10)
            response.raise_for_status()

            raw_data = response.json()
            pool_stats = raw_data.get('pool_statistics', {})

            # Enhanced pool statistics with calculations
            enhanced_stats = {
                'pool_hashrate': pool_stats.get('hashRate', 0),  # H/s
                'pool_hashrate_mhs': round(pool_stats.get('hashRate', 0) / 1e6, 2),  # MH/s
                'total_miners': pool_stats.get('miners', 0),
                'total_hashes': pool_stats.get('totalHashes', 0),
                'total_blocks_found': pool_stats.get('totalBlocksFound', 0),
                'last_block_found_time': pool_stats.get('lastBlockFoundTime', 0),
                'last_block_found_timestamp': datetime.fromtimestamp(
                    pool_stats.get('lastBlockFoundTime', 0)
                ).isoformat() if pool_stats.get('lastBlockFoundTime') else None,
                'total_miners_paid': pool_stats.get('totalMinersPaid', 0),
                'total_payments': pool_stats.get('totalPayments', 0),
                'round_hashes': pool_stats.get('roundHashes', 0),
                'api_timestamp': datetime.now().isoformat(),
                'data_source': 'SupportXMR Live API'
            }

            # Calculate pool efficiency metrics
            if pool_stats.get('totalHashes', 0) > 0:
                enhanced_stats['blocks_per_hash_efficiency'] = (
                    pool_stats.get('totalBlocksFound', 0) / pool_stats.get('totalHashes', 1)
                )

            # Cache the results
            if self.redis_service:
                await self.redis_service.cache_data(cache_key, enhanced_stats, self.cache_ttl)

            self.logger.info(f"Pool stats retrieved: {enhanced_stats['pool_hashrate_mhs']} MH/s, {enhanced_stats['total_miners']} miners")
            return enhanced_stats

        except Exception as e:
            self.logger.error(f"Error fetching pool statistics: {e}")
            return {
                'error': str(e),
                'pool_hashrate': 0,
                'total_miners': 0,
                'status': 'error',
                'api_timestamp': datetime.now().isoformat()
            }

    async def get_xmrt_miner_statistics(self) -> Dict[str, Any]:
        """Get XMRT mining wallet statistics from SupportXMR"""
        try:
            # Check Redis cache first
            cache_key = f"supportxmr:miner:{self.mining_wallet}"
            if self.redis_service:
                cached_data = await self.redis_service.get_cached_data(cache_key)
                if cached_data:
                    self.logger.debug("Returning cached XMRT miner statistics")
                    return cached_data

            # Fetch fresh data from API
            miner_url = f"{self.miner_stats_url}/{self.mining_wallet}/stats"
            response = requests.get(miner_url, timeout=10)
            response.raise_for_status()

            raw_data = response.json()

            # Convert atomic units to XMR
            amt_due_xmr = raw_data.get('amtDue', 0) / self.atomic_units_per_xmr
            amt_paid_xmr = raw_data.get('amtPaid', 0) / self.atomic_units_per_xmr

            # Enhanced miner statistics
            enhanced_stats = {
                'wallet_address': self.mining_wallet,
                'current_hashrate': raw_data.get('hash', 0),  # Current hashrate
                'total_hashes': raw_data.get('totalHashes', 0),
                'valid_shares': raw_data.get('validShares', 0),
                'invalid_shares': raw_data.get('invalidShares', 0),
                'last_hash_timestamp': raw_data.get('lastHash', 0),
                'last_hash_datetime': datetime.fromtimestamp(
                    raw_data.get('lastHash', 0)
                ).isoformat() if raw_data.get('lastHash') else None,
                'amount_due_atomic': raw_data.get('amtDue', 0),
                'amount_due_xmr': round(amt_due_xmr, 8),
                'amount_paid_atomic': raw_data.get('amtPaid', 0),
                'amount_paid_xmr': round(amt_paid_xmr, 8),
                'transaction_count': raw_data.get('txnCount', 0),
                'expiry_timestamp': raw_data.get('expiry', 0),
                'api_timestamp': datetime.now().isoformat(),
                'data_source': 'SupportXMR Live API',

                # Treasury allocation calculations
                'treasury_allocation_xmr': round(amt_due_xmr * self.treasury_allocation, 8),
                'operational_allocation_xmr': round(amt_due_xmr * self.operational_allocation, 8),
            }

            # Calculate mining efficiency
            if enhanced_stats['total_hashes'] > 0:
                enhanced_stats['shares_per_hash_ratio'] = (
                    enhanced_stats['valid_shares'] / enhanced_stats['total_hashes']
                )

            # Determine mining status
            last_hash_time = raw_data.get('lastHash', 0)
            current_time = time.time()
            minutes_since_last_hash = (current_time - last_hash_time) / 60

            if minutes_since_last_hash <= self.offline_threshold_minutes:
                enhanced_stats['mining_status'] = 'active'
            else:
                enhanced_stats['mining_status'] = 'offline'

            enhanced_stats['minutes_since_last_hash'] = round(minutes_since_last_hash, 1)

            # Cache the results
            if self.redis_service:
                await self.redis_service.cache_data(cache_key, enhanced_stats, self.cache_ttl)

            self.logger.info(f"XMRT miner stats: {enhanced_stats['amount_due_xmr']} XMR due, status: {enhanced_stats['mining_status']}")
            return enhanced_stats

        except Exception as e:
            self.logger.error(f"Error fetching XMRT miner statistics: {e}")
            return {
                'error': str(e),
                'wallet_address': self.mining_wallet,
                'amount_due_xmr': 0,
                'mining_status': 'error',
                'api_timestamp': datetime.now().isoformat()
            }

    async def get_comprehensive_mining_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive mining dashboard data"""
        try:
            # Fetch both pool and miner statistics
            pool_stats_task = self.get_pool_statistics()
            miner_stats_task = self.get_xmrt_miner_statistics()

            pool_stats, miner_stats = await asyncio.gather(pool_stats_task, miner_stats_task)

            # Combine into comprehensive dashboard
            dashboard = {
                'dashboard_timestamp': datetime.now().isoformat(),
                'xmrt_contracts': {
                    'token_address': '0x77307DFbc436224d5e6f2048d2b6bDfA66998a15',
                    'ip_nft_address': '0x9d691fc136a846d7442d1321a2d1b6aaef494eda',
                    'creator_wallet': '0xaE2402dFdD313B8c40AF06d3292B50dE1eD75F68'
                },
                'pool_statistics': pool_stats,
                'xmrt_miner_statistics': miner_stats,
                'treasury_projections': {
                    'current_xmr_due': miner_stats.get('amount_due_xmr', 0),
                    'treasury_allocation_xmr': miner_stats.get('treasury_allocation_xmr', 0),
                    'operational_allocation_xmr': miner_stats.get('operational_allocation_xmr', 0),
                    'allocation_percentage_treasury': self.treasury_allocation * 100,
                    'allocation_percentage_operational': self.operational_allocation * 100
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
            return {
                'error': str(e),
                'dashboard_timestamp': datetime.now().isoformat(),
                'status': 'error'
            }

    async def ping_mining_infrastructure(self) -> Dict[str, Any]:
        """Ping mining infrastructure for connectivity verification"""
        try:
            results = {}

            # Ping SupportXMR pool
            supportxmr_ping = ping3.ping('supportxmr.com', timeout=5)
            results['supportxmr_ping'] = {
                'hostname': 'supportxmr.com',
                'response_time_ms': round(supportxmr_ping * 1000, 2) if supportxmr_ping else None,
                'status': 'online' if supportxmr_ping else 'offline',
                'timestamp': datetime.now().isoformat()
            }

            # Test API accessibility
            try:
                api_response = requests.get(self.pool_stats_url, timeout=5)
                results['api_accessibility'] = {
                    'status_code': api_response.status_code,
                    'response_time_ms': round(api_response.elapsed.total_seconds() * 1000, 2),
                    'status': 'accessible' if api_response.status_code == 200 else 'error',
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                results['api_accessibility'] = {
                    'error': str(e),
                    'status': 'inaccessible',
                    'timestamp': datetime.now().isoformat()
                }

            return results

        except Exception as e:
            self.logger.error(f"Error pinging mining infrastructure: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    # Future MESHNET Integration Placeholder
    async def prepare_meshnet_integration(self) -> Dict[str, Any]:
        """Prepare for future MESHNET/Meshtastic integration"""
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
