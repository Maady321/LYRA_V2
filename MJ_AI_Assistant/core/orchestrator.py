import uuid
import asyncio
from typing import Dict, Any, List
from memory.sqlite_db import SQLiteDB
from memory.analytics_db import AnalyticsDB
from memory.graph_engine import KnowledgeGraphEngine
from memory.goal_manager import AutonomousGoalManager
from core.ollama_client import OllamaClient
from core.bus import MessageBus, Task

# Import specialized agents
from agents.fury import FuryAgent
from agents.vision import VisionAgent
from agents.captain import CaptainAgent
from agents.banner import BannerAgent
from agents.stark import StarkAgent
from agents.jarvis import JarvisAgent
from agents.spidey import SpideyAgent
from agents.ghost import GhostAgent
from agents.eagle import EagleAgent
from security.guardian import GuardianAgent
from user_model.twin_engine import UserModelTwin
from agents.navigator import NavigatorAgent
from memory.dreamer import DreamerMemoryConsolidator
from agents.red_agent import RedAgent
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.security.prompt_firewall_v2 import PromptFirewallV2

class MJOrchestrator:
    def __init__(self):
        # 1. Core Services & Database
        self.db = SQLiteDB()
        self.analytics_db = AnalyticsDB()
        self.client = OllamaClient()
        self.bus = MessageBus(self.db)
        
        # 2. Advanced AIOS Engines
        self.graph_engine = KnowledgeGraphEngine(self.db)
        self.goal_manager = AutonomousGoalManager(self.db)
        self.guardian = GuardianAgent(self.db.db_path)
        self.firewall = PromptFirewallV2(db_connection=self.db)
        self.user_twin = UserModelTwin(self.db.db_path)
        self.dreamer = DreamerMemoryConsolidator(self.db.db_path, self.graph_engine, self.client)
        
        # 3. Instantiate Agent workforce
        self.vision = VisionAgent("VISION", self.bus, self.client, self.db)
        self.fury = FuryAgent("FURY", self.bus, self.client, self.db)
        self.captain = CaptainAgent("CAPTAIN", self.bus, self.client, self.db)
        self.banner = BannerAgent("BANNER", self.bus, self.client, self.db)
        self.stark = StarkAgent("STARK", self.bus, self.client, self.db)
        self.jarvis = JarvisAgent("JARVIS", self.bus, self.client, self.db)
        self.spidey = SpideyAgent("SPIDEY", self.bus, self.client, self.db)
        
        # New AIOS agents
        self.ghost = GhostAgent("GHOST", self.bus, self.client, self.db)
        self.eagle = EagleAgent("EAGLE", self.bus, self.client, self.db)
        self.navigator = NavigatorAgent("NAVIGATOR", self.bus, self.client, self.db)
        self.red_agent = RedAgent("RED_AGENT", self.bus, self.client, self.db)



        # 4. Spin up the Background Autonomous Subtask Daemon safely
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._autonomous_background_worker())
        except RuntimeError:
            pass

    async def execute_query(self, prompt: str, conversation_id: str = "default") -> str:
        """
        Coordinates cooperative execution, injecting knowledge graph context parameters.
        """
        # Validate through PROMPT FIREWALL V2
        is_allowed, firewall_response, audit_data = await self.firewall.inspect_prompt("local_user", prompt)
        if not is_allowed:
            return firewall_response
            
        # Use sanitized prompt if necessary
        safe_prompt = firewall_response
            
        # Validate through GUARDIAN security wall first!
        verdict, risk_score, reasoning = self.guardian.validate_action("FURY", "CHAT", safe_prompt)
        if verdict == "BLOCKED":
            return f"[GUARDIAN BLOCK] Action denied by kernel security. Verdict: {verdict}. Risk: {risk_score}. Reasoning: {reasoning}"

        # Analyze and update the User Digital Twin state!
        self.user_twin.analyze_query_for_twin(safe_prompt)

        # Save user prompt
        user_msg_id = str(uuid.uuid4())
        self.db.add_message(user_msg_id, conversation_id, "user", safe_prompt)

        # 1. Query Knowledge Graph semantic context links!
        graph_context = self.graph_engine.query_semantic_context(safe_prompt)
        
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        coordinator_task = Task(
            task_id=task_id,
            goal="Coordinate user prompt flow",
            assigner="USER",
            assignee="FURY",
            payload={
                "prompt": safe_prompt, 
                "conversation_id": conversation_id,
                "graph_context": graph_context
            }
        )
        
        # 2. Dispatch task to Fury Coordinator
        final_answer = await self.bus.dispatch_task(coordinator_task)
        
        # Save assistant synthesized response
        assist_msg_id = str(uuid.uuid4())
        self.db.add_message(assist_msg_id, conversation_id, "assistant", final_answer)
        
        return final_answer

    async def _autonomous_background_worker(self) -> None:
        """
        Continuous background thread executing autonomous goal subtasks proactively.
        """
        while True:
            try:
                pending_tasks = self.goal_manager.get_pending_subtasks()
                for task_meta in pending_tasks:
                    subtask_id = task_meta["subtask_id"]
                    assigned_agent = task_meta["assigned_agent"]
                    title = task_meta["title"]
                    
                    print(f"[Autonomous Daemon] Executing proactive subtask: '{title}' on {assigned_agent}")
                    
                    # Update status to running
                    self.goal_manager.update_subtask_status(subtask_id, "RUNNING")
                    
                    # Construct async bus task
                    bus_task = Task(
                        task_id=f"auto_{subtask_id}",
                        goal=title,
                        assigner="AUTONOMOUS_DAEMON",
                        assignee=assigned_agent,
                        payload={"prompt": title}
                    )
                    
                    # Dispatch to agent
                    result = await self.bus.dispatch_task(bus_task)
                    
                    # Save results and update status
                    self.goal_manager.update_subtask_status(subtask_id, "COMPLETED", result=str(result))
                    
                    # Emit alert notification event
                    await self.bus.emit(
                        channel="notification_channel",
                        sender="SPIDEY",
                        data={"message": f"[Goal Update] Subtask '{title}' completed successfully!"}
                    )
                    
            except Exception as e:
                print(f"[Autonomous Daemon] Background cycle warning: {e}")
                
            await asyncio.sleep(6) # Poll queue every 6 seconds
