from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from backend.database.base import Base

class SecurityAuditLog(Base):
    __tablename__ = "security_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_name = Column(String, index=True)
    agent_name = Column(String, index=True)
    action = Column(String, index=True)
    target = Column(String)
    risk_level = Column(String, index=True)
    result = Column(String)
    ip_address = Column(String)
