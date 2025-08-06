"""
XMRT-DAO Gemini Service
Provides Google Gemini AI capabilities for enhanced intelligence and reasoning
"""

import asyncio
import logging
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import aiohttp
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Gemini service for Eliza agent providing advanced AI capabilities
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.model_name = self.config.get('model_name', 'gemini-pro')
        self.max_tokens = self.config.get('max_tokens', 8192)
        self.temperature = self.config.get('temperature', 0.7)
        
        # Initialize Gemini client
        self._init_gemini_client()
        
        # Service statistics
        self.stats = {
            'requests_made': 0,
            'successful_responses': 0,
            'failed_requests': 0,
            'total_tokens_used': 0,
            'last_request_time': None,
            'service_start_time': datetime.now().isoformat()
        }
        
    def _init_gemini_client(self):
        """Initialize Gemini AI client"""
        try:
            if not self.api_key:
                logger.warning("GEMINI_API_KEY not found in environment variables")
                self.client_available = False
                return
                
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            # Initialize the model with safety settings
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
            
            generation_config = {
                "temperature": self.temperature,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": self.max_tokens,
            }
            
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            self.client_available = True
            logger.info(f"✅ Gemini AI client initialized with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.client_available = False
    
    async def generate_response(self, prompt: str, context: Optional[str] = None, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response using Gemini AI
        
        Args:
            prompt: The user prompt
            context: Optional context for the conversation
            system_prompt: Optional system prompt to guide behavior
            
        Returns:
            Dict containing response and metadata
        """
        if not self.client_available:
            return {
                'success': False,
                'error': 'Gemini client not available',
                'response': None
            }
        
        try:
            self.stats['requests_made'] += 1
            self.stats['last_request_time'] = datetime.now().isoformat()
            
            # Construct the full prompt
            full_prompt = ""
            if system_prompt:
                full_prompt += f"System: {system_prompt}\n\n"
            if context:
                full_prompt += f"Context: {context}\n\n"
            full_prompt += f"User: {prompt}"
            
            # Generate response
            response = await asyncio.to_thread(self.model.generate_content, full_prompt)
            
            if response.text:
                self.stats['successful_responses'] += 1
                # Estimate token usage (rough approximation)
                estimated_tokens = len(full_prompt.split()) + len(response.text.split())
                self.stats['total_tokens_used'] += estimated_tokens
                
                return {
                    'success': True,
                    'response': response.text,
                    'estimated_tokens': estimated_tokens,
                    'model_used': self.model_name,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                self.stats['failed_requests'] += 1
                return {
                    'success': False,
                    'error': 'No response generated',
                    'response': None
                }
                
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"Error generating Gemini response: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': None
            }
    
    async def analyze_code(self, code: str, language: str = "python", task: str = "analyze") -> Dict[str, Any]:
        """
        Analyze code using Gemini AI
        
        Args:
            code: The code to analyze
            language: Programming language
            task: Type of analysis (analyze, optimize, debug, explain)
            
        Returns:
            Dict containing analysis results
        """
        system_prompt = f"""You are an expert {language} developer. Your task is to {task} the provided code.
        
        For analysis, provide:
        - Code quality assessment
        - Potential issues or bugs
        - Performance considerations
        - Security concerns
        - Improvement suggestions
        
        For optimization, provide:
        - Optimized version of the code
        - Explanation of improvements
        
        For debugging, provide:
        - Identified issues
        - Suggested fixes
        
        For explanation, provide:
        - Clear explanation of what the code does
        - How it works step by step"""
        
        prompt = f"Please {task} this {language} code:\n\n```{language}\n{code}\n```"
        
        return await self.generate_response(prompt, system_prompt=system_prompt)
    
    async def process_multimodal(self, text: str, media_data: Optional[bytes] = None, media_type: str = "image") -> Dict[str, Any]:
        """
        Process multimodal input (text + media)
        
        Args:
            text: Text prompt
            media_data: Binary media data
            media_type: Type of media (image, audio, video)
            
        Returns:
            Dict containing processing results
        """
        # For now, process as text-only since multimodal requires specific setup
        # This can be enhanced later with proper media handling
        
        if media_data:
            prompt = f"{text}\n\n[Note: Media content provided but not processed in current implementation]"
        else:
            prompt = text
            
        return await self.generate_response(prompt)
    
    async def enhance_command_processing(self, user_command: str, agent_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance command processing with Gemini intelligence
        
        Args:
            user_command: The user's command
            agent_context: Current agent context and capabilities
            
        Returns:
            Dict containing enhanced command interpretation
        """
        system_prompt = """You are Eliza, an autonomous AI agent for the XMRT-DAO-Ecosystem. 
        You have access to various services including mining, mesh networking, speech synthesis, 
        memory management, and autonomous task execution.
        
        Your capabilities include:
        - Mining operations and dashboard monitoring
        - Mesh network management
        - Speech synthesis and voice interaction
        - Memory storage and retrieval
        - Autonomous task execution
        - Health monitoring and system status
        
        Analyze the user command and provide:
        1. Command interpretation
        2. Suggested actions
        3. Required services
        4. Expected outcomes
        5. Any clarifications needed
        
        Be helpful, intelligent, and maintain the personality of an autonomous DAO operator."""
        
        context = f"Agent Context: {json.dumps(agent_context, indent=2)}"
        prompt = f"User Command: {user_command}"
        
        return await self.generate_response(prompt, context=context, system_prompt=system_prompt)
    
    async def generate_autonomous_tasks(self, current_status: Dict[str, Any], goals: List[str]) -> Dict[str, Any]:
        """
        Generate autonomous tasks based on current status and goals
        
        Args:
            current_status: Current system status
            goals: List of goals to achieve
            
        Returns:
            Dict containing suggested autonomous tasks
        """
        system_prompt = """You are an autonomous task generator for the XMRT-DAO-Ecosystem.
        Based on the current system status and goals, generate specific, actionable tasks
        that the autonomous agent can execute.
        
        Tasks should be:
        - Specific and measurable
        - Achievable with current capabilities
        - Aligned with the provided goals
        - Prioritized by importance
        
        Format your response as a structured list of tasks with:
        - Task description
        - Priority level (high, medium, low)
        - Required services
        - Expected duration
        - Success criteria"""
        
        context = f"Current Status: {json.dumps(current_status, indent=2)}\nGoals: {json.dumps(goals, indent=2)}"
        prompt = "Generate autonomous tasks based on the current status and goals."
        
        return await self.generate_response(prompt, context=context, system_prompt=system_prompt)
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        return {
            'service_name': 'Gemini AI Service',
            'status': 'healthy' if self.client_available else 'degraded',
            'client_available': self.client_available,
            'model_name': self.model_name,
            'api_key_configured': bool(self.api_key),
            'statistics': self.stats.copy(),
            'configuration': {
                'max_tokens': self.max_tokens,
                'temperature': self.temperature,
                'model_name': self.model_name
            },
            'timestamp': datetime.now().isoformat()
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Gemini API"""
        if not self.client_available:
            return {
                'success': False,
                'error': 'Gemini client not available'
            }
        
        try:
            test_response = await self.generate_response("Hello, this is a connection test. Please respond with 'Connection successful'.")
            return {
                'success': test_response['success'],
                'response': test_response.get('response', ''),
                'error': test_response.get('error')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_gemini_stats(self) -> Dict[str, Any]:
        """Get Gemini service statistics"""
        return {
            'success': True,
            'data': self.stats.copy()
        }
    
    async def reset_stats(self) -> Dict[str, Any]:
        """Reset service statistics"""
        self.stats = {
            'requests_made': 0,
            'successful_responses': 0,
            'failed_requests': 0,
            'total_tokens_used': 0,
            'last_request_time': None,
            'service_start_time': datetime.now().isoformat()
        }
        return {
            'success': True,
            'message': 'Statistics reset successfully'
        }

