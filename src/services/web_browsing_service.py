"""
XMRT-DAO Web Browsing Service
Provides capabilities for the Eliza agent to interact with the web
"""

import asyncio
import logging
import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class WebBrowsingService:
    """
    Web browsing service for Eliza agent providing web interaction capabilities
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.session = None
        self.search_engine_url = self.config.get("search_engine_url", "https://www.google.com/search?q=")
        
        # Service statistics
        self.stats = {
            'pages_fetched': 0,
            'searches_performed': 0,
            'failed_requests': 0,
            'last_request_time': None,
            'service_start_time': datetime.now().isoformat()
        }
        
    async def initialize_session(self):
        """Initialize the aiohttp client session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
            logger.info("✅ Web browsing session initialized")

    async def close_session(self):
        """Close the aiohttp client session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Web browsing session closed")

    async def fetch_url(self, url: str) -> Dict[str, Any]:
        """
        Fetch content from a given URL
        
        Args:
            url: The URL to fetch
            
        Returns:
            Dict containing page content and metadata
        """
        await self.initialize_session()
        
        try:
            self.stats["pages_fetched"] += 1
            self.stats["last_request_time"] = datetime.now().isoformat()
            
            async with self.session.get(url, timeout=15) as response:
                response.raise_for_status()  # Raise an exception for bad status codes
                
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                
                return {
                    'success': True,
                    'url': url,
                    'status_code': response.status,
                    'title': soup.title.string if soup.title else 'No title found',
                    'text_content': soup.get_text(separator='\n', strip=True),
                    'links': [a['href'] for a in soup.find_all('a', href=True)],
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            self.stats["failed_requests"] += 1
            logger.error(f"Error fetching URL {url}: {e}")
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }

    async def search_web(self, query: str) -> Dict[str, Any]:
        """
        Search the web using the configured search engine
        
        Args:
            query: The search query
            
        Returns:
            Dict containing search results
        """
        self.stats["searches_performed"] += 1
        search_url = f"{self.search_engine_url}{query}"
        
        # For now, we return the search URL. A more advanced implementation
        # would parse the search results page.
        return {
            'success': True,
            'query': query,
            'search_url': search_url,
            'message': 'Search initiated. Further implementation needed to parse results.',
            'timestamp': datetime.now().isoformat()
        }

    async def analyze_webpage(self, url: str, analysis_prompt: str, gemini_service) -> Dict[str, Any]:
        """
        Analyze a webpage using Gemini AI
        
        Args:
            url: The URL of the webpage to analyze
            analysis_prompt: The prompt for the analysis
            gemini_service: An instance of the GeminiService
            
        Returns:
            Dict containing the analysis results
        """
        if not gemini_service or not gemini_service.client_available:
            return {
                'success': False,
                'error': 'Gemini service not available for analysis'
            }

        fetch_result = await self.fetch_url(url)
        if not fetch_result['success']:
            return fetch_result

        page_content = fetch_result['text_content']
        
        # Prepare prompt for Gemini
        system_prompt = """You are a web content analysis expert. Analyze the provided text content from a webpage.
        Based on the user's request, provide a concise and accurate summary or analysis."""
        
        prompt = f"Please analyze the following webpage content based on this request: '{analysis_prompt}'\n\nWebpage URL: {url}\n\nWebpage Content:\n{page_content[:4000]}..."
        
        # Use Gemini for analysis
        analysis_result = await gemini_service.generate_response(prompt, system_prompt=system_prompt)
        
        return {
            'success': analysis_result['success'],
            'url': url,
            'analysis_prompt': analysis_prompt,
            'analysis': analysis_result.get('response'),
            'error': analysis_result.get('error'),
            'timestamp': datetime.now().isoformat()
        }

    async def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        return {
            'service_name': 'Web Browsing Service',
            'status': 'healthy' if self.session and not self.session.closed else 'inactive',
            'session_active': self.session and not self.session.closed,
            'statistics': self.stats.copy(),
            'timestamp': datetime.now().isoformat()
        }

    async def reset_stats(self) -> Dict[str, Any]:
        """Reset service statistics"""
        self.stats = {
            'pages_fetched': 0,
            'searches_performed': 0,
            'failed_requests': 0,
            'last_request_time': None,
            'service_start_time': datetime.now().isoformat()
        }
        return {
            'success': True,
            'message': 'Statistics reset successfully'
        }


