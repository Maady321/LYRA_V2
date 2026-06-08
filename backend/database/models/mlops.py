import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, JSON, ForeignKey, Enum
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class DeploymentStatus(enum.Enum):
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"
    ARCHIVED = "ARCHIVED"
    ROLLED_BACK = "ROLLED_BACK"

class ModelRegistry(Base):
    __tablename__ = "model_registry"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True) # e.g., "llama3"
    version = Column(String, nullable=False) # e.g., "v1.2.0"
    provider = Column(String, nullable=False) # e.g., "ollama", "openai"
    precision = Column(String) # e.g., "Q4_K_M"
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.STAGING)
    created_at = Column(DateTime, default=datetime.utcnow)

class PromptRegistry(Base):
    __tablename__ = "prompt_registry"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_type = Column(String, nullable=False, index=True) # e.g., "FURY", "STARK"
    version = Column(String, nullable=False)
    system_prompt = Column(String, nullable=False)
    few_shot_examples = Column(JSON, nullable=True)
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.STAGING)
    # A/B Testing weights. Sum of weights for an agent_type should be 100 in PRODUCTION
    traffic_weight = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)

class AgentRegistry(Base):
    __tablename__ = "agent_registry"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)
    version = Column(String, nullable=False)
    model_id = Column(String, ForeignKey("model_registry.id"), nullable=False)
    prompt_id = Column(String, ForeignKey("prompt_registry.id"), nullable=False)
    tool_names = Column(JSON, nullable=False) # List of enabled tools
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.STAGING)
    created_at = Column(DateTime, default=datetime.utcnow)

class EvaluationMetrics(Base):
    """Tracks performance of models/prompts in production for automated routing."""
    __tablename__ = "evaluation_metrics"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = Column(String, nullable=False) # 'MODEL', 'PROMPT', 'AGENT'
    entity_id = Column(String, nullable=False, index=True)
    task_id = Column(String, nullable=False)
    latency_ms = Column(Float)
    tokens_used = Column(Integer)
    success = Column(Boolean)
    human_rating = Column(Integer, nullable=True) # 1-5 scale
    created_at = Column(DateTime, default=datetime.utcnow)
