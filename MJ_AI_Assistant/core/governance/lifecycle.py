import asyncio
import logging
from sqlalchemy import select, update
from database.postgres_engine import get_pg_session
from database.models.governance import GovernanceRegistry, TrustRegistry, LifecycleState

logger = logging.getLogger("GovernanceLifecycle")

class AgentLifecycleEngine:
    """
    Background daemon that continuously monitors agent health and trust scores.
    Automatically suspends agents that fall below critical thresholds to protect the ecosystem.
    """
    def __init__(self):
        self.health_threshold = 60.0
        
    async def calculate_health_scores(self):
        """
        Recalculates health for all active agents based on recent success rates and security incidents.
        """
        async for session in get_pg_session():
            result = await session.execute(
                select(TrustRegistry, GovernanceRegistry)
                .join(GovernanceRegistry, TrustRegistry.agent_id == GovernanceRegistry.id)
                .where(GovernanceRegistry.state == LifecycleState.ACTIVE)
            )
            
            records = result.all()
            for trust, agent in records:
                # 1. Calculate Success Rate (Max 100)
                if trust.tasks_attempted == 0:
                    success_rate = 100.0
                else:
                    success_rate = (trust.tasks_succeeded / trust.tasks_attempted) * 100.0
                
                # 2. Calculate Penalty for Security Violations (e.g. Prompt Injections)
                # Severe penalty: -25 points per security violation
                security_penalty = trust.security_violations * 25.0
                
                # 3. Final Health Score (Weight: 50% Success Rate, 50% Trust Base - Penalties)
                raw_trust = max(0.0, trust.trust_score - security_penalty)
                
                new_health = (success_rate * 0.5) + (raw_trust * 0.5)
                new_health = max(0.0, min(new_health, 100.0))
                
                trust.health_score = new_health
                
                # 4. Suspension Logic
                if new_health < self.health_threshold:
                    logger.critical(f"Agent {agent.agent_name} health dropped to {new_health}. SUSPENDING.")
                    agent.state = LifecycleState.SUSPENDED
                    
            await session.commit()
            logger.info("Health scoring pass completed.")

    async def start_daemon(self):
        logger.info("Starting Agent Lifecycle Engine...")
        while True:
            try:
                await self.calculate_health_scores()
            except Exception as e:
                logger.error(f"Health scoring failed: {e}")
            
            # Run every 60 seconds
            await asyncio.sleep(60)
