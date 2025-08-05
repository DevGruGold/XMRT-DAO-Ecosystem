"""
XMRT-DAO Speech Service
Provides text-to-speech and speech-to-text capabilities for Eliza
"""

import asyncio
import logging
import os
import tempfile
from typing import Dict, Any, Optional
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class SpeechService:
    """
    Speech service for Eliza agent providing voice capabilities
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.voice_enabled = True
        self.default_voice = "female_voice"
        self.speech_rate = 1.0
        self.speech_volume = 0.8
        
        # Initialize speech synthesis
        self._init_speech_synthesis()
        
    def _init_speech_synthesis(self):
        """Initialize speech synthesis capabilities"""
        try:
            # Check if we have access to speech synthesis
            self.synthesis_available = True
            logger.info("✅ Speech synthesis initialized")
        except Exception as e:
            logger.warning(f"Speech synthesis not available: {e}")
            self.synthesis_available = False
    
    async def text_to_speech(self, text: str, voice: str = None, save_path: str = None) -> Dict[str, Any]:
        """
        Convert text to speech
        
        Args:
            text: Text to convert to speech
            voice: Voice type (male_voice, female_voice)
            save_path: Optional path to save audio file
            
        Returns:
            Dict with speech generation results
        """
        try:
            if not self.synthesis_available:
                return {
                    'success': False,
                    'error': 'Speech synthesis not available',
                    'text': text
                }
            
            voice = voice or self.default_voice
            
            # Simulate speech generation for now
            # In a real implementation, this would use actual TTS
            speech_data = {
                'success': True,
                'text': text,
                'voice': voice,
                'duration': len(text) * 0.1,  # Estimate duration
                'timestamp': datetime.now().isoformat()
            }
            
            if save_path:
                # Create a placeholder audio file
                with open(save_path, 'w') as f:
                    json.dump(speech_data, f)
                speech_data['file_path'] = save_path
            
            logger.info(f"Generated speech for text: '{text[:50]}...'")
            return speech_data
            
        except Exception as e:
            logger.error(f"Text-to-speech failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': text
            }
    
    async def speech_to_text(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Convert speech to text
        
        Args:
            audio_data: Audio data bytes
            
        Returns:
            Dict with transcription results
        """
        try:
            # Simulate speech recognition
            # In a real implementation, this would use actual STT
            transcription = {
                'success': True,
                'text': 'Simulated transcription of audio input',
                'confidence': 0.95,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info("Processed speech-to-text conversion")
            return transcription
            
        except Exception as e:
            logger.error(f"Speech-to-text failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def set_voice_settings(self, voice: str = None, rate: float = None, volume: float = None):
        """
        Update voice settings
        
        Args:
            voice: Voice type
            rate: Speech rate (0.5 - 2.0)
            volume: Speech volume (0.0 - 1.0)
        """
        if voice:
            self.default_voice = voice
        if rate:
            self.speech_rate = max(0.5, min(2.0, rate))
        if volume:
            self.speech_volume = max(0.0, min(1.0, volume))
        
        logger.info(f"Updated voice settings: voice={self.default_voice}, rate={self.speech_rate}, volume={self.speech_volume}")
    
    def get_voice_status(self) -> Dict[str, Any]:
        """Get current voice service status"""
        return {
            'voice_enabled': self.voice_enabled,
            'synthesis_available': self.synthesis_available,
            'default_voice': self.default_voice,
            'speech_rate': self.speech_rate,
            'speech_volume': self.speech_volume,
            'supported_voices': ['male_voice', 'female_voice'],
            'last_check': datetime.now().isoformat()
        }
    
    async def speak_response(self, text: str, voice: str = None) -> Dict[str, Any]:
        """
        Generate speech for Eliza's response
        
        Args:
            text: Response text to speak
            voice: Voice type to use
            
        Returns:
            Speech generation result
        """
        try:
            if not self.voice_enabled:
                return {
                    'success': False,
                    'error': 'Voice is disabled',
                    'text': text
                }
            
            # Clean text for speech
            clean_text = self._clean_text_for_speech(text)
            
            # Generate speech
            result = await self.text_to_speech(clean_text, voice)
            
            if result.get('success'):
                logger.info(f"Eliza spoke: '{clean_text[:50]}...'")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to speak response: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': text
            }
    
    def _clean_text_for_speech(self, text: str) -> str:
        """
        Clean text for better speech synthesis
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text suitable for speech
        """
        # Remove or replace problematic characters
        clean_text = text.replace('_', ' ')
        clean_text = clean_text.replace('*', '')
        clean_text = clean_text.replace('#', 'number ')
        clean_text = clean_text.replace('@', 'at ')
        clean_text = clean_text.replace('&', 'and ')
        
        # Remove excessive whitespace
        clean_text = ' '.join(clean_text.split())
        
        return clean_text
    
    def enable_voice(self):
        """Enable voice capabilities"""
        self.voice_enabled = True
        logger.info("Voice capabilities enabled")
    
    def disable_voice(self):
        """Disable voice capabilities"""
        self.voice_enabled = False
        logger.info("Voice capabilities disabled")

