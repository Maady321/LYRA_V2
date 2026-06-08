import asyncio
import json
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional
from memory.sqlite_db import SQLiteDB
from core.negotiation import PeerNegotiationBroker

class Event:
    def __init__(self, channel: str, sender: str, data: Any):
        self.channel = channel
        self.sender = sender
        self.data = data
        self.timestamp = datetime.now().isoformat()

    def to_json(self) -> str:
        return json.dumps({
            "channel": self.channel,
            "sender": self.sender,
            "data": self.data,
            "timestamp": self.timestamp
        })


class Task:
    def __init__(self, task_id: str, goal: str, assigner: str, assignee: str, payload: Any):
        self.task_id = task_id
        self.goal = goal
        self.assigner = assigner
        self.assignee = assignee
        self.payload = payload
        self.status = "PENDING"  # 'PENDING', 'RUNNING', 'COMPLETED', 'FAILED'
        self.result = None
        self.created_at = datetime.now().isoformat()


class MessageBus:
    def __init__(self, db: SQLiteDB):
        self.db = db
        self._listeners: Dict[str, List[Callable[[Event], Any]]] = {}
        self._agent_task_handlers: Dict[str, Callable[[Task], Any]] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.active_agents: Dict[str, str] = {
            "FURY": "ONLINE",
            "VISION": "ONLINE",
            "CAPTAIN": "ONLINE",
            "BANNER": "ONLINE",
            "STARK": "ONLINE",
            "JARVIS": "ONLINE",
            "SPIDEY": "ONLINE"
        }
        self.current_active_agent: str = "FURY"
        self.last_completed_task: str = "None"
        self.tasks_today: int = 0
        self.negotiator = PeerNegotiationBroker(self, db.db_path)

    # --- PubSub Event Management ---
    def subscribe(self, channel: str, callback: Callable[[Event], Any]) -> None:
        if channel not in self._listeners:
            self._listeners[channel] = []
        self._listeners[channel].append(callback)

    async def emit(self, channel: str, sender: str, data: Any) -> None:
        event = Event(channel, sender, data)
        self.db.log_agent_activity(
            agent_name=sender,
            action=f"Published event on channel: {channel}",
            status="SUCCESS",
            metrics={"data": data}
        )
        if channel in self._listeners:
            # Dispatch to listeners concurrently
            await asyncio.gather(
                *[asyncio.to_thread(cb, event) for cb in self._listeners[channel]],
                return_exceptions=True
            )

    # --- Point-to-Point Agent Task Routing ---
    def register_task_handler(self, agent_name: str, handler: Callable[[Task], Any]) -> None:
        self._agent_task_handlers[agent_name.upper()] = handler
        self.active_agents[agent_name.upper()] = "ONLINE"

    async def dispatch_task(self, task: Task) -> Optional[Any]:
        agent_key = task.assignee.upper()
        if agent_key not in self._agent_task_handlers:
            task.status = "FAILED"
            task.result = f"Error: Agent '{agent_key}' is offline or not registered."
            return task.result

        # Update stats
        self.current_active_agent = agent_key
        task.status = "RUNNING"
        self.active_agents[agent_key] = "BUSY"

        try:
            handler = self._agent_task_handlers[agent_key]
            # Execute agent logic in safe thread/async task
            if asyncio.iscoroutinefunction(handler):
                result = await handler(task)
            else:
                result = await asyncio.to_thread(handler, task)

            task.status = "COMPLETED"
            task.result = result
            self.last_completed_task = task.goal
            self.tasks_today += 1
            
            # Log successful database entry
            self.db.log_agent_activity(
                agent_name=agent_key,
                action=f"Completed Task: {task.goal}",
                status="SUCCESS",
                metrics={"result": str(result)[:300]}
            )
            return result
        except Exception as e:
            task.status = "FAILED"
            task.result = f"Error: {e}"
            self.db.log_agent_activity(
                agent_name=agent_key,
                action=f"Failed Task: {task.goal}",
                status="FAILED",
                metrics={"error": str(e)}
            )
            return task.result
        finally:
            self.active_agents[agent_key] = "ONLINE"
            self.current_active_agent = "FURY"
