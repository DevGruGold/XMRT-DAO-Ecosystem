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
    category: Optional[str] = None  # New field for categorization

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

class EnhancedMemoryService:
    """Enhanced memory service for Eliza agent with XMRT knowledgebase integration"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.memory_file = self.config.get('memory_file', 'data/eliza_memory.json')
        self.knowledgebase_file = self.config.get('knowledgebase_file', 'data/xmrt_knowledgebase.json')
        self.max_memories = self.config.get('max_memories', 10000)
        self.memory_retention_days = self.config.get('retention_days', 30)

        # In-memory storage
        self.memories: Dict[str, MemoryEntry] = {}
        self.conversation_context: List[Dict[str, Any]] = []
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.xmrt_knowledgebase: Dict[str, Any] = {}

        # Initialize memory storage
        self.init_memory_storage()
        self._load_memories()
        self._load_xmrt_knowledgebase()

    def init_memory_storage(self):
        """Initialize memory storage directory"""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)

    def _load_memories(self):
        """Load memories from file"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                try:
                    data = json.load(f)
                    for mem_data in data.get('memories', []):
                        mem = MemoryEntry.from_dict(mem_data)
                        self.memories[mem.id] = mem
                    self.conversation_context = data.get('conversation_context', [])
                    self.user_profiles = data.get('user_profiles', {})
                    logger.info("✅ Memories loaded successfully.")
                except json.JSONDecodeError:
                    logger.warning("Memory file is empty or corrupted, starting fresh.")
                except Exception as e:
                    logger.error(f"Error loading memories: {e}")
        else:
            logger.info("No existing memory file found, starting fresh")

    def _load_xmrt_knowledgebase(self):
        """Load XMRT knowledgebase and integrate into memory"""
        try:
            # Try to load from provided knowledgebase file
            if os.path.exists(self.knowledgebase_file):
                with open(self.knowledgebase_file, 'r') as f:
                    self.xmrt_knowledgebase = json.load(f)
            else:
                # Load from default location
                default_kb_path = '/home/ubuntu/xmrt_knowledgebase.json'
                if os.path.exists(default_kb_path):
                    with open(default_kb_path, 'r') as f:
                        self.xmrt_knowledgebase = json.load(f)
                else:
                    logger.warning("XMRT knowledgebase file not found")
                    return

            # Integrate knowledgebase into memory system
            self._integrate_knowledgebase_into_memory()
            logger.info("✅ XMRT knowledgebase loaded and integrated successfully.")
            
        except Exception as e:
            logger.error(f"Error loading XMRT knowledgebase: {e}")

    def _integrate_knowledgebase_into_memory(self):
        """Integrate XMRT knowledgebase into memory system"""
        if not self.xmrt_knowledgebase:
            return

        kb_data = self.xmrt_knowledgebase.get('xmrt_dao_knowledgebase', {})
        
        # Create memory entries for different knowledge categories
        knowledge_categories = [
            ('project_overview', 'XMRT Project Overview', 9),
            ('technical_specifications', 'Technical Specifications', 8),
            ('tokenomics', 'Tokenomics and Economics', 9),
            ('governance', 'Governance Model', 8),
            ('revenue_streams', 'Revenue Streams', 7),
            ('treasury_management', 'Treasury Management', 8),
            ('ai_agents', 'AI Agents and Capabilities', 8),
            ('competitive_advantages', 'Competitive Advantages', 7),
            ('development_status', 'Development Status', 6),
            ('funding_information', 'Funding Information', 7),
            ('technical_architecture', 'Technical Architecture', 8),
            ('community_metrics', 'Community Metrics', 6)
        ]

        for category_key, category_name, importance in knowledge_categories:
            if category_key in kb_data:
                content = self._format_knowledge_content(kb_data[category_key], category_name)
                context = f"XMRT DAO Knowledgebase - {category_name}"
                tags = ['xmrt', 'dao', 'knowledgebase', category_key.replace('_', '-')]
                
                # Create memory entry
                mem_id = f"kb_{category_key}_{hashlib.sha256(content.encode()).hexdigest()[:8]}"
                
                # Check if this knowledge already exists
                if mem_id not in self.memories:
                    memory_entry = MemoryEntry(
                        id=mem_id,
                        content=content,
                        context=context,
                        importance=importance,
                        timestamp=datetime.now(),
                        tags=tags,
                        category='knowledgebase'
                    )
                    self.memories[mem_id] = memory_entry

        # Save updated memories
        self._save_memories()

    def _format_knowledge_content(self, data: Any, category_name: str) -> str:
        """Format knowledge data into readable content"""
        if isinstance(data, dict):
            content_parts = [f"{category_name}:"]
            for key, value in data.items():
                if isinstance(value, dict):
                    content_parts.append(f"\n{key.replace('_', ' ').title()}:")
                    for sub_key, sub_value in value.items():
                        content_parts.append(f"  - {sub_key.replace('_', ' ').title()}: {sub_value}")
                elif isinstance(value, list):
                    content_parts.append(f"\n{key.replace('_', ' ').title()}:")
                    for item in value:
                        content_parts.append(f"  - {item}")
                else:
                    content_parts.append(f"\n{key.replace('_', ' ').title()}: {value}")
            return '\n'.join(content_parts)
        elif isinstance(data, list):
            return f"{category_name}:\n" + '\n'.join([f"- {item}" for item in data])
        else:
            return f"{category_name}: {data}"

    def _save_memories(self):
        """Save memories to file"""
        data = {
            'memories': [mem.to_dict() for mem in self.memories.values()],
            'conversation_context': self.conversation_context,
            'user_profiles': self.user_profiles
        }
        with open(self.memory_file, 'w') as f:
            json.dump(data, f, indent=4)
        logger.info("✅ Memories saved successfully.")

    def add_memory(self, content: str, context: str, importance: int = 5, tags: List[str] = None, user_id: Optional[str] = None, session_id: Optional[str] = None, category: Optional[str] = None) -> str:
        """Add a new memory entry"""
        mem_id = hashlib.sha256((content + context + str(datetime.now())).encode()).hexdigest()[:12]
        new_memory = MemoryEntry(
            id=mem_id,
            content=content,
            context=context,
            importance=importance,
            timestamp=datetime.now(),
            tags=tags or [],
            user_id=user_id,
            session_id=session_id,
            category=category
        )
        self.memories[mem_id] = new_memory
        self._manage_memory_limit()
        self._save_memories()
        logger.info(f"Stored memory: {mem_id} - '{content[:50]}...'")
        return mem_id

    def get_memory(self, mem_id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory by its ID"""
        return self.memories.get(mem_id)

    def search_memories(self, query: str, user_id: Optional[str] = None, session_id: Optional[str] = None, limit: int = 10, include_knowledgebase: bool = True) -> List[MemoryEntry]:
        """Search memories by keyword or tags with enhanced XMRT knowledge search"""
        results = []
        query_lower = query.lower()
        
        # Search through all memories
        for mem in self.memories.values():
            # Skip user/session filtering for knowledgebase entries
            if mem.category != 'knowledgebase':
                if user_id and mem.user_id != user_id:
                    continue
                if session_id and mem.session_id != session_id:
                    continue
            
            # Enhanced search logic
            score = 0
            
            # Direct content match
            if query_lower in mem.content.lower():
                score += 10
            
            # Tag matches
            for tag in mem.tags:
                if query_lower in tag.lower():
                    score += 5
            
            # Context match
            if query_lower in mem.context.lower():
                score += 3
            
            # XMRT-specific keyword boosting
            xmrt_keywords = ['xmrt', 'dao', 'monero', 'mining', 'governance', 'staking', 'treasury', 'ai agent', 'eliza', 'token', 'blockchain']
            for keyword in xmrt_keywords:
                if keyword in query_lower and keyword in mem.content.lower():
                    score += 8
            
            if score > 0:
                results.append((mem, score))
        
        # Sort by score and importance
        results.sort(key=lambda x: (x[1], x[0].importance), reverse=True)
        
        return [mem for mem, score in results[:limit]]

    def get_xmrt_knowledge(self, topic: str = None) -> Dict[str, Any]:
        """Get specific XMRT knowledge by topic"""
        if not self.xmrt_knowledgebase:
            return {}
        
        kb_data = self.xmrt_knowledgebase.get('xmrt_dao_knowledgebase', {})
        
        if topic:
            # Return specific topic
            return kb_data.get(topic, {})
        else:
            # Return all knowledge
            return kb_data

    def answer_xmrt_question(self, question: str) -> str:
        """Provide intelligent answers about XMRT based on knowledgebase"""
        question_lower = question.lower()
        
        # Search for relevant memories
        relevant_memories = self.search_memories(question, limit=5, include_knowledgebase=True)
        
        if not relevant_memories:
            return "I don't have specific information about that topic in my current knowledge base. Could you please rephrase your question or ask about XMRT DAO's tokenomics, governance, AI agents, or technical specifications?"
        
        # Compile answer from relevant memories
        answer_parts = []
        for memory in relevant_memories[:3]:  # Use top 3 most relevant
            if memory.category == 'knowledgebase':
                answer_parts.append(memory.content)
        
        if answer_parts:
            return "\n\n".join(answer_parts)
        else:
            # Fallback to general XMRT information
            overview = self.get_xmrt_knowledge('project_overview')
            if overview:
                return f"XMRT-Ecosystem is {overview.get('description', 'a decentralized autonomous organization')}. Key features include: {', '.join(overview.get('key_features', []))}"
            
        return "I have information about XMRT DAO but couldn't find specific details for your question. Please ask about specific topics like tokenomics, governance, AI agents, or technical specifications."

    def update_memory(self, mem_id: str, new_content: Optional[str] = None, new_context: Optional[str] = None, new_importance: Optional[int] = None, new_tags: Optional[List[str]] = None):
        """Update an existing memory"""
        mem = self.memories.get(mem_id)
        if mem:
            if new_content: mem.content = new_content
            if new_context: mem.context = new_context
            if new_importance: mem.importance = new_importance
            if new_tags: mem.tags = new_tags
            mem.timestamp = datetime.now() # Update timestamp on modification
            self._save_memories()
            logger.info(f"Updated memory: {mem_id}")
        else:
            logger.warning(f"Memory {mem_id} not found for update.")

    def delete_memory(self, mem_id: str):
        """Delete a memory by its ID"""
        if mem_id in self.memories:
            del self.memories[mem_id]
            self._save_memories()
            logger.info(f"Deleted memory: {mem_id}")
        else:
            logger.warning(f"Memory {mem_id} not found for deletion.")

    def add_to_conversation_context(self, entry: Dict[str, Any], max_entries: int = 10):
        """Add an entry to the conversation context"""
        self.conversation_context.append(entry)
        # Keep only the last 'max_entries' for conversation context
        self.conversation_context = self.conversation_context[-max_entries:]
        self._save_memories()
        logger.info(f"Added to conversation context: {entry.get('role')}: {entry.get('content')[:50]}...")

    def get_conversation_context(self) -> List[Dict[str, Any]]:
        """Retrieve the current conversation context"""
        return self.conversation_context

    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]):
        """Update or create a user profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {}
        self.user_profiles[user_id].update(profile_data)
        self._save_memories()
        logger.info(f"Updated user profile for {user_id}")

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a user profile"""
        return self.user_profiles.get(user_id)

    def _manage_memory_limit(self):
        """Manage the total number of memories based on max_memories and retention days"""
        # Don't delete knowledgebase entries
        non_kb_memories = {k: v for k, v in self.memories.items() if v.category != 'knowledgebase'}
        
        # Remove oldest non-knowledgebase memories if exceeding max_memories
        if len(non_kb_memories) > self.max_memories:
            oldest_memories = sorted(non_kb_memories.values(), key=lambda x: x.timestamp)
            for i in range(len(non_kb_memories) - self.max_memories):
                del self.memories[oldest_memories[i].id]
            logger.info(f"Trimmed memories to {self.max_memories} entries.")

        # Remove old non-knowledgebase memories older than retention_days
        cutoff_date = datetime.now() - timedelta(days=self.memory_retention_days)
        memories_to_delete = [mem_id for mem_id, mem in self.memories.items() 
                             if mem.timestamp < cutoff_date and mem.category != 'knowledgebase']
        for mem_id in memories_to_delete:
            del self.memories[mem_id]
        if memories_to_delete:
            logger.info(f"Deleted {len(memories_to_delete)} old memories.")

    def clear_all_memories(self, preserve_knowledgebase: bool = True):
        """Clear all memories, conversation context, and user profiles"""
        if preserve_knowledgebase:
            # Keep only knowledgebase entries
            kb_memories = {k: v for k, v in self.memories.items() if v.category == 'knowledgebase'}
            self.memories = kb_memories
        else:
            self.memories = {}
        
        self.conversation_context = []
        self.user_profiles = {}
        self._save_memories()
        logger.info("All memories cleared (knowledgebase preserved)." if preserve_knowledgebase else "All memories cleared.")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the current memory usage"""
        kb_count = len([m for m in self.memories.values() if m.category == 'knowledgebase'])
        regular_count = len(self.memories) - kb_count
        
        return {
            "total_memories": len(self.memories),
            "knowledgebase_entries": kb_count,
            "regular_memories": regular_count,
            "conversation_context_entries": len(self.conversation_context),
            "user_profiles_count": len(self.user_profiles),
            "memory_file": self.memory_file,
            "knowledgebase_file": self.knowledgebase_file,
            "max_memories": self.max_memories,
            "memory_retention_days": self.memory_retention_days,
            "xmrt_knowledgebase_loaded": bool(self.xmrt_knowledgebase)
        }

    def reload_knowledgebase(self):
        """Reload the XMRT knowledgebase"""
        self._load_xmrt_knowledgebase()
        logger.info("XMRT knowledgebase reloaded.")

