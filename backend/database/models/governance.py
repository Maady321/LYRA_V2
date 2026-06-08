import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, Enum, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()

class CertificationTier(enum.Enum):
    TIER_3_UNCERTIFIED = "TIER_3_UNCERTIFIED"
    TIER_2_VERIFIED = "TIER_2_VERIFIED"
    TIER_1_CERTIFIED = "TIER_1_CERTIFIED"

class LifecycleState(enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DEPRECATED = "DEPRECATED"

class GovernanceRegistry(Base):
    __tablename__ = "governance_registry"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_name = Column(String, nullable=False, unique=True, index=True)
    description = Column(String, nullable=False)
    
    tier = Column(Enum(CertificationTier), default=CertificationTier.TIER_3_UNCERTIFIED, nullable=False)
    state = Column(Enum(LifecycleState), default=LifecycleState.DRAFT, nullable=False)
    
    # Relationships
    capabilities = relationship("CapabilityRegistry", back_populates="agent", cascade="all, delete-orphan")
    trust_profile = relationship("TrustRegistry", uselist=False, back_populates="agent", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CapabilityRegistry(Base):
    """Taxonomy of skills the agent claims to possess."""
    __tablename__ = "capability_registry"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("governance_registry.id"), nullable=False)
    capability_name = Column(String, nullable=False) # e.g. "READ_DB", "WRITE_CODE"
    is_validated = Column(Boolean, default=False) # True if automated synthetic tests passed
    
    agent = relationship("GovernanceRegistry", back_populates="capabilities")

class TrustRegistry(Base):
    """Audit log of health, success rate, and security incidents."""
    __tablename__ = "trust_registry"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("governance_registry.id"), nullable=False)
    
    tasks_attempted = Column(Integer, default=0)
    tasks_succeeded = Column(Integer, default=0)
    security_violations = Column(Integer, default=0) # E.g. prompt injection attempts caught by Guardian
    
    trust_score = Column(Float, default=100.0)
    health_score = Column(Float, default=100.0)
    
    agent = relationship("GovernanceRegistry", back_populates="trust_profile")
