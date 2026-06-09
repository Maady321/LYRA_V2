from agents.base import BaseAgent
from core.bus import Task

class RedAgent(BaseAgent):
    async def handle_task(self, task: Task) -> str:
        """
        Test agent that simulates red team activities or testing interactions.
        """
        prompt = task.payload.get("prompt", "").lower().strip()
        await self.emit_log(f"RED_AGENT test module intercepting task: '{prompt}'")
        return f"RED_AGENT successfully executed test task. Received payload: {prompt}"
