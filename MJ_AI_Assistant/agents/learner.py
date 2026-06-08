import logging
import asyncio
import json
from typing import Dict, Any, List
from core.redis_broker import RedisMessageBus, Task
from memory.neo4j_engine import Neo4jEngine
from core.ollama_client import OllamaClient
from database.postgres_engine import get_pg_session
from sqlalchemy import text
import uuid

logger = logging.getLogger("LEARNER_V2")

class LearnerAgentV2:
    """
    Enterprise Self-Improving AI Pipeline.
    Implements Reflection -> Validation -> Scoring -> Approval -> Rollback
    """
    def __init__(self, bus: RedisMessageBus, graph: Neo4jEngine, llm: OllamaClient):
        self.bus = bus
        self.graph = graph
        self.llm = llm

    async def start(self):
        await self.bus.subscribe("task_result:*", self._handle_task_result)
        logger.info("LEARNER V2 started listening to task outcomes.")

    async def _handle_task_result(self, event):
        try:
            task = Task.from_json(event.data)
            if task.status == "FAILED":
                await self._process_failure_pipeline(task)
            elif task.status == "COMPLETED":
                # If completed successfully, check if we need to clear failure counts for active heuristics
                await self._reinforce_success(task)
        except Exception as e:
            logger.error(f"LEARNER pipeline error: {e}")

    async def _process_failure_pipeline(self, task: Task):
        logger.warning(f"Pipeline triggered for failed task: {task.goal} by {task.assignee}")
        
        # 0. Check for Automatic Rollbacks FIRST
        # If this failure was caused by a recently applied heuristic, increment its failure count.
        rolled_back = await self._evaluate_and_rollback(task)
        if rolled_back:
            return # Skip learning a new rule if we just rolled back a bad one causing this failure.
        
        # 1. Reflection Engine
        reflection_json = await self._run_reflection(task)
        if not reflection_json: return
        
        # 2. Validation Engine (LLM-as-a-Judge)
        validation_score = await self._run_validation(task, reflection_json)
        
        # 3. Confidence Scoring Formula
        # Mock reliability score for now (in prod, fetch from Postgres metrics)
        agent_reliability_score = 75.0 
        final_confidence = (validation_score * 0.7) + (agent_reliability_score * 0.3)
        
        logger.info(f"Generated heuristic scored {final_confidence}/100")
        
        # 4. Routing & Storage
        status = "REJECTED"
        active = False
        
        if final_confidence >= 85:
            status = "AUTO_APPROVED"
            active = True
            await self._inject_to_neo4j(task, reflection_json, final_confidence)
        elif final_confidence >= 50:
            status = "PENDING_REVIEW"
        
        # 5. Persist to Postgres for Auditing / Human Review
        await self._persist_to_postgres(task, reflection_json, validation_score, agent_reliability_score, final_confidence, status, active)

    async def _run_reflection(self, task: Task) -> Dict:
        prompt = f"""
        Analyze the following agent failure:
        Agent: {task.assignee}
        Goal: {task.goal}
        Error: {task.result}
        Provide a JSON with "root_cause" and "heuristic_correction".
        """
        try:
            res = await self.llm.generate("llama3", prompt)
            # Simplistic mock parsing for illustration
            return {"root_cause": "Failed to parse API", "heuristic_correction": res[:100]}
        except Exception:
            return {}

    async def _run_validation(self, task: Task, reflection: Dict) -> float:
        """LLM-as-a-Judge to score the proposed reflection."""
        prompt = f"""
        Evaluate this proposed system correction.
        Original Task: {task.goal}
        Error: {task.result}
        Proposed Correction: {reflection.get('heuristic_correction')}
        
        Score from 0 to 100 on how likely this correction will actually solve the error without causing side-effects.
        Return ONLY a number.
        """
        try:
            res = await self.llm.generate("llama3", prompt)
            score = float(res.strip())
            return min(max(score, 0), 100)
        except Exception:
            return 0.0

    async def _inject_to_neo4j(self, task: Task, reflection: Dict, score: float):
        query = """
        MERGE (a:Agent {name: $agent_name})
        CREATE (h:Heuristic {
            id: $h_id,
            task_context: $goal, 
            correction: $correction,
            confidence: $score,
            active: true,
            failure_count: 0
        })
        MERGE (a)-[:USES_RULE]->(h)
        """
        await self.graph.execute_write(query, {
            "agent_name": task.assignee,
            "h_id": str(uuid.uuid4()),
            "goal": task.goal,
            "correction": reflection.get("heuristic_correction"),
            "score": score
        })
        logger.info("Successfully injected AUTO_APPROVED heuristic into Knowledge Graph.")

    async def _persist_to_postgres(self, task: Task, ref: Dict, v_score: float, r_score: float, final: float, status: str, active: bool):
        async for session in get_pg_session():
            query = text("""
            INSERT INTO heuristic_versions (id, agent_name, task_goal, proposed_correction, validation_score, historical_reliability, final_confidence, status, active)
            VALUES (:id, :agent, :goal, :corr, :vscore, :rscore, :final, :status, :active)
            """)
            await session.execute(query, {
                "id": str(uuid.uuid4()),
                "agent": task.assignee,
                "goal": task.goal,
                "corr": ref.get("heuristic_correction"),
                "vscore": v_score,
                "rscore": r_score,
                "final": final,
                "status": status,
                "active": active
            })
            await session.commit()
            logger.info(f"Persisted heuristic version to Postgres. Status: {status}")

    async def _evaluate_and_rollback(self, task: Task) -> bool:
        """
        Checks if the failed agent was using a specific active heuristic.
        If failure count hits 3, deactivate it.
        """
        query = """
        MATCH (a:Agent {name: $agent})-[r:USES_RULE]->(h:Heuristic {active: true})
        SET h.failure_count = h.failure_count + 1
        WITH h
        WHERE h.failure_count >= 3
        SET h.active = false
        RETURN h.id as rolled_back_id
        """
        result = await self.graph.execute_write(query, {"agent": task.assignee})
        if result and len(result) > 0:
            h_id = result[0].get("rolled_back_id")
            logger.critical(f"AUTOMATIC ROLLBACK: Heuristic {h_id} caused 3 consecutive failures and has been deactivated!")
            # Also update Postgres status to ROLLED_BACK
            async for session in get_pg_session():
                await session.execute(text("UPDATE heuristic_versions SET status='ROLLED_BACK', active=false WHERE id=:id"), {"id": h_id})
                await session.commit()
            return True
        return False

    async def _reinforce_success(self, task: Task):
        """If an agent succeeds, reset the failure count of its active heuristics."""
        query = """
        MATCH (a:Agent {name: $agent})-[r:USES_RULE]->(h:Heuristic {active: true})
        SET h.failure_count = 0
        """
        await self.graph.execute_write(query, {"agent": task.assignee})
