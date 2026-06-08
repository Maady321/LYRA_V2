import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, BigInteger, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database.base import Base

class Conversation(Base):
    __tablename__ = "conversations"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), default="New Conversation")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationship to messages
    messages: Mapped[List["Message"]] = relationship(
        "Message", 
        back_populates="conversation", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class Message(Base):
    __tablename__ = "messages"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(50))  # 'user', 'assistant', 'system'
    content: Mapped[str] = mapped_column(Text)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Generation metadata
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_duration: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)  # duration in nanoseconds
    
    # Relationship to conversation
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

class Setting(Base):
    __tablename__ = "settings"
    
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text)  # Store value as JSON string or plain text

class ModelInfo(Base):
    __tablename__ = "models"
    
    name: Mapped[str] = mapped_column(String(255), primary_key=True)  # e.g., llama3
    parameter_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # e.g., 8B, 7B
    context_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # e.g., 8192
    status: Mapped[str] = mapped_column(String(50), default="installed")  # installed, downloading, dynamic
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # raw details from Ollama API
