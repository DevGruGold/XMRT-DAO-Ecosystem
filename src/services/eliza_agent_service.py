
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class ElizaAgentService:
    def __init__(self, mining_service, meshnet_service, speech_service=None, memory_service=None, gemini_service=None, web_browsing_service=None):
        self.logger = logging.getLogger(__name__)
        self.mining_service = mining_service
        self.meshnet_service = meshnet_service
        self.speech_service = speech_service
        self.memory_service = memory_service
        self.gemini_service = gemini_service
        self.web_browsing_service = web_browsing_service
        
        # Eliza personality and capabilities
        self.personality = {
            'name': 'Eliza',
            'role': 'XMRT-DAO Autonomous Operator',
            'voice_enabled': speech_service is not None,
            'memory_enabled': memory_service is not None,
            'gemini_enabled': gemini_service is not None,
            'web_browsing_enabled': web_browsing_service is not None,
            'autonomy_level': 'enhanced'
        }
        
        self.logger.info("Eliza Agent Service Initialized with enhanced capabilities.")
        if self.speech_service:
            self.logger.info("✅ Speech capabilities enabled")
        if self.memory_service:
            self.logger.info("✅ Memory capabilities enabled")
        if self.gemini_service:
            self.logger.info("✅ Gemini AI capabilities enabled")
        if self.web_browsing_service:
            self.logger.info("✅ Web browsing capabilities enabled")

    async def process_command(self, command_text: str, user_id: str = None, session_id: str = None):
        """
        Processes a natural language command and routes it to the appropriate service.
        Enhanced with memory, speech, and Gemini AI capabilities.
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

        # Use Gemini for enhanced command processing if available
        if self.gemini_service and self.gemini_service.client_available:
            try:
                # Get agent context for Gemini
                agent_context = await self._get_agent_context()
                
                # Use Gemini to enhance command understanding
                gemini_analysis = await self.gemini_service.enhance_command_processing(
                    command_text, agent_context
                )
                
                if gemini_analysis.get('success'):
                    self.logger.info("Using Gemini-enhanced command processing")
                    # Process with Gemini intelligence
                    response = await self._process_with_gemini(command_text, gemini_analysis, user_id, session_id)
                else:
                    # Fallback to traditional processing
                    response = await self._generate_response(command_text, user_id, session_id)
            except Exception as e:
                self.logger.warning(f"Gemini processing failed, using fallback: {e}")
                response = await self._generate_response(command_text, user_id, session_id)
        else:
            # Traditional processing
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
        
        # Web browsing commands
        elif any(keyword in command_text for keyword in ['browse', 'fetch', 'analyze webpage', 'web']) and self.web_browsing_service:
            return await self._handle_web_browsing_commands(command_text)
        
        # Gemini AI commands
        elif 'gemini' in command_text and self.gemini_service:
            return await self._handle_gemini_commands(command_text)
        
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
        
        if self.gemini_service:
            capabilities["enhanced_features"].append("Gemini AI intelligence")
            capabilities["enhanced_features"].append("Advanced reasoning and analysis")
            capabilities["enhanced_features"].append("Code analysis and generation")
        
        if self.web_browsing_service:
            capabilities["enhanced_features"].append("Web browsing and content fetching")
            capabilities["enhanced_features"].append("Webpage analysis and summarization")
            capabilities["enhanced_features"].append("Web search capabilities")
        
        capabilities["message"] = f"I am {self.personality['name']}, operating at {self.personality['autonomy_level']} autonomy level with {len(capabilities['enhanced_features'])} enhanced features active."
        
        return capabilities

    async def _generate_default_response(self, command_text: str, user_id: str = None) -> str:
        """Generate default response for unrecognized commands"""
        
        # Check memory for similar past interactions
        if self.memory_service:
            similar_memories = await self.memory_service.search_memories(command_text, limit=3)
            if similar_memories:
                return f"I don't recognize that specific command, but I found some related information from our past interactions. Try being more specific, or use one of these commands: 'status', 'dashboard', 'health', 'nodes', 'capabilities'."
        
        return {
            "response": "Command not recognized. I am Eliza, your autonomous operator for the XMRT-DAO Ecosystem.",
            "available_commands": ["status", "dashboard", "health", "nodes", "capabilities", "remember [text]", "voice status"],
            "suggestion": "Try asking about system status, mining dashboard, or network health."
        }

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
                "memory_service": self.memory_service is not None,
                "gemini_service": self.gemini_service is not None,
                "web_browsing_service": self.web_browsing_service is not None
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

    async def _get_agent_context(self) -> Dict[str, Any]:
        """Get current agent context for Gemini processing"""
        context = {
            "agent_name": self.personality['name'],
            "role": self.personality['role'],
            "capabilities": {
                "voice_enabled": self.personality['voice_enabled'],
                "memory_enabled": self.personality['memory_enabled'],
                "gemini_enabled": self.personality['gemini_enabled']
            },
            "available_services": {
                "mining": self.mining_service is not None,
                "meshnet": self.meshnet_service is not None,
                "speech": self.speech_service is not None,
                "memory": self.memory_service is not None,
                "gemini": self.gemini_service is not None,
                "web_browsing": self.web_browsing_service is not None
            }
        }
        
        # Add current system status if available
        try:
            if self.mining_service:
                mining_status = await self.mining_service.ping_mining_infrastructure()
                context["mining_status"] = mining_status
        except Exception as e:
            self.logger.debug(f"Could not get mining status for context: {e}")
        
        try:
            if self.meshnet_service:
                mesh_status = await self.meshnet_service.get_mesh_network_health()
                context["mesh_status"] = mesh_status
        except Exception as e:
            self.logger.debug(f"Could not get mesh status for context: {e}")
        
        return context
    
    async def _process_with_gemini(self, command_text: str, gemini_analysis: Dict[str, Any], user_id: str = None, session_id: str = None):
        """Process command using Gemini intelligence"""
        try:
            # Extract Gemini's analysis
            gemini_response = gemini_analysis.get('response', '')
            
            # Check if this is a complex query that needs Gemini's full response
            complex_keywords = ['analyze', 'explain', 'how', 'why', 'what if', 'compare', 'suggest', 'recommend']
            is_complex = any(keyword in command_text for keyword in complex_keywords)
            
            if is_complex:
                # For complex queries, use Gemini's response directly
                return {
                    "response": gemini_response,
                    "enhanced_by": "Gemini AI",
                    "analysis_type": "complex_reasoning",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # For simple commands, combine traditional processing with Gemini insights
                traditional_response = await self._generate_response(command_text, user_id, session_id)
                
                # Enhance traditional response with Gemini insights
                if isinstance(traditional_response, dict):
                    traditional_response["gemini_insights"] = gemini_response
                    traditional_response["enhanced_by"] = "Gemini AI"
                else:
                    traditional_response = {
                        "response": traditional_response,
                        "gemini_insights": gemini_response,
                        "enhanced_by": "Gemini AI",
                        "timestamp": datetime.now().isoformat()
                    }
                
                return traditional_response
                
        except Exception as e:
            self.logger.error(f"Error in Gemini processing: {e}")
            # Fallback to traditional processing
            return await self._generate_response(command_text, user_id, session_id)
    
    async def _handle_gemini_commands(self, command_text: str) -> str:
        """Handle Gemini-specific commands"""
        if not self.gemini_service:
            return "Gemini AI capabilities are not currently available."
        
        if 'gemini status' in command_text:
            status = await self.gemini_service.get_service_status()
            return f"Gemini AI Status: {status['status']}. Model: {status['model_name']}. Requests made: {status['statistics']['requests_made']}"
        
        elif 'gemini test' in command_text:
            test_result = await self.gemini_service.test_connection()
            if test_result['success']:
                return f"Gemini AI connection test successful: {test_result['response']}"
            else:
                return f"Gemini AI connection test failed: {test_result['error']}"
        
        elif 'analyze code' in command_text:
            return "Please provide code to analyze. Use format: 'analyze code: [your code here]'"
        
        elif command_text.startswith('analyze code:'):
            code_to_analyze = command_text.replace('analyze code:', '').strip()
            if code_to_analyze:
                analysis = await self.gemini_service.analyze_code(code_to_analyze)
                if analysis['success']:
                    return f"Code Analysis:\n{analysis['response']}"
                else:
                    return f"Code analysis failed: {analysis['error']}"
            else:
                return "No code provided for analysis."
        
        return "Gemini commands: 'gemini status', 'gemini test', 'analyze code: [code]'"


        
        if self.gemini_service:
            gemini_status = await self.gemini_service.get_service_status()
            status["gemini_status"] = gemini_status
        
        return status


    
    async def _handle_web_browsing_commands(self, command_text: str) -> str:
        """Handle web browsing commands"""
        if not self.web_browsing_service:
            return "Web browsing capabilities are not currently available."
        
        if 'web status' in command_text:
            status = await self.web_browsing_service.get_service_status()
            return f"Web Browsing Status: {status['status']}. Pages fetched: {status['statistics']['pages_fetched']}, Searches performed: {status['statistics']['searches_performed']}"
        
        elif command_text.startswith('fetch ') or command_text.startswith('browse '):
            # Extract URL from command
            url = command_text.replace('fetch ', '').replace('browse ', '').strip()
            if url.startswith('http'):
                result = await self.web_browsing_service.fetch_url(url)
                if result['success']:
                    return {
                        "url": result['url'],
                        "title": result['title'],
                        "content_preview": result['text_content'][:500] + "..." if len(result['text_content']) > 500 else result['text_content'],
                        "links_found": len(result['links']),
                        "timestamp": result['timestamp']
                    }
                else:
                    return f"Failed to fetch URL: {result['error']}"
            else:
                return "Please provide a valid URL starting with http:// or https://"
        
        elif command_text.startswith('analyze webpage '):
            # Extract URL and analysis prompt
            parts = command_text.replace('analyze webpage ', '').split(' for ')
            if len(parts) == 2:
                url, analysis_prompt = parts
                url = url.strip()
                analysis_prompt = analysis_prompt.strip()
                
                if url.startswith('http'):
                    result = await self.web_browsing_service.analyze_webpage(url, analysis_prompt, self.gemini_service)
                    if result['success']:
                        return {
                            "url": result['url'],
                            "analysis_prompt": result['analysis_prompt'],
                            "analysis": result['analysis'],
                            "timestamp": result['timestamp']
                        }
                    else:
                        return f"Failed to analyze webpage: {result['error']}"
                else:
                    return "Please provide a valid URL starting with http:// or https://"
            else:
                return "Please use format: 'analyze webpage [URL] for [analysis prompt]'"
        
        elif command_text.startswith('search '):
            query = command_text.replace('search ', '').strip()
            if query:
                result = await self.web_browsing_service.search_web(query)
                return f"Search initiated for: '{result['query']}'. Search URL: {result['search_url']}"
            else:
                return "Please provide a search query."
        
        return "Web browsing commands: 'web status', 'fetch [URL]', 'browse [URL]', 'analyze webpage [URL] for [prompt]', 'search [query]'"


        
        if self.web_browsing_service:
            web_status = await self.web_browsing_service.get_service_status()
            status["web_browsing_status"] = web_status
        
        return status

