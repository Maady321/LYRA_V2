import asyncio
import sqlite3
from typing import Dict, List, Any, Optional
from MJ_AI_Assistant.security.guardian import guardian_kernel

class PeerNegotiationBroker:
    def __init__(self, bus, db_path: str):
        self.bus = bus
        self.db_path = db_path
        try:
            self.loop = asyncio.get_event_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
        self.bids: Dict[str, List[Dict[str, Any]]] = {}
        
        # Subscribe to channels
        self.bus.subscribe("task_negotiation_channel", self._handle_negotiation_request_sync)
        self.bus.subscribe("task_bids_channel", self._handle_bid_response_sync)

    def _handle_negotiation_request_sync(self, event):
        """
        Synchronous callback wrapper for the message bus thread executor.
        """
        asyncio.run_coroutine_threadsafe(self._handle_negotiation_request(event), self.loop)

    def _handle_bid_response_sync(self, event):
        """
        Synchronous callback wrapper for the message bus thread executor.
        """
        asyncio.run_coroutine_threadsafe(self._handle_bid_response(event), self.loop)

    async def _handle_negotiation_request(self, event):
        """
        Processes negotiation requests, queries database for agents with matching capabilities,
        and emits bid events on the task_bids_channel.
        """
        data = event.data
        if not isinstance(data, dict):
            return
        
        task_id = data.get("task_id")
        required_capability = data.get("required_capability")
        if not task_id or not required_capability:
            return

        matching_agents = []
        try:
            guardian_kernel.authorize_execution(agent_name="negotiation", action="db_access", target="sqlite3")
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT ar.agent_name, ar.trust_level
                    FROM agent_roles ar
                    JOIN agent_capabilities ac ON ar.agent_name = ac.agent_name
                    WHERE ac.capability_type = ?
                    """,
                    (required_capability,)
                )
                rows = cursor.fetchall()
                matching_agents = [(row["agent_name"], row["trust_level"]) for row in rows]
        except Exception as e:
            return

        for agent_name, trust_level in matching_agents:
            status = self.bus.active_agents.get(agent_name, "OFFLINE")
            if status == "OFFLINE":
                continue
            
            # Status multiplier: ONLINE = 1.0, BUSY = 0.5
            multiplier = 1.0 if status == "ONLINE" else 0.5
            bid_score = float(trust_level * multiplier)
            
            bid_data = {
                "task_id": task_id,
                "agent_name": agent_name,
                "bid_score": bid_score
            }
            await self.bus.emit("task_bids_channel", agent_name, bid_data)

    async def _handle_bid_response(self, event):
        """
        Collects bid responses for active negotiations.
        """
        data = event.data
        if not isinstance(data, dict):
            return
        
        task_id = data.get("task_id")
        agent_name = data.get("agent_name")
        bid_score = data.get("bid_score")
        
        if task_id and agent_name and bid_score is not None:
            if task_id in self.bids:
                self.bids[task_id].append({
                    "agent_name": agent_name,
                    "bid_score": bid_score
                })

    async def negotiate_best_agent(self, task_id: str, subtask_title: str, required_capability: str) -> str:
        """
        Emits a task negotiation request on task_negotiation_channel,
        waits 0.4s for bids to arrive, and selects the agent with the highest bid score.
        If no bids arrive, falls back or raises RuntimeError.
        """
        self.bids[task_id] = []
        
        request_data = {
            "task_id": task_id,
            "subtask_title": subtask_title,
            "required_capability": required_capability
        }
        
        await self.bus.emit("task_negotiation_channel", "FURY", request_data)
        
        # Wait for bids to collect
        await asyncio.sleep(0.4)
        
        collected_bids = self.bids.pop(task_id, [])
        if not collected_bids:
            raise RuntimeError(f"No active bids received for capability: {required_capability}")
            
        # Select best agent (highest bid score)
        best_bid = max(collected_bids, key=lambda x: (x["bid_score"], x["agent_name"]))
        return best_bid["agent_name"]
