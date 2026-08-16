from pydantic import BaseModel


class IngestDocumentDTO(BaseModel):
    user_id: str
    chatbot_id: str
    filename: str
    file_type: str
    file_content: bytes
