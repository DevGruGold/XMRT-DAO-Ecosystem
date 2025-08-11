import logging
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedElizaAgentService:
    """Enhanced Eliza Agent Service with XMRT DAO knowledge integration"""

    def __init__(self, mining_service=None, meshnet_service=None, speech_service=None, memory_service=None):
        self.mining_service = mining_service
        self.meshnet_service = meshnet_service
        self.speech_service = speech_service
        self.memory_service = memory_service
        
        # Agent configuration
        self.agent_config = {
            "name": "XMRT-DAO-Agent",
            "version": "2.3.0",
            "capabilities": [
                "XMRT DAO knowledge",
                "Treasury management insights",
                "Governance information",
                "Mining operations status",
                "Tokenomics explanations",
                "AI agent coordination"
            ]
        }
        
        # Initialize agent personality and knowledge
        self._initialize_agent_personality()
        
        logger.info("Eliza Agent Service Initialized with enhanced capabilities.")
        if self.speech_service:
            logger.info("✅ Speech capabilities enabled")
        if self.memory_service:
            logger.info("✅ Memory capabilities enabled")

    def _initialize_agent_personality(self):
        """Initialize the agent's personality and response patterns"""
        self.personality_traits = {
            "professional": True,
            "knowledgeable": True,
            "helpful": True,
            "technical": True,
            "community_focused": True
        }
        
        self.response_patterns = {
            "greeting": [
                "Hello! I'm the XMRT DAO AI agent. How can I help you with information about our decentralized autonomous organization?",
                "Welcome to XMRT DAO! I'm here to assist you with questions about our tokenomics, governance, or technical specifications.",
                "Greetings! I'm your XMRT DAO assistant, powered by real Monero mining revenue and AI-driven governance."
            ],
            "xmrt_info": [
                "XMRT is a revolutionary AI-governed DAO funded by real-world Monero mining operations.",
                "Our ecosystem features 21 million XMRT tokens with sophisticated staking mechanisms and cross-chain capabilities.",
                "XMRT DAO combines traditional cryptocurrency mining with modern DeFi governance structures."
            ],
            "technical": [
                "Our technical stack includes 59+ smart contracts, 15+ microservices, and advanced AI integration.",
                "We've implemented zero-knowledge voting with Noir circuits and RISC Zero agents.",
                "The system features cross-chain bridges using LayerZero and Wormhole protocols."
            ]
        }

    def process_command(self, command: str, user_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """Process user command and generate appropriate response"""
        try:
            # Store the user command in memory
            if self.memory_service:
                self.memory_service.add_memory(
                    content=f"User said: {command}",
                    context="User interaction",
                    importance=5,
                    tags=["user_input", "conversation"],
                    user_id=user_id,
                    session_id=session_id
                )

            # Analyze command and generate response
            response = self._generate_response(command, user_id, session_id)
            
            # Store the response in memory
            if self.memory_service:
                self.memory_service.add_memory(
                    content=f"Agent responded: {response}",
                    context="Agent response",
                    importance=4,
                    tags=["agent_response", "conversation"],
                    user_id=user_id,
                    session_id=session_id
                )

            # Generate speech if available
            if self.speech_service:
                try:
                    self.speech_service.generate_speech(response)
                    logger.info(f"Eliza spoke: '{response[:50]}...'")
                except Exception as e:
                    logger.warning(f"Speech generation failed: {e}")

            return response

        except Exception as e:
            logger.error(f"Error processing command '{command}': {e}")
            return "I apologize, but I encountered an error processing your request. Please try again."

    def _generate_response(self, command: str, user_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """Generate intelligent response based on command analysis"""
        command_lower = command.lower()
        
        # Check for XMRT-specific questions first
        if self._is_xmrt_question(command_lower):
            return self._handle_xmrt_question(command, user_id, session_id)
        
        # Handle greetings
        if any(greeting in command_lower for greeting in ['hello', 'hi', 'hey', 'greetings']):
            return self._get_greeting_response()
        
        # Handle memory and conversation questions
        if any(phrase in command_lower for phrase in ['remember', 'memory', 'who am i', 'do you know me']):
            return self._handle_memory_question(command, user_id, session_id)
        
        # Handle status questions
        if any(phrase in command_lower for phrase in ['status', 'health', 'how are you']):
            return self._get_status_response()
        
        # Handle mining questions
        if any(phrase in command_lower for phrase in ['mining', 'monero', 'xmr']):
            return self._handle_mining_question(command)
        
        # Handle governance questions
        if any(phrase in command_lower for phrase in ['governance', 'voting', 'proposal', 'dao']):
            return self._handle_governance_question(command)
        
        # Handle technical questions
        if any(phrase in command_lower for phrase in ['technical', 'smart contract', 'blockchain', 'api']):
            return self._handle_technical_question(command)
        
        # Default response with XMRT context
        return self._get_default_response(command)

    def _is_xmrt_question(self, command: str) -> bool:
        """Check if the command is asking about XMRT-specific topics"""
        xmrt_keywords = [
            'xmrt', 'token', 'tokenomics', 'staking', 'treasury', 'ai agent',
            'governance', 'dao', 'mining', 'monero', 'revenue', 'funding',
            'smart contract', 'cross-chain', 'bridge', 'eliza'
        ]
        return any(keyword in command for keyword in xmrt_keywords)

    def _handle_xmrt_question(self, command: str, user_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """Handle XMRT-specific questions using the knowledgebase"""
        if self.memory_service and hasattr(self.memory_service, 'answer_xmrt_question'):
            try:
                answer = self.memory_service.answer_xmrt_question(command)
                if answer and len(answer) > 50:  # Valid answer
                    return answer
            except Exception as e:
                logger.error(f"Error getting XMRT answer: {e}")
        
        # Fallback to pattern-based responses
        command_lower = command.lower()
        
        if 'tokenomics' in command_lower or 'token' in command_lower:
            return ("XMRT has a fixed supply of 21 million tokens with sophisticated staking mechanisms. "
                   "The token features governance rights, staking rewards up to 30% APR, and treasury access. "
                   "Distribution includes 35% for community rewards, 25% for staking pool, and 15% for development.")
        
        elif 'staking' in command_lower:
            return ("XMRT staking offers tiered rewards from 12% to 30% APR based on duration. "
                   "Minimum stake period is 7 days with 10% early withdrawal penalty. "
                   "Longer stakes get higher multipliers: 30 days (1.0x), 90 days (1.3x), up to 730 days (2.5x).")
        
        elif 'governance' in command_lower or 'dao' in command_lower:
            return ("XMRT DAO uses hybrid token-weighted voting with AI-assisted decision making. "
                   "Voting power = (Held tokens × 1.0) + (Staked tokens × 1.5) + (Delegated to AI × 2.0). "
                   "Different proposal types have varying thresholds, from 50k XMRT for AI agent deployment to 500k for emergency actions.")
        
        elif 'mining' in command_lower or 'revenue' in command_lower:
            return ("XMRT DAO is funded by real Monero mining operations contributing 45% of revenue ($67,500 monthly target). "
                   "Additional revenue comes from DeFi protocol fees (25%), cross-chain bridge fees (15%), "
                   "NFT marketplace commission (10%), and AI agent services (5%).")
        
        elif 'treasury' in command_lower:
            return ("The XMRT treasury holds $1.5M in assets with diversified allocation: "
                   "30% stablecoins, 25% XMRT tokens, 20% Ethereum, 15% Monero, and 10% DeFi yield positions. "
                   "Funds are deployed for development (40%), marketing (25%), strategic investments (20%), emergency reserve (10%), and community rewards (5%).")
        
        elif 'ai agent' in command_lower or 'eliza' in command_lower:
            return ("XMRT DAO features advanced AI agents using the Eliza framework for autonomous governance. "
                   "Capabilities include treasury management, governance participation, cross-chain operations, "
                   "community engagement, risk assessment, and performance reporting. Token holders can delegate voting power to specialized AI agents.")
        
        else:
            return ("XMRT-Ecosystem is a first-of-its-kind AI-governed DAO funded by real-world Monero mining. "
                   "We feature 59+ smart contracts, zero-knowledge voting, cross-chain operability, and decentralized AI agents. "
                   "Ask me about tokenomics, governance, staking, mining revenue, or technical specifications!")

    def _handle_memory_question(self, command: str, user_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """Handle questions about memory and user recognition"""
        if not self.memory_service:
            return "I don't have memory capabilities enabled at the moment."
        
        # Search for user-specific memories
        if user_id:
            user_memories = self.memory_service.search_memories("", user_id=user_id, limit=5)
            if user_memories:
                return f"Yes, I remember our previous conversations! I have {len(user_memories)} memories of our interactions. I have stored that information in my memory (ID: {user_memories[0].id[:8]}...)."
        
        # General memory response
        stats = self.memory_service.get_memory_stats()
        return (f"I have memory capabilities with {stats['total_memories']} total memories stored, "
               f"including {stats['knowledgebase_entries']} XMRT knowledgebase entries. "
               f"I can remember our conversations and provide information about XMRT DAO.")

    def _get_greeting_response(self) -> str:
        """Get a greeting response"""
        import random
        return random.choice(self.response_patterns["greeting"])

    def _get_status_response(self) -> str:
        """Get system status response"""
        status_parts = ["I'm operating normally with all systems functional."]
        
        if self.mining_service:
            try:
                mining_status = self.mining_service.get_status()
                if mining_status.get('operational', False):
                    status_parts.append("Mining operations are active and contributing to the treasury.")
            except Exception as e:
                logger.warning(f"Could not get mining status: {e}")
        
        if self.memory_service:
            stats = self.memory_service.get_memory_stats()
            status_parts.append(f"Memory system is active with {stats['total_memories']} stored memories.")
        
        return " ".join(status_parts)

    def _handle_mining_question(self, command: str) -> str:
        """Handle mining-related questions"""
        if self.mining_service:
            try:
                status = self.mining_service.get_status()
                return (f"Mining operations are {'active' if status.get('operational', False) else 'inactive'}. "
                       f"Our Monero mining provides sustainable revenue for the XMRT DAO treasury, "
                       f"targeting $67,500 monthly with 8% growth rate.")
            except Exception as e:
                logger.warning(f"Could not get mining status: {e}")
        
        return ("XMRT DAO is uniquely funded by real Monero mining operations through MobileMonero.com pool. "
               "Mining revenue contributes 45% of our total income, providing sustainable cash flow for the ecosystem.")

    def _handle_governance_question(self, command: str) -> str:
        """Handle governance-related questions"""
        return ("XMRT DAO implements sophisticated governance with token-weighted voting and AI assistance. "
               "Proposal types include treasury allocation (66% approval needed), protocol upgrades (75% approval), "
               "and AI agent deployment (60% approval). Token holders can delegate voting power to AI agents for automated participation.")

    def _handle_technical_question(self, command: str) -> str:
        """Handle technical questions"""
        return ("XMRT features 59+ smart contracts across governance, treasury, voting, and staking. "
               "Technical stack includes 15+ microservices in Python & JavaScript, ZK voting with Noir circuits, "
               "RISC Zero agents, IPFS fork for AI model storage, and cross-chain bridges using LayerZero and Wormhole.")

    def _get_default_response(self, command: str) -> str:
        """Get default response for unrecognized commands"""
        return ("I'm the XMRT DAO AI agent, here to help with information about our decentralized autonomous organization. "
               "You can ask me about tokenomics, governance, staking rewards, mining operations, AI agents, "
               "technical specifications, or treasury management. How can I assist you today?")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status"""
        status = {
            "agent_name": self.agent_config["name"],
            "version": self.agent_config["version"],
            "capabilities": self.agent_config["capabilities"],
            "services": {
                "mining_service": self.mining_service is not None,
                "meshnet_service": self.meshnet_service is not None,
                "speech_service": self.speech_service is not None,
                "memory_service": self.memory_service is not None
            },
            "operational": True,
            "last_updated": datetime.now().isoformat()
        }
        
        if self.memory_service:
            status["memory_stats"] = self.memory_service.get_memory_stats()
        
        return status

    def get_conversation_summary(self, user_id: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """Get a summary of recent conversations"""
        if not self.memory_service:
            return "Memory service not available for conversation summary."
        
        try:
            recent_memories = self.memory_service.search_memories(
                "", user_id=user_id, session_id=session_id, limit=10
            )
            
            if not recent_memories:
                return "No recent conversation history found."
            
            summary_parts = ["Recent conversation summary:"]
            for memory in recent_memories[-5:]:  # Last 5 interactions
                if "User said:" in memory.content:
                    summary_parts.append(f"- {memory.content}")
                elif "Agent responded:" in memory.content:
                    summary_parts.append(f"- {memory.content}")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error generating conversation summary: {e}")
            return "Error generating conversation summary."

    def reload_knowledge(self):
        """Reload the XMRT knowledgebase"""
        if self.memory_service and hasattr(self.memory_service, 'reload_knowledgebase'):
            try:
                self.memory_service.reload_knowledgebase()
                return "XMRT knowledgebase reloaded successfully."
            except Exception as e:
                logger.error(f"Error reloading knowledgebase: {e}")
                return f"Error reloading knowledgebase: {e}"
        return "Memory service or knowledgebase reload not available."

