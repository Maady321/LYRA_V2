from agents.base import BaseAgent
from core.bus import Task

class CaptainAgent(BaseAgent):
    async def handle_task(self, task: Task) -> str:
        """
        Decomposes complex requests into clear strategic roadmaps.
        """
        user_prompt = task.payload.get("prompt", "")
        await self.emit_log(f"Formulating execution roadmap for: '{user_prompt}'")

        system_prompt = (
            "You are CAPTAIN, the elite Planning Agent of the MJ AI Assistant.\n"
            "Your role is to break complex, multi-step goals into small, actionable steps.\n"
            "Output a structured, clear markdown roadmap with bullet points.\n"
            "Highlight dependencies, checklist checkboxes `[ ]`, and assign specific targets if relevant."
        )

        input_data = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Formulate a plan for this objective: '{user_prompt}'"}
        ]

        roadmap = self.client.generate_chat_response(input_data)
        return roadmap
