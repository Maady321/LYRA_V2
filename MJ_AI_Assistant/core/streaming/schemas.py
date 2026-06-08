import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any, Dict, Optional

class EventPayload(BaseModel):
    """Base class for stream events"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    sender: str
    
class TaskEvent(EventPayload):
    """Represents a Task routed to an agent"""
    task_id: str
    assignee: str
    goal: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    retries: int = 0

class SystemEvent(EventPayload):
    """Represents a global broadcast event (e.g. FURY Leader Elected)"""
    event_type: str
    details: Dict[str, Any] = Field(default_factory=dict)

class AgentHeartbeat(EventPayload):
    """Represents a durable heartbeat logging to stream"""
    node_id: str
    status: str
    cpu_usage: float
    ram_usage: float
