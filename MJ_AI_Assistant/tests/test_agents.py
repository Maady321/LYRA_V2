import unittest
import asyncio
import os
import sys
from pathlib import Path

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.orchestrator import MJOrchestrator
from core.bus import Task

class TestMJAgents(unittest.TestCase):
    def setUp(self):
        # Build local orchestrator for unit testing
        self.orchestrator = MJOrchestrator()
        self.loop = asyncio.get_event_loop()
        
        # Mock Ollama embeddings call to run deterministically and 100% offline
        self.orchestrator.client.generate_embedding = lambda text, *args, **kwargs: [
            1.0 if char in text.lower() else 0.0 for char in "abcdefghijklmnopqrstuvwxyz" * 30
        ][:768]

    def test_database_initialization(self):
        """
        Confirms databases and tables are allocated cleanly on launch.
        """
        self.assertTrue(self.orchestrator.db.db_path.exists())
        pref_name = self.orchestrator.db.get_preference("name", "Friend")
        self.assertEqual(pref_name, "Friend")

    def test_bus_task_registration(self):
        """
        Verifies all specialized agents register task handlers successfully on the bus.
        """
        active_list = list(self.orchestrator.bus._agent_task_handlers.keys())
        expected = ["FURY", "VISION", "CAPTAIN", "BANNER", "STARK", "JARVIS", "SPIDEY", "GHOST", "EAGLE"]
        for agent in expected:
            self.assertIn(agent, active_list)

    def test_vision_store_and_retrieve(self):
        """
        Verifies VISION agent processes memory store and retrieve routines correctly.
        """
        async def run_vision_test():
            # 1. Store memory
            store_task = Task(
                task_id="test_store_1",
                goal="Save fact",
                assigner="TEST",
                assignee="VISION",
                payload={"action": "store", "fact": "User is a Senior AI Engineer named Sabari"}
            )
            store_res = await self.orchestrator.bus.dispatch_task(store_task)
            self.assertEqual(store_res, "Memory successfully stored.")

            # 2. Retrieve memory
            retrieve_task = Task(
                task_id="test_retrieve_1",
                goal="Retrieve context",
                assigner="TEST",
                assignee="VISION",
                payload={"action": "retrieve", "query": "Sabari"}
            )
            context = await self.orchestrator.bus.dispatch_task(retrieve_task)
            self.assertIn("Sabari", context)

        self.loop.run_until_complete(run_vision_test())

    def test_knowledge_graph(self):
        """
        Verifies Knowledge Graph manages entities and crawls multi-hop relationships correctly.
        """
        # 1. Map Subject -> Predicate -> Object
        self.orchestrator.graph_engine.add_relationship("Maddy", "studies", "BCA")
        self.orchestrator.graph_engine.add_relationship("Maddy", "interested_in", "DevOps")
        
        # 2. Traverse BFS paths
        paths = self.orchestrator.graph_engine.traverse_multi_hop("Maddy", max_hops=2)
        self.assertTrue(len(paths) >= 2)
        
        # 3. Retrieve formatted context string
        context = self.orchestrator.graph_engine.query_semantic_context("studies BCA")
        self.assertIn("studies", context)

    def test_autonomous_task_engine(self):
        """
        Verifies Goal manager schedules subtasks and updates statuses successfully.
        """
        # 1. Register Goal
        goal_id = self.orchestrator.goal_manager.register_goal("Perform Diagnostics Plan", priority=5)
        self.assertTrue(goal_id.startswith("goal_"))
        
        # 2. Add executable Subtask
        subtask_id = self.orchestrator.goal_manager.add_subtask(goal_id, "Analyze CPU Loads", "JARVIS")
        self.assertTrue(subtask_id.startswith("subtask_"))
        
        # 3. Verify pending queue
        pending = self.orchestrator.goal_manager.get_pending_subtasks()
        self.assertTrue(any(t["subtask_id"] == subtask_id for t in pending))

if __name__ == "__main__":
    unittest.main()
