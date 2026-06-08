import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional
import redis.asyncio as redis

logger = logging.getLogger("RedisBroker")

class Event:
    def __init__(self, channel: str, sender: str, data: Any, timestamp: str = None):
        self.channel = channel
        self.sender = sender
        self.data = data
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_json(self) -> str:
        return json.dumps({
            "channel": self.channel,
            "sender": self.sender,
            "data": self.data,
            "timestamp": self.timestamp
        })

    @classmethod
    def from_json(cls, payload: str) -> "Event":
        data = json.loads(payload)
        return cls(
            channel=data["channel"],
            sender=data["sender"],
            data=data["data"],
            timestamp=data["timestamp"]
        )

class Task:
    def __init__(self, task_id: str, goal: str, assigner: str, assignee: str, payload: Any, status: str = "PENDING"):
        self.task_id = task_id
        self.goal = goal
        self.assigner = assigner
        self.assignee = assignee
        self.payload = payload
        self.status = status
        self.result = None
        self.created_at = datetime.now().isoformat()
        
    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, payload: str) -> "Task":
        data = json.loads(payload)
        t = cls(
            task_id=data["task_id"],
            goal=data["goal"],
            assigner=data["assigner"],
            assignee=data["assignee"],
            payload=data["payload"],
            status=data["status"]
        )
        t.result = data.get("result")
        t.created_at = data.get("created_at", datetime.now().isoformat())
        return t

class RedisMessageBus:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self._listeners: Dict[str, List[Callable[[Event], Any]]] = {}
        self._task_handlers: Dict[str, Callable[[Task], Any]] = {}
        self._listen_task: Optional[asyncio.Task] = None

    async def connect(self):
        # Start background listener
        await self.pubsub.subscribe("system_events")
        self._listen_task = asyncio.create_task(self._listen_loop())
        logger.info(f"Connected to Redis at {self.redis_url}")

    async def _listen_loop(self):
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    channel = message["channel"]
                    payload = message["data"]
                    
                    if channel.startswith("task_dispatch:"):
                        await self._handle_task_dispatch(payload)
                    else:
                        await self._handle_event(channel, payload)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Redis listen loop error: {e}")

    async def _handle_event(self, channel: str, payload: str):
        try:
            event = Event.from_json(payload)
            if channel in self._listeners:
                await asyncio.gather(
                    *[self._execute_callback(cb, event) for cb in self._listeners[channel]],
                    return_exceptions=True
                )
        except Exception as e:
            logger.error(f"Error handling event on {channel}: {e}")

    async def _handle_task_dispatch(self, payload: str):
        try:
            task = Task.from_json(payload)
            agent_key = task.assignee.upper()
            if agent_key in self._task_handlers:
                handler = self._task_handlers[agent_key]
                try:
                    if asyncio.iscoroutinefunction(handler):
                        result = await handler(task)
                    else:
                        result = await asyncio.to_thread(handler, task)
                    
                    task.status = "COMPLETED"
                    task.result = result
                except Exception as e:
                    task.status = "FAILED"
                    task.result = f"Error: {e}"
                
                # Publish completion back to a result channel
                await self.redis.publish(f"task_result:{task.task_id}", task.to_json())
        except Exception as e:
            logger.error(f"Error handling task dispatch: {e}")

    async def _execute_callback(self, cb: Callable, event: Event):
        if asyncio.iscoroutinefunction(cb):
            await cb(event)
        else:
            await asyncio.to_thread(cb, event)

    async def subscribe(self, channel: str, callback: Callable[[Event], Any]) -> None:
        if channel not in self._listeners:
            self._listeners[channel] = []
            await self.pubsub.subscribe(channel)
        self._listeners[channel].append(callback)

    async def emit(self, channel: str, sender: str, data: Any) -> None:
        event = Event(channel, sender, data)
        await self.redis.publish(channel, event.to_json())

    async def register_task_handler(self, agent_name: str, handler: Callable[[Task], Any]) -> None:
        self._task_handlers[agent_name.upper()] = handler
        await self.pubsub.subscribe(f"task_dispatch:{agent_name.upper()}")

    async def dispatch_task(self, task: Task) -> Optional[Any]:
        # Publish task to the specific agent queue
        agent_key = task.assignee.upper()
        # Create a pubsub listener for the result
        result_pubsub = self.redis.pubsub()
        await result_pubsub.subscribe(f"task_result:{task.task_id}")
        
        await self.redis.publish(f"task_dispatch:{agent_key}", task.to_json())
        
        # Wait for result with a timeout
        try:
            async with asyncio.timeout(300.0): # 5 min timeout
                async for message in result_pubsub.listen():
                    if message["type"] == "message":
                        completed_task = Task.from_json(message["data"])
                        await result_pubsub.unsubscribe()
                        return completed_task.result
        except asyncio.TimeoutError:
            await result_pubsub.unsubscribe()
            return f"Error: Task {task.task_id} timed out waiting for {agent_key}"

    async def close(self):
        if self._listen_task:
            self._listen_task.cancel()
        await self.pubsub.close()
        await self.redis.close()
