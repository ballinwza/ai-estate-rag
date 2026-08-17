from typing import TypedDict

from app.core.mongodb import get_mongodb_database
from app.infrastructure.persistence.mongodb.multi_tenant_repository import (
    MongoMultiTenantChatbotRepository,
)
from app.usecases.multi_tenant.chatbot_usecase import (
    CreateMultiTenantChatbotUseCase,
    DeleteMultiTenantChatbotUseCase,
    GetMultiTenantChatbotUseCase,
    ListUserMultiTenantChatbotsUseCase,
    UpdateMultiTenantChatbotUseCase,
)


# Type Dict เพิ่มเติมสำหรับ Chatbot Blueprint Use Cases
class ChatbotUseCaseDict(TypedDict):
    create_use_case: CreateMultiTenantChatbotUseCase
    get_use_case: GetMultiTenantChatbotUseCase
    list_use_case: ListUserMultiTenantChatbotsUseCase
    update_use_case: UpdateMultiTenantChatbotUseCase
    delete_use_case: DeleteMultiTenantChatbotUseCase


def build_chatbot_usecases() -> ChatbotUseCaseDict:
    """
    Factory Function สำหรับดึง Mongo Connection และ Inject เข้า
    MongoMultiTenantChatbotRepository ร่วมกับ Chatbot Blueprint Use Cases
    """
    mongo_db = get_mongodb_database()
    chatbot_repo = MongoMultiTenantChatbotRepository(db=mongo_db)

    return {
        "create_use_case": CreateMultiTenantChatbotUseCase(chatbot_repo=chatbot_repo),
        "get_use_case": GetMultiTenantChatbotUseCase(chatbot_repo=chatbot_repo),
        "list_use_case": ListUserMultiTenantChatbotsUseCase(chatbot_repo=chatbot_repo),
        "update_use_case": UpdateMultiTenantChatbotUseCase(chatbot_repo=chatbot_repo),
        "delete_use_case": DeleteMultiTenantChatbotUseCase(chatbot_repo=chatbot_repo),
    }
