from datetime import datetime, timezone

from pydantic import BaseModel, Field


class PageDetail(BaseModel):
    page_number: int
    char_length: int
    text: str


class DocumentCreateSchema(BaseModel):
    filename: str
    content_type: str
    total_pages: int
    full_text: str
    pages: list[PageDetail]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DocumentInDB(DocumentCreateSchema):
    id: str = Field(alias="_id")
