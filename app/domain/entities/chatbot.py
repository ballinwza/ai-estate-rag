from pydantic import BaseModel


class CreateMultiTenantChatbot(BaseModel):
    user_id: str
    name: str
    description: str
    system_prompt: str


class UpdateMultiTenantChatbot(BaseModel):
    chatbot_id: str
    user_id: str
    name: str | None = None
    description: str | None = None
    system_prompt: str | None = None


class GetMultiTenantChatbot(BaseModel):
    chatbot_id: str
    user_id: str


class ListMultiTenantChatbots(BaseModel):
    user_id: str
    limit: int = 100
    offset: int = 0


class DeleteMultiTenantChatbot(BaseModel):
    chatbot_id: str
    user_id: str
