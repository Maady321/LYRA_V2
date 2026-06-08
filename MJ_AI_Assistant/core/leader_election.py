import asyncio
import logging
import uuid
from typing import Optional, Callable, Awaitable
import redis.asyncio as redis

logger = logging.getLogger("LeaderElection")

class RedisLeaderElection:
    """
    Implements a simple Redlock-style distributed lock for Leader Election among multiple FURY instances.
    Ensures that only one FURY node acts as the active coordinator at any time.
    """
    def __init__(self, redis_url: str = "redis://localhost:6379/0", lock_name: str = "lyra:leader:fury", node_id: str = None):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.lock_name = lock_name
        self.node_id = node_id or str(uuid.uuid4())
        self.lock_ttl = 10  # seconds
        self.is_leader = False
        self._election_task: Optional[asyncio.Task] = None
        self._on_promotion: Optional[Callable[[], Awaitable[None]]] = None
        self._on_demotion: Optional[Callable[[], Awaitable[None]]] = None

    def on_promotion(self, callback: Callable[[], Awaitable[None]]):
        self._on_promotion = callback

    def on_demotion(self, callback: Callable[[], Awaitable[None]]):
        self._on_demotion = callback

    async def start(self):
        if self._election_task is None:
            self._election_task = asyncio.create_task(self._election_loop())
            logger.info(f"Node {self.node_id} started participating in leader election for '{self.lock_name}'")

    async def _election_loop(self):
        try:
            while True:
                # Try to acquire the lock
                # SET key value NX PX ttl
                acquired = await self.redis.set(
                    self.lock_name, 
                    self.node_id, 
                    nx=True, 
                    px=self.lock_ttl * 1000
                )

                if acquired:
                    if not self.is_leader:
                        logger.info(f"🏆 Node {self.node_id} promoted to LEADER!")
                        self.is_leader = True
                        if self._on_promotion:
                            await self._on_promotion()
                    
                    # Already leader, sleep half the TTL to renew
                    await asyncio.sleep(self.lock_ttl / 2)
                    
                    # Renew lock
                    current_owner = await self.redis.get(self.lock_name)
                    if current_owner == self.node_id:
                        await self.redis.pexpire(self.lock_name, self.lock_ttl * 1000)
                    else:
                        # Lock was lost (e.g. GC pause caused expiration)
                        if self.is_leader:
                            logger.warning(f"⚠️ Node {self.node_id} lost LEADER lock!")
                            self.is_leader = False
                            if self._on_demotion:
                                await self._on_demotion()
                else:
                    if self.is_leader:
                        logger.warning(f"⚠️ Node {self.node_id} demoted to FOLLOWER.")
                        self.is_leader = False
                        if self._on_demotion:
                            await self._on_demotion()
                    
                    # Wait and try again
                    await asyncio.sleep(self.lock_ttl / 2)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Election loop error on node {self.node_id}: {e}")
            self.is_leader = False
            await asyncio.sleep(2)

    async def stop(self):
        if self._election_task:
            self._election_task.cancel()
            self._election_task = None
        
        # If leader, release the lock gracefully
        if self.is_leader:
            current_owner = await self.redis.get(self.lock_name)
            if current_owner == self.node_id:
                await self.redis.delete(self.lock_name)
            self.is_leader = False
            logger.info(f"Node {self.node_id} released leader lock and stepped down.")
        
        await self.redis.close()
