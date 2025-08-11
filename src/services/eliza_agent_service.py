
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class ElizaAgentService:
    def __init__(self, mining_service, meshnet_service, speech_service=None, memory_service=None):
        self.logger = logging.getLogger(__name__)
        self.mining_service = mining_service
        self.meshnet_service = meshnet_service
        self.speech_service = speech_service
        self.memory_service = memory_service
        
        # Eliza personality and capabilities
        self.personality = {
            'name': 'Eliza',
            'role': 'XMRT-DAO Autonomous Operator',
            'voice_enabled': speech_service is not None,
            'memory_enabled': memory_service is not None,
            'autonomy_level': 'enhanced'
        }
        
        self.logger.info("Eliza Agent Service Initialized with enhanced capabilities.")
        if self.speech_service:
            self.logger.info("✅ Speech capabilities enabled")
        if self.memory_service:
            self.logger.info("✅ Memory capabilities enabled")

    async def process_command(self, command_text: str, user_id: str = None, session_id: str = None):
        """
        Processes a natural language command and routes it to the appropriate service.
        Enhanced with memory and speech capabilities.
        """
        command_text = command_text.lower().strip()
        self.logger.info(f"Processing command: '{command_text}'")

        # Store user interaction in memory
        if self.memory_service:
            await self.memory_service.update_conversation_context(
                user_input=command_text,
                eliza_response="",  # Will be updated after response
                user_id=user_id,
                session_id=session_id
            )

        # Process command and generate response
        response = await self._generate_response(command_text, user_id, session_id)
        
        # Update memory with response
        if self.memory_service:
            await self.memory_service.update_conversation_context(
                user_input=command_text,
                eliza_response=str(response),
                user_id=user_id,
                session_id=session_id
            )
        
        # Generate speech if enabled
        if self.speech_service and self.speech_service.voice_enabled:
            speech_result = await self.speech_service.speak_response(str(response))
            if speech_result.get('success'):
                response = {
                    'text_response': response,
                    'speech_response': speech_result,
                    'has_voice': True
                }
        
        return response

    async def _generate_response(self, command_text: str, user_id: str = None, session_id: str = None):
        """Generate appropriate response based on command"""
        
        # Greeting and introduction
        if any(word in command_text for word in ['hello', 'hi', 'greetings', 'hey']):
            self.logger.info("Command recognized: Greeting")
            return await self._generate_greeting(user_id)
        
        # Health check
        elif 'health' in command_text:
            self.logger.info("Command recognized: Performing health check.")
            try:
                mining_health = await self.mining_service.ping_mining_infrastructure()
                mesh_health = await self.meshnet_service.get_mesh_network_health()
                return {
                    "status": "Health check completed",
                    "mining_infrastructure": mining_health, 
                    "meshnet_infrastructure": mesh_health,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                return f"Error: An internal error occurred in the agent: {str(e)}"

        # Dashboard and status
        elif 'dashboard' in command_text or 'status' in command_text:
            self.logger.info("Command recognized: Fetching system dashboard.")
            try:
                dashboard = await self.mining_service.get_comprehensive_mining_dashboard()
                return dashboard
            except Exception as e:
                return f"Error fetching dashboard: {str(e)}"

        # MESHNET nodes
        elif 'nodes' in command_text or 'mesh' in command_text:
            self.logger.info("Command recognized: Fetching MESHNET information.")
            try:
                mesh_status = self.meshnet_service.get_mesh_network_status()
                return {
                    "meshnet_status": mesh_status,
                    "message": "MESHNET is operational with secure mesh connectivity"
                }
            except Exception as e:
                return f"Error fetching MESHNET data: {str(e)}"
        
        # Memory commands
        elif 'remember' in command_text and self.memory_service:
            return await self._handle_memory_command(command_text, user_id, session_id)
        
        # Voice commands
        elif 'voice' in command_text or 'speak' in command_text:
            return await self._handle_voice_command(command_text)
        
        # Capabilities inquiry
        elif 'capabilities' in command_text or 'what can you do' in command_text:
            return await self._describe_capabilities()
        
        # Mining operations
        elif 'mining' in command_text or 'xmr' in command_text:
            self.logger.info("Command recognized: Mining operations inquiry")
            try:
                mining_stats = await self.mining_service.get_comprehensive_mining_dashboard()
                return {
                    "mining_operations": mining_stats,
                    "message": "XMRT mining operations are active and contributing to the DAO treasury"
                }
            except Exception as e:
                return f"Error accessing mining data: {str(e)}"
        
        # Default response with personality
        else:
            self.logger.warning(f"Unknown command: '{command_text}'")
            return await self._generate_default_response(command_text, user_id)

    async def _generate_greeting(self, user_id: str = None) -> str:
        """Generate personalized greeting"""
        base_greeting = f"Greetings, Founder. I am {self.personality['name']}, the {self.personality['role']} for the XMRT-DAO Ecosystem."
        
        # Add user-specific information if available
        if self.memory_service and user_id:
            profile = self.memory_service.get_user_profile(user_id)
            if profile:
                interactions = profile.get('interactions', 0)
                if interactions > 1:
                    base_greeting += f" Welcome back! We've interacted {interactions} times before."
        
        # Add current status
        base_greeting += " My systems are online and fully operational. How may I assist you today?"
        
        # Add available commands
        base_greeting += " Available commands: 'status', 'dashboard', 'health', 'nodes', 'capabilities'."
        
        return base_greeting

    async def _handle_memory_command(self, command_text: str, user_id: str, session_id: str) -> str:
        """Handle memory-related commands"""
        if 'remember' in command_text:
            # Extract what to remember
            remember_text = command_text.replace('remember', '').strip()
            if remember_text:
                memory_id = await self.memory_service.store_memory(
                    content=remember_text,
                    context="user_request",
                    importance=7,
                    tags=["user_request", "important"],
                    user_id=user_id,
                    session_id=session_id
                )
                return f"I have stored that information in my memory (ID: {memory_id}). I will remember: {remember_text}"
            else:
                return "What would you like me to remember?"
        
        elif 'recall' in command_text or 'what do you remember' in command_text:
            memories = await self.memory_service.retrieve_memories(
                user_id=user_id,
                limit=5
            )
            if memories:
                memory_list = []
                for memory in memories:
                    memory_list.append(f"- {memory.content} (importance: {memory.importance})")
                return f"Here are some things I remember:\n" + "\n".join(memory_list)
            else:
                return "I don't have any specific memories stored for you yet."
        
        return "I can help you with memory operations. Try 'remember [something]' or 'what do you remember'."

    async def _handle_voice_command(self, command_text: str) -> str:
        """Handle voice-related commands"""
        if not self.speech_service:
            return "Voice capabilities are not currently available."
        
        if 'enable voice' in command_text:
            self.speech_service.enable_voice()
            return "Voice capabilities have been enabled. I can now speak my responses."
        
        elif 'disable voice' in command_text:
            self.speech_service.disable_voice()
            return "Voice capabilities have been disabled."
        
        elif 'voice status' in command_text:
            status = self.speech_service.get_voice_status()
            return f"Voice status: {'Enabled' if status['voice_enabled'] else 'Disabled'}. Current voice: {status['default_voice']}"
        
        return "Voice commands: 'enable voice', 'disable voice', 'voice status'"

    async def _describe_capabilities(self) -> Dict[str, Any]:
        """Describe Eliza's current capabilities"""
        capabilities = {
            "core_functions": [
                "System health monitoring",
                "Mining operations oversight",
                "MESHNET coordination",
                "DAO treasury management",
                "Real-time dashboard access"
            ],
            "enhanced_features": [],
            "autonomy_level": self.personality['autonomy_level'],
            "voice_enabled": self.personality['voice_enabled'],
            "memory_enabled": self.personality['memory_enabled']
        }
        
        if self.speech_service:
            capabilities["enhanced_features"].append("Text-to-speech synthesis")
            capabilities["enhanced_features"].append("Voice response generation")
        
        if self.memory_service:
            capabilities["enhanced_features"].append("Persistent memory storage")
            capabilities["enhanced_features"].append("Conversation context tracking")
            capabilities["enhanced_features"].append("User profile management")
        
        capabilities["message"] = f"I am {self.personality['name']}, operating at {self.personality['autonomy_level']} autonomy level with {len(capabilities['enhanced_features'])} enhanced features active."
        
        return capabilities

    async def _generate_default_response(self, command_text: str, user_id: str = None) -> str:
        """Generate default response for unrecognized commands"""
        
        # Check memory for similar past interactions
        if self.memory_service:
            similar_memories = await self.memory_service.search_memories(command_text, limit=3)
            if similar_memories:
                return f"I don't recognize that specific command, but I found some related information from our past interactions. Try being more specific, or use one of these commands: 'status', 'dashboard', 'health', 'nodes', 'capabilities'."
        
        available_commands = ["status", "dashboard", "health", "nodes", "capabilities", "remember [text]", "voice status"]
        suggestion = "Try asking about system status, mining dashboard, or network health."
        commands_str = ", ".join(available_commands)
        return f"Command not recognized. I am Eliza, your autonomous operator for the XMRT-DAO Ecosystem. Available commands: {commands_str}. Suggestion: {suggestion}"

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        status = {
            "agent_name": self.personality['name'],
            "role": self.personality['role'],
            "autonomy_level": self.personality['autonomy_level'],
            "voice_enabled": self.personality['voice_enabled'],
            "memory_enabled": self.personality['memory_enabled'],
            "services_connected": {
                "mining_service": self.mining_service is not None,
                "meshnet_service": self.meshnet_service is not None,
                "speech_service": self.speech_service is not None,
                "memory_service": self.memory_service is not None
            },
            "last_check": datetime.now().isoformat()
        }
        
        if self.memory_service:
            memory_stats = self.memory_service.get_memory_stats()
            status["memory_stats"] = memory_stats
        
        if self.speech_service:
            voice_status = self.speech_service.get_voice_status()
            status["voice_status"] = voice_status
        
        return status
