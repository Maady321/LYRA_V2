import asyncio
import logging
import json
import redis.asyncio as redis
from typing import Dict, Any

logger = logging.getLogger("RetryManager")

class RetryManager:
    """
    Monitors the Pending Entries List (PEL) for unacknowledged messages.
    If a consumer crashes mid-processing, this manager will XCLAIM the message
    and either re-queue it or route it to a Dead Letter Queue (DLQ) if max retries are exceeded.
    """
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.idle_time_ms = 30000  # 30 seconds before a message is considered orphaned
        self.max_retries = 3

    async def run_maintenance(self, stream_name: str, group_name: str, consumer_name: str = "retry_daemon"):
        """Runs a single pass of PEL maintenance."""
        try:
            # 1. Find pending messages idle for more than idle_time_ms
            # XPENDING stream group - + 100
            pending_info = await self.redis.xpending_range(
                stream_name, group_name, min="-", max="+", count=100
            )

            for msg in pending_info:
                msg_id = msg['message_id']
                idle_time = msg['time_since_delivered']
                delivery_count = msg['deliveries']
                
                if idle_time >= self.idle_time_ms:
                    logger.warning(f"Message {msg_id} in {stream_name} has been idle for {idle_time}ms (Deliveries: {delivery_count})")
                    
                    if delivery_count > self.max_retries:
                        await self._route_to_dlq(stream_name, group_name, msg_id)
                    else:
                        await self._reclaim_message(stream_name, group_name, consumer_name, msg_id)

        except Exception as e:
            logger.error(f"Retry maintenance failed for {stream_name}: {e}")

    async def _route_to_dlq(self, stream_name: str, group_name: str, msg_id: str):
        logger.error(f"Message {msg_id} exceeded max retries. Routing to DLQ.")
        
        # Read the exact message content
        msgs = await self.redis.xrange(stream_name, min=msg_id, max=msg_id, count=1)
        if msgs:
            _, payload = msgs[0]
            # Add metadata
            payload["original_stream"] = stream_name
            payload["dlq_reason"] = "max_retries_exceeded"
            
            # Send to DLQ
            await self.redis.xadd("stream:dlq", payload)
            
            # ACK from original stream to clear PEL
            await self.redis.xack(stream_name, group_name, msg_id)

    async def _reclaim_message(self, stream_name: str, group_name: str, consumer_name: str, msg_id: str):
        logger.info(f"Reclaiming message {msg_id} for {consumer_name}")
        # XCLAIM transfers ownership of the message in the PEL to the new consumer
        claimed_msgs = await self.redis.xclaim(
            stream_name, 
            group_name, 
            consumer_name, 
            min_idle_time=self.idle_time_ms, 
            message_ids=[msg_id]
        )
        
        if claimed_msgs:
            # Re-publish it or process it.
            # Easiest way to "re-queue" for another worker to pick up normally via XREADGROUP
            # is to append it as a NEW message, and ACK the old one.
            _, payload = claimed_msgs[0]
            
            # Increment retries counter in payload
            retries = int(payload.get("retries", 0)) + 1
            payload["retries"] = str(retries)
            
            await self.redis.xadd(stream_name, payload)
            await self.redis.xack(stream_name, group_name, msg_id)
            logger.info(f"Message {msg_id} re-queued as a new entry with retry count {retries}")

    async def start_daemon(self, stream_names: list, group_name: str):
        logger.info("Starting Retry Manager Daemon...")
        while True:
            for stream in stream_names:
                await self.run_maintenance(stream, group_name)
            await asyncio.sleep(10) # Run check every 10 seconds

    async def close(self):
        await self.redis.close()
