import asyncio
import logging
import json
from typing import Callable, Dict, Any, Optional
import redis.asyncio as redis
from redis.exceptions import ResponseError
from core.streaming.schemas import TaskEvent

logger = logging.getLogger("StreamConsumer")

class StreamConsumer:
    """
    Reads from a Redis Stream using Consumer Groups.
    Ensures horizontal load balancing (messages are delivered to exactly one consumer).
    Requires explicit ACKs after successful processing to prevent message loss.
    """
    def __init__(self, stream_name: str, group_name: str, consumer_name: str, redis_url: str = "redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.stream_name = stream_name
        self.group_name = group_name
        self.consumer_name = consumer_name
        self._listen_task: Optional[asyncio.Task] = None
        self._handler: Optional[Callable[[TaskEvent], Any]] = None

    async def initialize_group(self):
        """Creates the consumer group if it doesn't exist."""
        try:
            # Create stream and group, '$' means only read NEW messages arriving after creation
            # MKSTREAM automatically creates the stream if it doesn't exist
            await self.redis.xgroup_create(self.stream_name, self.group_name, id="$", mkstream=True)
            logger.info(f"Created consumer group {self.group_name} on {self.stream_name}")
        except ResponseError as e:
            if "BUSYGROUP Consumer Group name already exists" in str(e):
                pass # Expected if already initialized
            else:
                logger.error(f"Error creating group: {e}")
                raise

    def set_handler(self, handler: Callable[[TaskEvent], Any]):
        self._handler = handler

    async def start(self):
        await self.initialize_group()
        if not self._handler:
            raise ValueError("Handler not set. Call set_handler() first.")
            
        self._listen_task = asyncio.create_task(self._listen_loop())
        logger.info(f"Consumer {self.consumer_name} listening to {self.stream_name} via group {self.group_name}")

    async def _listen_loop(self):
        try:
            while True:
                # Block for up to 2 seconds waiting for new messages ('>' means undelivered messages)
                messages = await self.redis.xreadgroup(
                    groupname=self.group_name,
                    consumername=self.consumer_name,
                    streams={self.stream_name: ">"},
                    count=1,
                    block=2000
                )
                
                if messages:
                    for stream, msg_list in messages:
                        for msg_id, payload in msg_list:
                            await self._process_message(msg_id, payload)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Consumer loop error: {e}")
            await asyncio.sleep(2) # Backoff before retrying

    async def _process_message(self, msg_id: str, payload: Dict[str, Any]):
        try:
            # Parse payload
            payload["payload"] = json.loads(payload.get("payload", "{}"))
            task_event = TaskEvent(**payload)
            
            logger.info(f"Processing message {msg_id} (Task: {task_event.task_id})")
            
            # Execute handler
            if asyncio.iscoroutinefunction(self._handler):
                await self._handler(task_event)
            else:
                await asyncio.to_thread(self._handler, task_event)
                
            # If successful, ACK the message to remove it from the Pending Entries List (PEL)
            await self.redis.xack(self.stream_name, self.group_name, msg_id)
            logger.info(f"ACKed message {msg_id}")
            
        except Exception as e:
            logger.error(f"Failed to process message {msg_id}: {e}")
            # Do NOT ACK. The RetryManager will detect it in the PEL.

    async def close(self):
        if self._listen_task:
            self._listen_task.cancel()
        await self.redis.close()
