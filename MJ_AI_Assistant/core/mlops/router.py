import logging
import random
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Tuple

from database.postgres_engine import get_pg_session
from database.models.mlops import PromptRegistry, DeploymentStatus

logger = logging.getLogger("MLOpsRouter")

class MLOpsRouter:
    """
    Dynamically routes LLM requests based on A/B testing configurations 
    and handles automatic model selection.
    """
    def __init__(self):
        pass

    async def get_prompt_for_agent(self, agent_type: str) -> Tuple[str, str]:
        """
        Retrieves the active system prompt for an agent type.
        Handles A/B testing traffic splits (e.g., 80% weight to Prompt A, 20% to Prompt B).
        Returns: (prompt_id, system_prompt_text)
        """
        async for session in get_pg_session():
            result = await session.execute(
                select(PromptRegistry)
                .where(PromptRegistry.agent_type == agent_type)
                .where(PromptRegistry.status == DeploymentStatus.PRODUCTION)
                .where(PromptRegistry.traffic_weight > 0)
            )
            prompts = result.scalars().all()
            
            if not prompts:
                logger.warning(f"No PRODUCTION prompt found for {agent_type}. Using fallback.")
                return ("fallback_id", f"You are {agent_type}.")

            if len(prompts) == 1:
                return (prompts[0].id, prompts[0].system_prompt)

            # A/B Testing Logic: Weighted Random Choice
            weights = [p.traffic_weight for p in prompts]
            chosen_prompt = random.choices(prompts, weights=weights, k=1)[0]
            
            logger.info(f"[A/B Test Routing] Routed {agent_type} request to Prompt Version: {chosen_prompt.version} (Weight: {chosen_prompt.traffic_weight}%)")
            
            return (chosen_prompt.id, chosen_prompt.system_prompt)

    async def select_optimal_model(self, task_complexity_score: float) -> str:
        """
        Automatic Model Selection based on task complexity.
        This allows Lyra to save compute costs on simple tasks by routing to smaller models,
        while using heavy models (like Llama-3-70B) for complex logic.
        """
        # In a real system, this queries the EvaluationMetrics table.
        # For now, simplistic heuristic routing.
        if task_complexity_score > 0.8:
            logger.info("Task complexity is HIGH. Routing to llama3:70b-instruct.")
            return "llama3:70b-instruct"
        elif task_complexity_score > 0.4:
            logger.info("Task complexity is MEDIUM. Routing to llama3:8b-instruct.")
            return "llama3:8b-instruct"
        else:
            logger.info("Task complexity is LOW. Routing to phi3:mini.")
            return "phi3:mini"
