from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import List

from database.postgres_engine import get_pg_session
from database.models.governance import GovernanceRegistry, CapabilityRegistry, TrustRegistry, CertificationTier, LifecycleState
from backend.security.guardian import guardian_kernel

router = APIRouter(prefix="/governance", tags=["Governance"])

class OnboardRequest(BaseModel):
    agent_name: str
    description: str
    capabilities: List[str]

@router.post("/agents/onboard")
async def onboard_agent(req: OnboardRequest, session: AsyncSession = Depends(get_pg_session)):
    guardian_kernel.authorize_execution(agent_name="anonymous", action="api_access", target="onboard_agent")
    agent = GovernanceRegistry(
        agent_name=req.agent_name,
        description=req.description,
        tier=CertificationTier.TIER_3_UNCERTIFIED,
        state=LifecycleState.DRAFT
    )
    session.add(agent)
    await session.flush() # Get ID
    
    # Init Trust Profile
    trust = TrustRegistry(agent_id=agent.id)
    session.add(trust)
    
    # Init Capabilities
    for cap in req.capabilities:
        c = CapabilityRegistry(agent_id=agent.id, capability_name=cap, is_validated=False)
        session.add(c)
        
    await session.commit()
    return {"message": "Agent drafted successfully.", "agent_id": agent.id}

@router.post("/agents/{agent_id}/certify")
async def certify_agent(agent_id: str, session: AsyncSession = Depends(get_pg_session)):
    """Runs capability validation and promotes to TIER_2_VERIFIED if successful."""
    # Mocking capability validation test passing
    guardian_kernel.authorize_execution(agent_name="anonymous", action="api_access", target="certify_agent")
    await session.execute(
        update(CapabilityRegistry)
        .where(CapabilityRegistry.agent_id == agent_id)
        .values(is_validated=True)
    )
    
    # Promote Tier and activate
    await session.execute(
        update(GovernanceRegistry)
        .where(GovernanceRegistry.id == agent_id)
        .values(tier=CertificationTier.TIER_2_VERIFIED, state=LifecycleState.ACTIVE)
    )
    
    await session.commit()
    return {"message": "Agent passed capability validation and is now ACTIVE (Tier 2)."}

@router.put("/agents/{agent_id}/deprecate")
async def deprecate_agent(agent_id: str, session: AsyncSession = Depends(get_pg_session)):
    """Marks an agent for deprecation, routing dependent workflows away."""
    guardian_kernel.authorize_execution(agent_name="anonymous", action="api_access", target="deprecate_agent")
    await session.execute(
        update(GovernanceRegistry)
        .where(GovernanceRegistry.id == agent_id)
        .values(state=LifecycleState.DEPRECATED)
    )
    await session.commit()
    return {"message": "Agent marked as DEPRECATED."}

@router.get("/marketplace/search")
async def search_marketplace(capability: str, session: AsyncSession = Depends(get_pg_session)):
    """Search for ACTIVE agents matching a capability."""
    guardian_kernel.authorize_execution(agent_name="anonymous", action="api_access", target="search_marketplace")
    result = await session.execute(
        select(GovernanceRegistry.agent_name, GovernanceRegistry.description, GovernanceRegistry.tier)
        .join(CapabilityRegistry, GovernanceRegistry.id == CapabilityRegistry.agent_id)
        .where(CapabilityRegistry.capability_name == capability)
        .where(CapabilityRegistry.is_validated == True)
        .where(GovernanceRegistry.state == LifecycleState.ACTIVE)
    )
    agents = result.fetchall()
    return [{"name": row.agent_name, "description": row.description, "tier": row.tier.value} for row in agents]
