import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
import redis.asyncio as redis

logger = logging.getLogger("AgentRegistry")

class AgentRegistry:
    """
    Distributed Agent Registry using Redis for auto-discovery and heartbeat tracking.
    """
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.prefix = "lyra:agent:"
        self.heartbeat_interval = 10 # seconds
        self._heartbeat_tasks: Dict[str, asyncio.Task] = {}

    async def register(self, agent_name: str, node_id: str, capabilities: List[str]):
        """Register an agent with a TTL-based key (heartbeat)."""
        key = f"{self.prefix}{agent_name.upper()}:{node_id}"
        data = {
            "node_id": node_id,
            "agent_name": agent_name.upper(),
            "capabilities": capabilities,
            "status": "ONLINE"
        }
        await self.redis.set(key, json.dumps(data), ex=self.heartbeat_interval + 5)
        logger.info(f"Registered agent {agent_name} at node {node_id}")

    async def update_status(self, agent_name: str, node_id: str, status: str):
        """Update the status of a specific agent node (ONLINE, BUSY)."""
        key = f"{self.prefix}{agent_name.upper()}:{node_id}"
        val = await self.redis.get(key)
        if val:
            data = json.loads(val)
            data["status"] = status
            await self.redis.set(key, json.dumps(data), ex=self.heartbeat_interval + 5)

    async def start_heartbeat(self, agent_name: str, node_id: str, capabilities: List[str]):
        """Start a background task to periodically refresh the TTL."""
        task_id = f"{agent_name}:{node_id}"
        if task_id in self._heartbeat_tasks:
            return

        async def heartbeat_loop():
            try:
                while True:
                    await self.register(agent_name, node_id, capabilities)
                    await asyncio.sleep(self.heartbeat_interval)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Heartbeat loop error for {task_id}: {e}")
        
        self._heartbeat_tasks[task_id] = asyncio.create_task(heartbeat_loop())

    async def stop_heartbeat(self, agent_name: str, node_id: str):
        task_id = f"{agent_name}:{node_id}"
        if task_id in self._heartbeat_tasks:
            self._heartbeat_tasks[task_id].cancel()
            del self._heartbeat_tasks[task_id]
        
        # Explicitly delete the key so it immediately unregisters
        key = f"{self.prefix}{agent_name.upper()}:{node_id}"
        await self.redis.delete(key)

    async def get_active_agents(self) -> List[Dict[str, Any]]:
        """Find all active agents by scanning keys."""
        agents = []
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor, match=f"{self.prefix}*")
            if keys:
                values = await self.redis.mget(keys)
                for val in values:
                    if val:
                        agents.append(json.loads(val))
            if cursor == 0:
                break
        return agents

    async def get_agents_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        agents = await self.get_active_agents()
        return [a for a in agents if capability in a.get("capabilities", [])]

    async def close(self):
        for task in self._heartbeat_tasks.values():
            task.cancel()
        await self.redis.close()
