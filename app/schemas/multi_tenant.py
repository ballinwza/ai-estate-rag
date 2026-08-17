from typing import Any

from pydantic import BaseModel, Field


class IngestDocumentSchema(BaseModel):
    user_id: str
    chatbot_id: str
    filename: str
    file_type: str
    file_content: bytes


class VectorRecordSchema(BaseModel):
    id: str | None = Field(default=None, alias="id")
    values: list[float]
    metadata: dict[str, Any]
