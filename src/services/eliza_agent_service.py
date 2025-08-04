
import asyncio
import logging

class ElizaAgentService:
    def __init__(self, mining_service, meshnet_service):
        self.logger = logging.getLogger(__name__)
        self.mining_service = mining_service
        self.meshnet_service = meshnet_service
        self.logger.info("Eliza Agent Service Initialized. Ready to receive commands.")

    async def process_command(self, command_text: str):
        """
        Processes a natural language command and routes it to the appropriate service.
        """
        command_text = command_text.lower().strip()
        self.logger.info(f"Processing command: '{command_text}'")

        if 'dashboard' in command_text or 'status' in command_text:
            self.logger.info("Command recognized: Fetching system dashboard.")
            return await self.mining_service.get_comprehensive_mining_dashboard()

        elif 'health' in command_text:
            self.logger.info("Command recognized: Performing health check.")
            mining_health = await self.mining_service.ping_mining_infrastructure()
            mesh_health = await self.meshnet_service.get_mesh_network_health()
            return {"mining_infrastructure": mining_health, "meshnet_infrastructure": mesh_health}

        elif 'nodes' in command_text:
            self.logger.info("Command recognized: Fetching MESHNET nodes.")
            return await self.meshnet_service.get_all_nodes()

        else:
            self.logger.warning(f"Unknown command: '{command_text}'")
            return {
                "response": "Command not recognized.",
                "available_commands": ["status", "dashboard", "health", "nodes"]
            }
