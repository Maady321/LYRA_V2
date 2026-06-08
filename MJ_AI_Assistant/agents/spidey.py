import asyncio
from agents.base import BaseAgent
from core.bus import Task

class SpideyAgent(BaseAgent):
    async def handle_task(self, task: Task) -> str:
        """
        Manages timers, notifications, and background countdown reminder triggers.
        """
        prompt = task.payload.get("prompt", "")
        await self.emit_log(f"Assessing notification scheduler request: '{prompt}'")

        # Basic parser for duration (e.g. "reminder in 5 seconds to stand up" or "remind me in 2 minutes")
        import re
        duration = 10  # default 10s
        subject = "Time is up!"
        
        # Regex to match duration numbers
        num_match = re.search(r"(\d+)\s*(second|sec|minute|min|hour|hr)", prompt, re.IGNORECASE)
        if num_match:
            val = int(num_match.group(1))
            unit = num_match.group(2).lower()
            if "minute" in unit or "min" in unit:
                duration = val * 60
            elif "hour" in unit or "hr" in unit:
                duration = val * 3600
            else:
                duration = val

        # Regex to capture what the user wants to be reminded of
        sub_match = re.search(r"(?:remind me to|reminder to|remind me)\s+(.*)", prompt, re.IGNORECASE)
        if sub_match:
            subject = sub_match.group(1).strip()

        # Launch non-blocking background async task to countdown and announce
        asyncio.create_task(self._run_timer(duration, subject))
        
        await self.emit_log(f"Alert scheduled successfully: '{subject}' in {duration}s")
        return f"Notification Scheduled: I will remind you to '{subject}' in exactly {duration} seconds."

    async def _run_timer(self, delay: int, text: str) -> None:
        await asyncio.sleep(delay)
        # Emit alert event onto the message bus
        await self.bus.emit(
            channel="notification_channel",
            sender=self.name,
            data={"alert": text, "message": f"[MJ ALERT] Reminder: {text}"}
        )
