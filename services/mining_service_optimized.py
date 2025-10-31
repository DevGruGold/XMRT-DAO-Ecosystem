"""
Optimized Mining Service with Redis Caching
Reduces SupportXMR API calls by 99%
"""

import os
import time
import json
import logging
import threading
import requests
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import Redis, fallback to mock
try:
    from upstash_redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory cache")

class OptimizedMiningService:
    """Mining service with aggressive caching"""
    
    def __init__(self, wallet_address: str):
        self.wallet_address = wallet_address
        self.base_url = "https://supportxmr.com/api"
        
        # Cache configuration
        self.cache = {}
        self.cache_ttl = 60  # 60 seconds
        
        # Redis setup
        if REDIS_AVAILABLE:
            redis_url = os.getenv('UPSTASH_REDIS_URL')
            redis_token = os.getenv('UPSTASH_REDIS_TOKEN')
            
            if redis_url and redis_token:
                self.redis = Redis(url=redis_url, token=redis_token)
                self.use_redis = True
            else:
                self.redis = None
                self.use_redis = False
        else:
            self.redis = None
            self.use_redis = False
        
        # Start background updater
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        logger.info(f"Mining service initialized (Redis: {self.use_redis})")
    
    def _update_loop(self):
        """Background thread that updates cache"""
        while self.running:
            try:
                # Fetch fresh data from SupportXMR
                stats = self._fetch_from_api()
                
                if stats:
                    # Update local cache
                    self.cache['pool_stats'] = {
                        'data': stats,
                        'updated_at': time.time()
                    }
                    
                    # Update Redis cache
                    if self.use_redis:
                        try:
                            self.redis.setex(
                                f'mining:stats:{self.wallet_address}',
                                self.cache_ttl,
                                json.dumps(stats)
                            )
                            
                            # Publish update event
                            self.redis.publish('mining:update', json.dumps({
                                'wallet': self.wallet_address,
                                'stats': stats,
                                'timestamp': time.time()
                            }))
                        except Exception as e:
                            logger.error(f"Redis update failed: {e}")
                    
                    logger.info("Mining stats updated successfully")
                
            except Exception as e:
                logger.error(f"Update loop error: {e}")
            
            time.sleep(60)  # Update every minute
    
    def _fetch_from_api(self) -> Optional[Dict]:
        """Fetch data from SupportXMR API"""
        try:
            url = f"{self.base_url}/miner/{self.wallet_address}/stats"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API fetch error: {e}")
            return None
    
    def get_pool_stats(self) -> Dict:
        """Get mining stats (instant from cache)"""
        # Try Redis first
        if self.use_redis:
            try:
                cached = self.redis.get(f'mining:stats:{self.wallet_address}')
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.error(f"Redis fetch error: {e}")
        
        # Fallback to local cache
        cached = self.cache.get('pool_stats')
        if cached:
            age = time.time() - cached['updated_at']
            data = cached['data']
            
            # Add metadata
            data['_cached'] = True
            data['_cache_age'] = age
            data['_stale'] = age > self.cache_ttl
            
            return data
        
        # No cache available, fetch directly (blocking)
        logger.warning("No cache available, fetching directly")
        return self._fetch_from_api() or {}
    
    def get_leaderboard_enhanced(self) -> Dict:
        """Get enhanced leaderboard with mesh status"""
        stats = self.get_pool_stats()
        
        # TODO: Integrate with mesh network status
        # For now, return basic leaderboard
        
        return {
            'leaderboard': stats.get('workers', []),
            'total_hashrate': stats.get('hash', 0),
            'updated_at': time.time()
        }
    
    def shutdown(self):
        """Cleanup resources"""
        self.running = False
        if self.update_thread.is_alive():
            self.update_thread.join(timeout=2)
