import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, Enum, Integer
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class ApprovalStatus(enum.Enum):
    AUTO_APPROVED = "AUTO_APPROVED"
    PENDING_REVIEW = "PENDING_REVIEW"
    MANUALLY_APPROVED = "MANUALLY_APPROVED"
    REJECTED = "REJECTED"
    ROLLED_BACK = "ROLLED_BACK"

class HeuristicVersion(Base):
    __tablename__ = "heuristic_versions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_name = Column(String, nullable=False, index=True)
    task_goal = Column(String, nullable=False)
    proposed_correction = Column(String, nullable=False)
    
    # Confidence metrics
    validation_score = Column(Float, nullable=False)
    historical_reliability = Column(Float, nullable=False)
    final_confidence = Column(Float, nullable=False)
    
    # Lifecycle
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING_REVIEW, nullable=False)
    active = Column(Boolean, default=False)
    
    # Tracking subsequent performance
    failure_count_since_applied = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
