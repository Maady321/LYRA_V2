from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Any, Dict

# Messages schemas
class MessageBase(BaseModel):
    role: str = Field(..., description="Role of the sender: user, assistant, system")
    content: str = Field(..., description="Content of the message")
    model_used: Optional[str] = Field(None, description="Ollama model identifier used to generate assistant response")

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    timestamp: datetime
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_duration: Optional[int] = None

    class Config:
        from_attributes = True

# Conversation schemas
class ConversationBase(BaseModel):
    title: str = Field("New Conversation", description="The display title of this thread")

class ConversationCreate(BaseModel):
    title: Optional[str] = Field(None, description="Optional title, defaults to 'New Conversation'")

class ConversationUpdate(BaseModel):
    title: str = Field(..., description="Updated conversation title")

class ConversationResponse(ConversationBase):
    id: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True

# Settings schemas
class SettingBase(BaseModel):
    key: str = Field(..., description="Unique configuration setting key")
    value: str = Field(..., description="Configuration setting value stringified or raw")

class SettingUpdate(SettingBase):
    pass

class SettingResponse(SettingBase):
    class Config:
        from_attributes = True

# Model info schemas
class ModelInfoResponse(BaseModel):
    name: str
    parameter_size: Optional[str] = None
    context_size: Optional[int] = None
    status: str
    details: Optional[str] = None  # Store details stringified and client can parse

    class Config:
        from_attributes = True

# General schemas
class HealthResponse(BaseModel):
    status: str
    database: str
    ollama: str

