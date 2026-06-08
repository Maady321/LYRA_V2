import logging
import json
import redis.asyncio as redis
from typing import Dict, Any, Union
from core.streaming.schemas import TaskEvent, SystemEvent

logger = logging.getLogger("StreamProducer")

class StreamProducer:
    """
    Appends events to a durable Redis Stream.
    Messages persist until explicitly trimmed, enabling replays and DLQ mechanisms.
    """
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url, decode_responses=True)

    async def publish_task(self, stream_name: str, task_event: TaskEvent) -> str:
        """
        Publishes a task to a specific worker stream (e.g., 'stream:fury_tasks').
        Returns the unique stream ID (e.g., '1526919030474-55').
        """
        payload = {
            "task_id": task_event.task_id,
            "assignee": task_event.assignee,
            "goal": task_event.goal,
            "payload": json.dumps(task_event.payload),
            "sender": task_event.sender,
            "timestamp": task_event.timestamp,
            "retries": str(task_event.retries)
        }
        
        try:
            # XADD key ID field string [field string ...]
            # '*' auto-generates the ID based on current timestamp
            message_id = await self.redis.xadd(stream_name, payload, id="*")
            logger.info(f"Published Task {task_event.task_id} to {stream_name} with ID {message_id}")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish task to stream {stream_name}: {e}")
            raise

    async def publish_system_event(self, event: SystemEvent) -> str:
        payload = {
            "event_type": event.event_type,
            "details": json.dumps(event.details),
            "sender": event.sender,
            "timestamp": event.timestamp
        }
        try:
            message_id = await self.redis.xadd("stream:system_events", payload, id="*")
            return message_id
        except Exception as e:
            logger.error(f"Failed to publish system event: {e}")
            raise
            
    async def close(self):
        await self.redis.close()
