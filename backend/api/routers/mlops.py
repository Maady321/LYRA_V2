from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from typing import List, Optional

from database.postgres_engine import get_pg_session
from database.models.mlops import PromptRegistry, DeploymentStatus

router = APIRouter(prefix="/mlops", tags=["MLOps"])

class PromptCreate(BaseModel):
    agent_type: str
    version: str
    system_prompt: str
    traffic_weight: int = 100

class ABTestRequest(BaseModel):
    agent_type: str
    prompt_id_a: str
    prompt_id_b: str
    weight_a: int = 50
    weight_b: int = 50

@router.post("/prompts/")
async def create_prompt(prompt: PromptCreate, session: AsyncSession = Depends(get_pg_session)):
    new_prompt = PromptRegistry(
        agent_type=prompt.agent_type,
        version=prompt.version,
        system_prompt=prompt.system_prompt,
        traffic_weight=prompt.traffic_weight,
        status=DeploymentStatus.STAGING
    )
    session.add(new_prompt)
    await session.commit()
    return {"message": "Prompt created successfully", "id": new_prompt.id}

@router.post("/ab-test/")
async def initialize_ab_test(req: ABTestRequest, session: AsyncSession = Depends(get_pg_session)):
    if req.weight_a + req.weight_b != 100:
        raise HTTPException(status_code=400, detail="Weights must sum to 100")
        
    # Set weights
    await session.execute(update(PromptRegistry).where(PromptRegistry.id == req.prompt_id_a).values(traffic_weight=req.weight_a, status=DeploymentStatus.PRODUCTION))
    await session.execute(update(PromptRegistry).where(PromptRegistry.id == req.prompt_id_b).values(traffic_weight=req.weight_b, status=DeploymentStatus.PRODUCTION))
    
    # Set all others for this agent type to 0 weight and archived
    await session.execute(
        update(PromptRegistry)
        .where(PromptRegistry.agent_type == req.agent_type)
        .where(PromptRegistry.id.notin_([req.prompt_id_a, req.prompt_id_b]))
        .values(traffic_weight=0, status=DeploymentStatus.ARCHIVED)
    )
    
    await session.commit()
    return {"message": f"A/B test initialized for {req.agent_type}"}

@router.post("/rollbacks/{prompt_id}")
async def rollback_prompt(prompt_id: str, session: AsyncSession = Depends(get_pg_session)):
    # Find prompt
    res = await session.execute(select(PromptRegistry).where(PromptRegistry.id == prompt_id))
    prompt = res.scalar_one_or_none()
    if not prompt: raise HTTPException(404)
    
    # Demote this prompt
    prompt.status = DeploymentStatus.ROLLED_BACK
    prompt.traffic_weight = 0
    
    # Find previous stable version
    prev_res = await session.execute(
        select(PromptRegistry)
        .where(PromptRegistry.agent_type == prompt.agent_type)
        .where(PromptRegistry.status == DeploymentStatus.ARCHIVED)
        .order_by(PromptRegistry.created_at.desc())
        .limit(1)
    )
    prev = prev_res.scalar_one_or_none()
    if prev:
        prev.status = DeploymentStatus.PRODUCTION
        prev.traffic_weight = 100
        
    await session.commit()
    return {"message": "Rollback successful."}
