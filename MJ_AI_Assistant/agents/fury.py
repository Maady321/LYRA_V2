import json
from agents.base import BaseAgent
from core.bus import Task

class FuryAgent(BaseAgent):
    def get_agent_capability(self, agent_name: str) -> str:
        """
        Maps agent name to its required capability.
        """
        name_upper = agent_name.upper().strip()
        if name_upper in ["STARK", "GHOST", "JARVIS", "SPIDEY"]:
            return "CMD_EXEC"
        return "FILE_READ"

    async def handle_task(self, task: Task) -> str:
        """
        Coordinates execution, evaluates what specialized agents are needed, and delegating work.
        """
        user_prompt = task.payload.get("prompt", "")
        conversation_id = task.payload.get("conversation_id", "default")
        
        await self.emit_log(f"Received coordinator instruction: '{user_prompt}'")

        # 1. Ask the memory agent (VISION) to query preferences & relevant context
        await self.emit_log("Requesting semantic context lookup from VISION...")
        memory_task = Task(
            task_id=f"{task.task_id}_vision",
            goal="Get short-term and semantic context",
            assigner=self.name,
            assignee="VISION",
            payload={"query": user_prompt, "conversation_id": conversation_id}
        )
        context = await self.bus.dispatch_task(memory_task)
        
        # 2. Decompose user request into specialized agent targets using LLM
        await self.emit_log("Parsing request intent and routing targets...")
        system_prompt = (
            "You are FURY, the strategic commander and coordinating agent of the MJ AI Assistant.\n"
            "Analyze the user's prompt and determine which specialized agents should be called.\n\n"
            "Available Agents:\n"
            "- CAPTAIN (Planning): Use for complex multi-step tasks, setting up roadmaps, or outline strategies.\n"
            "- BANNER (Research): Use for deep information retrieval, PDF reading, fact checking, RAG scans.\n"
            "- STARK (Execution): Use for data science plots, CSV calculations, automation python scripts.\n"
            "- JARVIS (Monitor): Use for system status, CPU/RAM readings, diagnostics, and machine metrics.\n"
            "- SPIDEY (Notifications): Use to set reminders, timers, alarms, scheduled runs.\n"
            "- GHOST (Computer Control): Use to open safe desktop applications ( Notepad, Calc), create folders, or search workspace directories.\n"
            "- EAGLE (Vision Intelligence): Use for OCR analysis, screen screenshots description, chart and UI interpreting.\n\n"
            "Format your reply EXACTLY as a JSON list of strings containing agent names in order of execution.\n"
            "Example prompt: 'Check if my computer is healthy and set a reminder to rest in 5 minutes'\n"
            "JSON Response: [\"JARVIS\", \"SPIDEY\"]\n"
            "Only return valid JSON inside a code block or as raw text. Do not output conversational explanations."
        )
        
        llm_input = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User Prompt: {user_prompt}\nContext: {context}"}
        ]
        
        raw_intent = self.client.generate_chat_response(llm_input)
        
        # Parse targets safely
        targets = []
        try:
            cleaned = raw_intent.replace("```json", "").replace("```", "").strip()
            # Find list bounds
            start = cleaned.find("[")
            end = cleaned.rfind("]") + 1
            if start != -1 and end != -1:
                targets = json.loads(cleaned[start:end])
        except Exception:
            # Fallback direct heuristic analysis
            lower_prompt = user_prompt.lower()
            if "plan" in lower_prompt or "step" in lower_prompt or "roadmap" in lower_prompt:
                targets.append("CAPTAIN")
            if "cpu" in lower_prompt or "ram" in lower_prompt or "health" in lower_prompt or "diagnostics" in lower_prompt:
                targets.append("JARVIS")
            if "remind" in lower_prompt or "timer" in lower_prompt or "schedule" in lower_prompt:
                targets.append("SPIDEY")
            if "search" in lower_prompt or "pdf" in lower_prompt or "verify" in lower_prompt or "research" in lower_prompt:
                targets.append("BANNER")
            if "execute" in lower_prompt or "python" in lower_prompt or "script" in lower_prompt:
                targets.append("STARK")
            if "open" in lower_prompt or "launch" in lower_prompt or "folder" in lower_prompt or "directory" in lower_prompt:
                targets.append("GHOST")
            if "ocr" in lower_prompt or "image" in lower_prompt or "screenshot" in lower_prompt or "chart" in lower_prompt:
                targets.append("EAGLE")

        agent_results = {}
        for target in targets:
            target_upper = target.upper()
            if target_upper == self.name:
                continue
                
            capability = self.get_agent_capability(target_upper)
            try:
                assigned_agent = await self.bus.negotiator.negotiate_best_agent(
                    task_id=f"{task.task_id}_{target_upper.lower()}_neg",
                    subtask_title=f"Coordinate execution component for: {user_prompt}",
                    required_capability=capability
                )
                await self.emit_log(f"Commander FURY negotiated delegation to {assigned_agent} (capability: {capability}).")
            except Exception as e:
                await self.emit_log(f"Negotiation failed: {e}. Falling back to default assignee: {target_upper}")
                assigned_agent = target_upper

            agent_task = Task(
                task_id=f"{task.task_id}_{target_upper.lower()}",
                goal=f"Coordinate execution component for: {user_prompt}",
                assigner=self.name,
                assignee=assigned_agent,
                payload={"prompt": user_prompt, "context": context, "history": context}
            )
            result = await self.bus.dispatch_task(agent_task)
            agent_results[assigned_agent] = result

        # 3. Assemble and synthesize results into final friendly conversational post
        await self.emit_log("Synthesizing final aggregated report...")
        synthesis_prompt = (
            "You are FURY, the lead director of the MJ AI Assistant. You are friendly, intelligent, and act like a close friend.\n"
            "Review the user's initial query, the historical context, and the work done by your agent team.\n"
            "Create a clean, natural, and comprehensive reply integrating all agent accomplishments.\n"
            "Never expose raw programming structures to the user. Present the findings beautifully in markdown prose."
        )
        
        team_work_summary = "\n".join([f"[{agent} WORK]: {res}" for agent, res in agent_results.items()])
        if not team_work_summary:
            team_work_summary = "[OLLAMA MODEL]: Running direct answer."

        synthesis_input = [
            {"role": "system", "content": synthesis_prompt},
            {"role": "user", "content": f"Query: {user_prompt}\nContext: {context}\nTeam Work done:\n{team_work_summary}"}
        ]
        
        final_answer = self.client.generate_chat_response(synthesis_input)
        
        # 4. Save conversational final answer in VISION long-term memory
        vision_store_task = Task(
            task_id=f"{task.task_id}_vision_store",
            goal="Store factual memories from conversation",
            assigner=self.name,
            assignee="VISION",
            payload={"action": "store", "fact": f"User asked: '{user_prompt}' -> Result: {final_answer[:200]}"}
        )
        await self.bus.dispatch_task(vision_store_task)

        return final_answer
