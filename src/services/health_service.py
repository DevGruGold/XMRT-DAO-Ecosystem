"""
XMRT-DAO Health Service
Provides comprehensive health monitoring for all system components
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
import aiohttp
import subprocess

logger = logging.getLogger(__name__)

class HealthService:
    """
    Centralized health monitoring service for XMRT-DAO ecosystem
    """
    
    def __init__(self, mining_service=None, meshnet_service=None):
        self.mining_service = mining_service
        self.meshnet_service = meshnet_service
        self.last_health_check = None
        self.health_cache = {}
        self.cache_duration = 30  # Cache health results for 30 seconds
        
    async def get_comprehensive_health(self) -> Dict[str, Any]:
        """
        Get comprehensive health status for all services
        """
        try:
            # Check if we have cached results
            if (self.last_health_check and 
                time.time() - self.last_health_check < self.cache_duration):
                return self.health_cache
                
            health_status = {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'healthy',
                'services': {},
                'network': {},
                'system': {}
            }
            
            # Check mining service health
            if self.mining_service:
                try:
                    mining_health = await self._check_mining_health()
                    health_status['services']['mining'] = mining_health
                except Exception as e:
                    logger.error(f"Mining health check failed: {e}")
                    health_status['services']['mining'] = {
                        'status': 'unhealthy',
                        'error': str(e)
                    }
            
            # Check meshnet service health
            if self.meshnet_service:
                try:
                    meshnet_health = await self._check_meshnet_health()
                    health_status['services']['meshnet'] = meshnet_health
                except Exception as e:
                    logger.error(f"Meshnet health check failed: {e}")
                    health_status['services']['meshnet'] = {
                        'status': 'unhealthy',
                        'error': str(e)
                    }
            
            # Check network connectivity
            network_health = await self._check_network_health()
            health_status['network'] = network_health
            
            # Check system resources
            system_health = await self._check_system_health()
            health_status['system'] = system_health
            
            # Determine overall status
            health_status['overall_status'] = self._determine_overall_status(health_status)
            
            # Cache results
            self.health_cache = health_status
            self.last_health_check = time.time()
            
            return health_status
            
        except Exception as e:
            logger.error(f"Comprehensive health check failed: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'overall_status': 'unhealthy',
                'error': str(e)
            }
    
    async def _check_mining_health(self) -> Dict[str, Any]:
        """Check mining service health"""
        try:
            # Test mining service ping
            mining_ping = await self.mining_service.ping_mining_infrastructure()
            
            return {
                'status': 'healthy' if mining_ping.get('api_accessibility', {}).get('status') == 'accessible' else 'degraded',
                'api_accessibility': mining_ping.get('api_accessibility', {}),
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    async def _check_meshnet_health(self) -> Dict[str, Any]:
        """Check meshnet service health"""
        try:
            # Get meshnet status
            meshnet_status = await self.meshnet_service.get_mesh_network_health()
            
            return {
                'status': 'healthy' if meshnet_status.get('network_health') == 'healthy' else 'degraded',
                'network_health': meshnet_status.get('network_health'),
                'nodes': meshnet_status.get('total_nodes', 0),
                'active_nodes': meshnet_status.get('active_nodes', 0),
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    async def _check_network_health(self) -> Dict[str, Any]:
        """Check network connectivity"""
        try:
            # Test external connectivity
            connectivity_tests = [
                ('google.com', 80),
                ('supportxmr.com', 443),
                ('github.com', 443)
            ]
            
            results = {}
            for host, port in connectivity_tests:
                try:
                    # Use asyncio to test connectivity
                    future = asyncio.open_connection(host, port)
                    reader, writer = await asyncio.wait_for(future, timeout=5.0)
                    writer.close()
                    await writer.wait_closed()
                    results[host] = 'accessible'
                except Exception:
                    results[host] = 'unreachable'
            
            accessible_count = sum(1 for status in results.values() if status == 'accessible')
            total_tests = len(connectivity_tests)
            
            return {
                'status': 'healthy' if accessible_count == total_tests else 'degraded' if accessible_count > 0 else 'unhealthy',
                'connectivity_tests': results,
                'accessibility_rate': f"{accessible_count}/{total_tests}",
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """Check system resource health"""
        try:
            # Get basic system info
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'status': 'healthy',
                'cpu_usage': f"{cpu_percent}%",
                'memory_usage': f"{memory.percent}%",
                'disk_usage': f"{disk.percent}%",
                'available_memory': f"{memory.available / (1024**3):.1f}GB",
                'available_disk': f"{disk.free / (1024**3):.1f}GB",
                'last_check': datetime.now().isoformat()
            }
        except ImportError:
            # psutil not available, use basic checks
            return {
                'status': 'healthy',
                'note': 'Limited system monitoring (psutil not available)',
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'status': 'degraded',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    def _determine_overall_status(self, health_data: Dict[str, Any]) -> str:
        """Determine overall system health status"""
        try:
            service_statuses = []
            
            # Collect all service statuses
            for service_name, service_data in health_data.get('services', {}).items():
                service_statuses.append(service_data.get('status', 'unknown'))
            
            # Add network and system status
            service_statuses.append(health_data.get('network', {}).get('status', 'unknown'))
            service_statuses.append(health_data.get('system', {}).get('status', 'unknown'))
            
            # Determine overall status
            if all(status == 'healthy' for status in service_statuses):
                return 'healthy'
            elif any(status == 'unhealthy' for status in service_statuses):
                return 'unhealthy'
            else:
                return 'degraded'
                
        except Exception as e:
            logger.error(f"Error determining overall status: {e}")
            return 'unknown'
    
    async def get_simple_health(self) -> Dict[str, Any]:
        """Get simplified health status for quick checks"""
        try:
            # Quick health check without detailed analysis
            health_status = {
                'healthy': True,
                'status': 'operational',
                'timestamp': datetime.now().isoformat(),
                'services': {}
            }
            
            # Quick service checks
            if self.mining_service:
                try:
                    # Simple ping test
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                        async with session.get('https://supportxmr.com/api/pool/stats') as response:
                            if response.status == 200:
                                health_status['services']['mining'] = 'operational'
                            else:
                                health_status['services']['mining'] = 'degraded'
                                health_status['healthy'] = False
                except Exception:
                    health_status['services']['mining'] = 'unavailable'
                    health_status['healthy'] = False
            
            if self.meshnet_service:
                try:
                    # Check if meshnet service is responsive
                    meshnet_status = self.meshnet_service.get_mesh_network_status()
                    health_status['services']['meshnet'] = 'operational'
                except Exception:
                    health_status['services']['meshnet'] = 'degraded'
                    health_status['healthy'] = False
            
            # Update overall status
            if not health_status['healthy']:
                health_status['status'] = 'degraded'
            
            return health_status
            
        except Exception as e:
            logger.error(f"Simple health check failed: {e}")
            return {
                'healthy': False,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

