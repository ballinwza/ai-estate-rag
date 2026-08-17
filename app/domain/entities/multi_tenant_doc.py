# Multi tenant
# Chat history
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


class ChatbotBlueprint(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    user_id: str
    name: str
    description: str
    system_prompt: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# knowleadge file
class FileStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Chunk(BaseModel):
    vector_id: str
    chunk_index: int
    text_content: str
    page_number: int
    token_count: int


class KnowledgeFiles(BaseModel):
    id: str | None = Field(default=None, alias="_id")
    user_id: str
    chatbot_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    status: FileStatus
    total_chunks: int = 1
    chunks: list[Chunk] = []
    total_page: int = 1
    text_content: str | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Vector db
class MetadataVectorRecord(BaseModel):
    user_id: str
    chatbot_id: str
    file_id: str

    chunk_index: int
    text_content: str
    page_number: int

    filename: str


class VectorRecord(BaseModel):
    id: str | None = None
    values: list[float]
    metadata: MetadataVectorRecord


class SearchVectorRecordItem(BaseModel):
    score: float
    record: VectorRecord
