from pydantic import BaseModel, Field

from app.domain.entities.multi_tenant_doc import VectorRecord


class RagSearchSimilarRequest(BaseModel):
    user_id: str
    chatbot_id: str
    query_text: str
    top_k: int = Field(default=5, ge=1, le=100)
    file_id: str | None = None


class SearchResultItem(BaseModel):
    score: float
    record: VectorRecord


class RagResponse(BaseModel):
    answer_message: str
    sources: list[SearchResultItem]
