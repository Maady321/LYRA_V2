from typing import Any
from core.bus import MessageBus, Task, Event
from core.ollama_client import OllamaClient
from memory.sqlite_db import SQLiteDB

class BaseAgent:
    def __init__(self, name: str, bus: MessageBus, client: OllamaClient, db: SQLiteDB):
        self.name = name.upper()
        self.bus = bus
        self.client = client
        self.db = db
        
        # Register task routing automatically on instantiation
        self.bus.register_task_handler(self.name, self.handle_task)

    async def handle_task(self, task: Task) -> Any:
        """
        Subclasses should override this method to implement agent-specific logic.
        """
        raise NotImplementedError(f"Agent '{self.name}' must implement handle_task.")

    async def emit_log(self, message: str, status: str = "INFO") -> None:
        """
        Emits log diagnostic events onto the bus channels.
        """
        await self.bus.emit(
            channel="system_monitor_channel",
            sender=self.name,
            data={"log": message, "status": status}
        )
