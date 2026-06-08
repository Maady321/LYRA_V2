import unittest
import os
import sys
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.navigator import NavigatorAgent
from core.bus import Task

class MockMessageBus:
    def __init__(self):
        self.agents = {}

    def register_task_handler(self, agent_name: str, handler) -> None:
        self.agents[agent_name] = handler

class TestNavigatorAgent(unittest.TestCase):
    def setUp(self):
        self.bus = MockMessageBus()
        self.navigator = NavigatorAgent("NAVIGATOR", self.bus)
        self.loop = asyncio.get_event_loop()

    def test_agent_registration(self):
        """
        Confirms NAVIGATOR registers its task handler on the central Message Bus.
        """
        self.assertIn("NAVIGATOR", self.bus.agents)

    def test_search_task_execution(self):
        """
        Confirms search actions execute safely returning result strings.
        """
        async def run_search():
            task = Task(
                task_id="t1",
                goal="Search",
                assigner="FURY",
                assignee="NAVIGATOR",
                payload={"action": "search", "query": "python fastapi"}
            )
            res = await self.navigator.handle_task(task)
            self.assertTrue(len(res) > 0)
            
        self.loop.run_until_complete(run_search())

    def test_navigate_task_execution(self):
        """
        Confirms direct page reads operate successfully.
        """
        async def run_navigate():
            task = Task(
                task_id="t2",
                goal="Navigate",
                assigner="FURY",
                assignee="NAVIGATOR",
                payload={"action": "navigate", "url": "https://fastapi.tiangolo.com/"}
            )
            res = await self.navigator.handle_task(task)
            self.assertTrue(len(res) > 0)
            
        self.loop.run_until_complete(run_navigate())

if __name__ == "__main__":
    unittest.main()
