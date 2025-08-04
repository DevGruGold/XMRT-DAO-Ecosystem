"""
Redis Service for XMRT DAO Ecosystem
Provides memory persistence and caching capabilities for AI agents
"""

import redis
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RedisService:
    """Redis service for memory persistence and caching"""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, 
                 password: Optional[str] = None, decode_responses: bool = True):
        """
        Initialize Redis connection
        
        Args:
            host: Redis server host
            port: Redis server port
            db: Redis database number
            password: Redis password (if required)
            decode_responses: Whether to decode responses to strings
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.decode_responses = decode_responses
        self.redis_client = None
        self.connected = False
        
    def connect(self) -> bool:
        """
        Establish connection to Redis server
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            self.redis_client.ping()
            self.connected = True
            logger.info(f"Successfully connected to Redis at {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            self.redis_client.close()
            self.connected = False
            logger.info("Disconnected from Redis")
    
    def is_connected(self) -> bool:
        """Check if Redis connection is active"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.ping()
            return True
        except:
            self.connected = False
            return False
    
    def set_memory(self, agent_id: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Store agent memory data
        
        Args:
            agent_id: Unique identifier for the agent
            key: Memory key
            value: Memory value (will be JSON serialized)
            ttl: Time to live in seconds (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Redis not connected")
            return False
        
        try:
            memory_key = f"agent:{agent_id}:memory:{key}"
            serialized_value = json.dumps(value, default=str)
            
            if ttl:
                result = self.redis_client.setex(memory_key, ttl, serialized_value)
            else:
                result = self.redis_client.set(memory_key, serialized_value)
                
            logger.debug(f"Stored memory for {agent_id}: {key}")
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to set memory for {agent_id}: {e}")
            return False
    
    def get_memory(self, agent_id: str, key: str) -> Optional[Any]:
        """
        Retrieve agent memory data
        
        Args:
            agent_id: Unique identifier for the agent
            key: Memory key
            
        Returns:
            Any: Deserialized memory value or None if not found
        """
        if not self.is_connected():
            logger.error("Redis not connected")
            return None
        
        try:
            memory_key = f"agent:{agent_id}:memory:{key}"
            value = self.redis_client.get(memory_key)
            
            if value is None:
                return None
                
            return json.loads(value)
            
        except Exception as e:
            logger.error(f"Failed to get memory for {agent_id}: {e}")
            return None
    
    def delete_memory(self, agent_id: str, key: str) -> bool:
        """
        Delete agent memory data
        
        Args:
            agent_id: Unique identifier for the agent
            key: Memory key
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Redis not connected")
            return False
        
        try:
            memory_key = f"agent:{agent_id}:memory:{key}"
            result = self.redis_client.delete(memory_key)
            logger.debug(f"Deleted memory for {agent_id}: {key}")
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to delete memory for {agent_id}: {e}")
            return False
    
    def get_all_memory_keys(self, agent_id: str) -> List[str]:
        """
        Get all memory keys for an agent
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            List[str]: List of memory keys
        """
        if not self.is_connected():
            logger.error("Redis not connected")
            return []
        
        try:
            pattern = f"agent:{agent_id}:memory:*"
            keys = self.redis_client.keys(pattern)
            
            # Extract just the memory key part
            memory_keys = []
            for key in keys:
                if isinstance(key, str):
                    memory_key = key.split(':')[-1]
                    memory_keys.append(memory_key)
                    
            return memory_keys
            
        except Exception as e:
            logger.error(f"Failed to get memory keys for {agent_id}: {e}")
            return []
    
    def cache_set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set cache value with TTL
        
        Args:
            key: Cache key
            value: Cache value (will be JSON serialized)
            ttl: Time to live in seconds (default 1 hour)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Redis not connected")
            return False
        
        try:
            cache_key = f"cache:{key}"
            serialized_value = json.dumps(value, default=str)
            result = self.redis_client.setex(cache_key, ttl, serialized_value)
            logger.debug(f"Cached value for key: {key}")
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to cache value: {e}")
            return False
    
    def cache_get(self, key: str) -> Optional[Any]:
        """
        Get cached value
        
        Args:
            key: Cache key
            
        Returns:
            Any: Deserialized cache value or None if not found
        """
        if not self.is_connected():
            logger.error("Redis not connected")
            return None
        
        try:
            cache_key = f"cache:{key}"
            value = self.redis_client.get(cache_key)
            
            if value is None:
                return None
                
            return json.loads(value)
            
        except Exception as e:
            logger.error(f"Failed to get cached value: {e}")
            return None
    
    def cache_delete(self, key: str) -> bool:
        """
        Delete cached value
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Redis not connected")
            return False
        
        try:
            cache_key = f"cache:{key}"
            result = self.redis_client.delete(cache_key)
            logger.debug(f"Deleted cache for key: {key}")
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to delete cache: {e}")
            return False
    
    def store_agent_state(self, agent_id: str, state: Dict[str, Any]) -> bool:
        """
        Store complete agent state
        
        Args:
            agent_id: Unique identifier for the agent
            state: Agent state dictionary
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Redis not connected")
            return False
        
        try:
            state_key = f"agent:{agent_id}:state"
            state_with_timestamp = {
                **state,
                'last_updated': datetime.now().isoformat()
            }
            serialized_state = json.dumps(state_with_timestamp, default=str)
            result = self.redis_client.set(state_key, serialized_state)
            logger.debug(f"Stored state for agent: {agent_id}")
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to store agent state: {e}")
            return False
    
    def get_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve complete agent state
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            Dict[str, Any]: Agent state dictionary or None if not found
        """
        if not self.is_connected():
            logger.error("Redis not connected")
            return None
        
        try:
            state_key = f"agent:{agent_id}:state"
            value = self.redis_client.get(state_key)
            
            if value is None:
                return None
                
            return json.loads(value)
            
        except Exception as e:
            logger.error(f"Failed to get agent state: {e}")
            return None
    
    def clear_agent_data(self, agent_id: str) -> bool:
        """
        Clear all data for an agent
        
        Args:
            agent_id: Unique identifier for the agent
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Redis not connected")
            return False
        
        try:
            pattern = f"agent:{agent_id}:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                result = self.redis_client.delete(*keys)
                logger.info(f"Cleared {result} keys for agent: {agent_id}")
                return True
            else:
                logger.info(f"No data found for agent: {agent_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to clear agent data: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get Redis statistics
        
        Returns:
            Dict[str, Any]: Redis statistics
        """
        if not self.is_connected():
            return {"connected": False, "error": "Redis not connected"}
        
        try:
            info = self.redis_client.info()
            return {
                "connected": True,
                "used_memory": info.get('used_memory_human', 'Unknown'),
                "connected_clients": info.get('connected_clients', 0),
                "total_commands_processed": info.get('total_commands_processed', 0),
                "keyspace_hits": info.get('keyspace_hits', 0),
                "keyspace_misses": info.get('keyspace_misses', 0),
                "uptime_in_seconds": info.get('uptime_in_seconds', 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get Redis stats: {e}")
            return {"connected": False, "error": str(e)}

