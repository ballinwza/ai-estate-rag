from pydantic import BaseModel


class CreateMultiTenantChatbotDTO(BaseModel):
    user_id: str
    name: str
    description: str
    system_prompt: str


class UpdateMultiTenantChatbotDTO(BaseModel):
    chatbot_id: str
    user_id: str
    name: str | None = None
    description: str | None = None
    system_prompt: str | None = None


class GetMultiTenantChatbotDTO(BaseModel):
    chatbot_id: str
    user_id: str


class ListMultiTenantChatbotsDTO(BaseModel):
    user_id: str
    limit: int = 100
    offset: int = 0


class DeleteMultiTenantChatbotDTO(BaseModel):
    chatbot_id: str
    user_id: str
