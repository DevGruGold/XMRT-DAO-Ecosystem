"""
XMRT-DAO Memory Service
Provides persistent memory and context management for Eliza
"""

import asyncio
import logging
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Represents a memory entry"""
    id: str
    content: str
    context: str
    importance: int  # 1-10 scale
    timestamp: datetime
    tags: List[str]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class MemoryService:
    """
    Memory service for Eliza agent providing persistent memory and context
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.memory_file = self.config.get('memory_file', 'data/eliza_memory.json')
        self.max_memories = self.config.get('max_memories', 10000)
        self.memory_retention_days = self.config.get('retention_days', 30)
        
        # In-memory storage
        self.memories: Dict[str, MemoryEntry] = {}
        self.conversation_context: List[Dict[str, Any]] = []
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        
        # Initialize memory storage
        self._init_memory_storage()
        self._load_memories()
        
    def _init_memory_storage(self):
        """Initialize memory storage directory"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            logger.info("✅ Memory storage initialized")
        except Exception as e:
            logger.error(f"Failed to initialize memory storage: {e}")
    
    def _load_memories(self):
        """Load memories from persistent storage"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    
                # Load memories
                for memory_data in data.get('memories', []):
                    memory = MemoryEntry.from_dict(memory_data)
                    self.memories[memory.id] = memory
                
                # Load user profiles
                self.user_profiles = data.get('user_profiles', {})
                
                logger.info(f"Loaded {len(self.memories)} memories from storage")
            else:
                logger.info("No existing memory file found, starting fresh")
                
        except Exception as e:
            logger.error(f"Failed to load memories: {e}")
    
    def _save_memories(self):
        """Save memories to persistent storage"""
        try:
            data = {
                'memories': [memory.to_dict() for memory in self.memories.values()],
                'user_profiles': self.user_profiles,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.memory_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug("Memories saved to storage")
            
        except Exception as e:
            logger.error(f"Failed to save memories: {e}")
    
    def _generate_memory_id(self, content: str, context: str) -> str:
        """Generate unique ID for memory entry"""
        combined = f"{content}_{context}_{datetime.now().isoformat()}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    async def store_memory(self, content: str, context: str, importance: int = 5, 
                          tags: List[str] = None, user_id: str = None, 
                          session_id: str = None) -> str:
        """
        Store a new memory
        
        Args:
            content: Memory content
            context: Context of the memory
            importance: Importance level (1-10)
            tags: Associated tags
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Memory ID
        """
        try:
            memory_id = self._generate_memory_id(content, context)
            
            memory = MemoryEntry(
                id=memory_id,
                content=content,
                context=context,
                importance=max(1, min(10, importance)),
                timestamp=datetime.now(),
                tags=tags or [],
                user_id=user_id,
                session_id=session_id
            )
            
            self.memories[memory_id] = memory
            
            # Clean old memories if needed
            await self._cleanup_old_memories()
            
            # Save to persistent storage
            self._save_memories()
            
            logger.info(f"Stored memory: {memory_id} - '{content[:50]}...'")
            return memory_id
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return ""
    
    async def retrieve_memories(self, query: str = None, context: str = None, 
                               user_id: str = None, tags: List[str] = None,
                               limit: int = 10) -> List[MemoryEntry]:
        """
        Retrieve memories based on criteria
        
        Args:
            query: Search query
            context: Context filter
            user_id: User filter
            tags: Tag filters
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        try:
            matching_memories = []
            
            for memory in self.memories.values():
                # Apply filters
                if user_id and memory.user_id != user_id:
                    continue
                    
                if context and context.lower() not in memory.context.lower():
                    continue
                    
                if tags and not any(tag in memory.tags for tag in tags):
                    continue
                    
                if query and query.lower() not in memory.content.lower():
                    continue
                
                matching_memories.append(memory)
            
            # Sort by importance and recency
            matching_memories.sort(
                key=lambda m: (m.importance, m.timestamp), 
                reverse=True
            )
            
            return matching_memories[:limit]
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            return []
    
    async def store_data(self, key: str, data: Any) -> bool:
        """
        Store arbitrary data with a key (Redis-like interface)
        
        Args:
            key: Storage key
            data: Data to store
            
        Returns:
            Success status
        """
        try:
            # Store in a separate data structure for key-value storage
            if not hasattr(self, 'key_value_store'):
                self.key_value_store = {}
            
            self.key_value_store[key] = data
            self._save_memories()  # Save to persistent storage
            
            logger.debug(f"Stored data with key: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store data for key {key}: {e}")
            return False
    
    async def get_data(self, key: str) -> Any:
        """
        Retrieve data by key (Redis-like interface)
        
        Args:
            key: Storage key
            
        Returns:
            Stored data or None
        """
        try:
            if not hasattr(self, 'key_value_store'):
                self.key_value_store = {}
            
            return self.key_value_store.get(key)
            
        except Exception as e:
            logger.error(f"Failed to get data for key {key}: {e}")
            return None
    
    async def get_keys_pattern(self, pattern: str) -> List[str]:
        """
        Get keys matching a pattern (Redis-like interface)
        
        Args:
            pattern: Key pattern (supports * wildcard)
            
        Returns:
            List of matching keys
        """
        try:
            if not hasattr(self, 'key_value_store'):
                self.key_value_store = {}
            
            import fnmatch
            matching_keys = []
            
            for key in self.key_value_store.keys():
                if fnmatch.fnmatch(key, pattern):
                    matching_keys.append(key)
            
            return matching_keys
            
        except Exception as e:
            logger.error(f"Failed to get keys for pattern {pattern}: {e}")
            return []
    
    async def update_conversation_context(self, user_input: str, eliza_response: str,
                                        user_id: str = None, session_id: str = None):
        """
        Update conversation context
        
        Args:
            user_input: User's input
            eliza_response: Eliza's response
            user_id: User identifier
            session_id: Session identifier
        """
        try:
            context_entry = {
                'timestamp': datetime.now().isoformat(),
                'user_input': user_input,
                'eliza_response': eliza_response,
                'user_id': user_id,
                'session_id': session_id
            }
            
            self.conversation_context.append(context_entry)
            
            # Keep only recent context (last 50 exchanges)
            if len(self.conversation_context) > 50:
                self.conversation_context = self.conversation_context[-50:]
            
            # Store important conversations as memories
            if len(user_input) > 20:  # Only store substantial inputs
                await self.store_memory(
                    content=f"User said: {user_input}",
                    context="conversation",
                    importance=3,
                    tags=["conversation", "user_input"],
                    user_id=user_id,
                    session_id=session_id
                )
            
            logger.debug("Updated conversation context")
            
        except Exception as e:
            logger.error(f"Failed to update conversation context: {e}")
    
    def get_conversation_context(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation context"""
        return self.conversation_context[-limit:]
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]):
        """
        Update user profile information
        
        Args:
            user_id: User identifier
            profile_data: Profile data to update
        """
        try:
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = {
                    'created': datetime.now().isoformat(),
                    'interactions': 0
                }
            
            # Update profile
            self.user_profiles[user_id].update(profile_data)
            self.user_profiles[user_id]['last_updated'] = datetime.now().isoformat()
            self.user_profiles[user_id]['interactions'] += 1
            
            # Save to storage
            self._save_memories()
            
            logger.info(f"Updated profile for user: {user_id}")
            
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile"""
        return self.user_profiles.get(user_id, {})
    
    async def _cleanup_old_memories(self):
        """Clean up old memories based on retention policy"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.memory_retention_days)
            
            # Remove old, low-importance memories
            memories_to_remove = []
            for memory_id, memory in self.memories.items():
                if (memory.timestamp < cutoff_date and 
                    memory.importance < 7 and 
                    len(self.memories) > self.max_memories):
                    memories_to_remove.append(memory_id)
            
            for memory_id in memories_to_remove:
                del self.memories[memory_id]
            
            if memories_to_remove:
                logger.info(f"Cleaned up {len(memories_to_remove)} old memories")
                
        except Exception as e:
            logger.error(f"Failed to cleanup memories: {e}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory service statistics"""
        try:
            total_memories = len(self.memories)
            recent_memories = len([
                m for m in self.memories.values() 
                if (datetime.now() - m.timestamp).days < 7
            ])
            
            importance_distribution = {}
            for memory in self.memories.values():
                importance_distribution[memory.importance] = importance_distribution.get(memory.importance, 0) + 1
            
            return {
                'total_memories': total_memories,
                'recent_memories': recent_memories,
                'conversation_context_length': len(self.conversation_context),
                'user_profiles': len(self.user_profiles),
                'importance_distribution': importance_distribution,
                'memory_file': self.memory_file,
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {'error': str(e)}
    
    async def search_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search memories with relevance scoring
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of relevant memories with scores
        """
        try:
            query_lower = query.lower()
            scored_memories = []
            
            for memory in self.memories.values():
                score = 0
                
                # Content match
                if query_lower in memory.content.lower():
                    score += 10
                
                # Context match
                if query_lower in memory.context.lower():
                    score += 5
                
                # Tag match
                for tag in memory.tags:
                    if query_lower in tag.lower():
                        score += 3
                
                # Importance bonus
                score += memory.importance
                
                # Recency bonus
                days_old = (datetime.now() - memory.timestamp).days
                if days_old < 7:
                    score += 5
                elif days_old < 30:
                    score += 2
                
                if score > 0:
                    scored_memories.append({
                        'memory': memory.to_dict(),
                        'relevance_score': score
                    })
            
            # Sort by relevance score
            scored_memories.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            return scored_memories[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []

