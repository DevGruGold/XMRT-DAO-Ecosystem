"""
Optimized MESHNET Service with Background Health Checks
Non-blocking verification with cached status
"""

import os
import time
import json
import logging
import threading
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import Redis
try:
    from upstash_redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

class OptimizedMESHNETService:
    """MESHNET service with async health checks"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.nodes = {}
        self.node_health = {}
        self.health_check_interval = 30  # seconds
        
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
        
        # Start background health checker
        self.running = True
        self.health_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.health_thread.start()
        
        logger.info(f"MESHNET service initialized (Redis: {self.use_redis})")
    
    def _health_check_loop(self):
        """Background thread for health checks"""
        while self.running:
            try:
                for node_id, node in list(self.nodes.items()):
                    try:
                        # Check node health (non-blocking in background)
                        last_heard = node.get('last_seen', 0)
                        is_online = time.time() - last_heard < 300  # 5 minutes
                        
                        health = {
                            'node_id': node_id,
                            'status': 'online' if is_online else 'offline',
                            'last_checked': time.time(),
                            'last_heard': last_heard,
                            'signal_strength': node.get('signal_strength', -999)
                        }
                        
                        self.node_health[node_id] = health
                        
                        # Publish to Redis
                        if self.use_redis:
                            try:
                                self.redis.setex(
                                    f'meshnet:health:{node_id}',
                                    self.health_check_interval * 2,
                                    json.dumps(health)
                                )
                                
                                # Publish event if status changed
                                if is_online:
                                    self.redis.publish('meshnet:verified', json.dumps({
                                        'node_id': node_id,
                                        'verified': True,
                                        'timestamp': time.time()
                                    }))
                            except Exception as e:
                                logger.error(f"Redis health update failed: {e}")
                        
                    except Exception as e:
                        logger.error(f"Node health check error for {node_id}: {e}")
                        self.node_health[node_id] = {
                            'status': 'error',
                            'last_checked': time.time(),
                            'error': str(e)
                        }
                
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
            
            time.sleep(self.health_check_interval)
    
    def verify_participant(self, wallet_address: str) -> Dict:
        """Instant verification from cache (non-blocking)"""
        # Try Redis first
        if self.use_redis:
            try:
                cached = self.redis.get(f'meshnet:health:{wallet_address}')
                if cached:
                    health = json.loads(cached)
                    return {
                        'verified': health['status'] == 'online',
                        'status': health['status'],
                        'last_checked': health['last_checked'],
                        'source': 'redis_cache'
                    }
            except Exception as e:
                logger.error(f"Redis verification error: {e}")
        
        # Fallback to local cache
        health = self.node_health.get(wallet_address)
        
        if not health:
            return {
                'verified': False,
                'status': 'unknown',
                'reason': 'node_not_found',
                'source': 'local_cache'
            }
        
        return {
            'verified': health['status'] == 'online',
            'status': health['status'],
            'last_checked': health.get('last_checked'),
            'source': 'local_cache'
        }
    
    def get_network_status(self) -> Dict:
        """Get overall network status"""
        total_nodes = len(self.nodes)
        online_nodes = sum(1 for h in self.node_health.values() if h.get('status') == 'online')
        
        return {
            'total_nodes': total_nodes,
            'online_nodes': online_nodes,
            'offline_nodes': total_nodes - online_nodes,
            'health_percentage': (online_nodes / total_nodes * 100) if total_nodes > 0 else 0,
            'last_updated': time.time()
        }
    
    def shutdown(self):
        """Cleanup resources"""
        self.running = False
        if self.health_thread.is_alive():
            self.health_thread.join(timeout=2)
