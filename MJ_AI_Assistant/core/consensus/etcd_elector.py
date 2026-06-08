import asyncio
import logging
import uuid
import aetcd
from typing import Optional, Callable, Awaitable

logger = logging.getLogger("EtcdElector")

class EtcdLeaderElection:
    """
    Implements strict Raft-based Leader Election using etcd.
    Ensures that split-brain is mathematically impossible due to Quorum requirements.
    """
    def __init__(self, etcd_host: str = "localhost", etcd_port: int = 2379, election_name: str = "lyra-fury-leader", node_id: str = None):
        self.etcd_host = etcd_host
        self.etcd_port = etcd_port
        self.election_name = election_name
        self.node_id = node_id or str(uuid.uuid4())
        self.lease_ttl = 5  # seconds
        
        self.client: Optional[aetcd.Client] = None
        self.lease: Optional[aetcd.Lease] = None
        self.is_leader = False
        
        self._election_task: Optional[asyncio.Task] = None
        self._on_promotion: Optional[Callable[[], Awaitable[None]]] = None
        self._on_demotion: Optional[Callable[[], Awaitable[None]]] = None

    def on_promotion(self, callback: Callable[[], Awaitable[None]]):
        self._on_promotion = callback

    def on_demotion(self, callback: Callable[[], Awaitable[None]]):
        self._on_demotion = callback

    async def connect(self):
        self.client = aetcd.Client(host=self.etcd_host, port=self.etcd_port)
        logger.info(f"Connected to etcd cluster at {self.etcd_host}:{self.etcd_port}")

    async def start(self):
        if not self.client:
            await self.connect()
            
        if self._election_task is None:
            self._election_task = asyncio.create_task(self._campaign_loop())
            logger.info(f"Node {self.node_id} started etcd Raft campaign for '{self.election_name}'")

    async def _campaign_loop(self):
        try:
            while True:
                # Create a lease
                self.lease = await self.client.lease(self.lease_ttl)
                
                logger.info(f"Node {self.node_id} campaigning for leadership...")
                
                try:
                    # Campaign for the leader key. This call BLOCKS until this node becomes the leader.
                    # Under the hood, etcd creates a sequential key. The lowest sequence wins.
                    # Other nodes block here, waiting for the current leader's lease to expire.
                    election = self.client.election(self.election_name)
                    async with election.campaign(self.node_id, lease=self.lease):
                        # We won the election!
                        self.is_leader = True
                        logger.info(f"🏆 Node {self.node_id} promoted to LEADER by Raft Quorum!")
                        
                        if self._on_promotion:
                            await self._on_promotion()
                            
                        # Maintain leadership by refreshing the lease
                        try:
                            # Keep alive blocks until lease is revoked or connection lost
                            async for _ in self.client.keep_alive(self.lease):
                                # Heartbeat successful
                                pass
                        except Exception as e:
                            logger.error(f"Lost etcd heartbeat / Quorum: {e}")
                        finally:
                            # We lost the lease / connection / quorum
                            if self.is_leader:
                                logger.warning(f"⚠️ Node {self.node_id} lost Quorum. Demoted to FOLLOWER.")
                                self.is_leader = False
                                if self._on_demotion:
                                    await self._on_demotion()
                                    
                except Exception as e:
                    logger.error(f"Campaign error: {e}")
                    
                # If we exit the campaign (error or lost lease), sleep briefly before retrying
                await asyncio.sleep(2)

        except asyncio.CancelledError:
            logger.info(f"Election task for {self.node_id} cancelled.")
            if self.is_leader and self._on_demotion:
                await self._on_demotion()
            self.is_leader = False

    async def stop(self):
        if self._election_task:
            self._election_task.cancel()
            self._election_task = None
            
        if self.client:
            if self.lease and self.is_leader:
                # Resign leadership by revoking lease
                await self.client.revoke_lease(self.lease.id)
            await self.client.close()
        logger.info(f"Node {self.node_id} stepped down and closed etcd connection.")
