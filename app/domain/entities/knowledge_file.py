from pydantic import BaseModel, Field


class CreateKnowledgeFile(BaseModel):
    user_id: str
    chatbot_id: str
    filename: str
    file_type: str
    file_content: bytes


class ProcessAndIngestDocument(BaseModel):
    user_id: str
    chatbot_id: str
    filename: str
    file_type: str
    file_content: bytes


class GetKnowledgeFile(BaseModel):
    id: str
    user_id: str


class ListKnowledgeFiles(BaseModel):
    user_id: str
    chatbot_id: str
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class DeleteKnowledgeFile(BaseModel):
    chatbot_id: str
    user_id: str
