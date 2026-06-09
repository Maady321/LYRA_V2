import os
from pathlib import Path
from agents.base import BaseAgent
from core.bus import Task
from MJ_AI_Assistant.security.guardian import guardian_kernel

class BannerAgent(BaseAgent):
    async def handle_task(self, task: Task) -> str:
        """
        Conducts local knowledge bases, reads files, and analyzes text content.
        """
        user_prompt = task.payload.get("prompt", "")
        await self.emit_log(f"Conducting research query: '{user_prompt}'")

        # Extract path or file reference in prompt if any
        workspace_path = Path(__file__).parent.parent
        file_content = ""
        target_file = None

        # Simple file lookup in the local folder
        for word in user_prompt.split():
            if "." in word and len(word) > 4:
                # Clean word from quotes or brackets
                cleaned_word = word.replace('"', '').replace("'", "").replace("[", "").replace("]", "")
                possible_file = workspace_path / cleaned_word
                if possible_file.exists() and possible_file.is_file():
                    target_file = possible_file
                    break

        if target_file:
            await self.emit_log(f"BANNER scanning file asset: {target_file.name}")
            try:
                with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
                    file_content = f.read(4000)  # Read up to 4k characters
            except Exception as e:
                file_content = f"Error reading file: {e}"

        # Feed file content into local model for summarization/RAG
        system_prompt = (
            "You are BANNER, the brilliant Research and Knowledge Retrieval Agent of the MJ AI Assistant.\n"
            "Analyze the given document content or answer the research prompt based on valid facts.\n"
            "Keep your output factually verified, precise, and highly analytical."
        )

        user_content = f"Query: {user_prompt}"
        if file_content:
            user_content += f"\n\nDocument content to analyze:\n{file_content}"

        input_data = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        research_report = self.client.generate_chat_response(input_data)
        return research_report
