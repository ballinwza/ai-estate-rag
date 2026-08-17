from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    USER = "user"
    AI = "ai"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatSession(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    user_id: str
    chatbot_id: str
    session_title: str
    messages: list[ChatMessage] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==============================================================================
# DTOs (Data Transfer Objects)
# ==============================================================================


class CreateChatSessionDTO(BaseModel):
    user_id: str
    chatbot_id: str
    session_title: str | None = "New Chat"


class AddChatMessageDTO(BaseModel):
    session_id: str
    user_id: str
    role: MessageRole
    content: str


class GetChatHistoryDTO(BaseModel):
    session_id: str
    user_id: str
