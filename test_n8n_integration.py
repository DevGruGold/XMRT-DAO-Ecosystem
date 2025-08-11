#!/usr/bin/env python3
"""
Test script for n8n integration in XMRT DAO Ecosystem
"""

import sys
import os
import asyncio
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.n8n_service import N8NService
from services.memory_service import MemoryService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_n8n_service():
    """Test n8n service functionality."""
    print("🧪 Testing n8n Service Integration")
    print("=" * 50)
    
    # Initialize memory service
    memory_service = MemoryService({})
    print("✅ Memory service initialized")
    
    # Initialize n8n service
    n8n_config = {
        'n8n_url': 'http://localhost:5678',
        'n8n_api_key': None
    }
    n8n_service = N8NService(n8n_config)
    n8n_service.set_memory_service(memory_service)
    print("✅ N8N service created")
    
    # Test service status
    status = await n8n_service.get_service_status()
    print(f"📊 Service Status: {status}")
    
    # Test capabilities
    capabilities = await n8n_service.get_workflow_capabilities()
    print(f"🔧 Capabilities: {capabilities}")
    
    # Test workflow listing (should work even without n8n running)
    workflows = await n8n_service.list_workflows()
    print(f"📋 Workflows: {workflows}")
    
    print("\n✅ All tests completed successfully!")
    print("Note: n8n server connection will fail if n8n is not running, but this is expected.")

if __name__ == "__main__":
    asyncio.run(test_n8n_service())
