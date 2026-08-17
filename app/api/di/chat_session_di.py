from typing import TypedDict

from app.core.mongodb import get_mongodb_database
from app.infrastructure.persistence.mongodb.chat_session_repository import (
    MongoChatSessionRepository,
)
from app.usecases.multi_tenant.chat_session_usecase import (
    AddChatMessageUseCase,
    CreateChatSessionUseCase,
    DeleteChatSessionUseCase,
    GetChatHistoryUseCase,
    GetChatSessionUseCase,
    ListUserChatSessionsUseCase,
)


# Type Dict เพิ่มเติมสำหรับ Chatbot Blueprint Use Cases
class ChatSessionUseCaseDict(TypedDict):
    create_session_use_case: CreateChatSessionUseCase
    get_history_use_case: GetChatHistoryUseCase
    get_session_use_case: GetChatSessionUseCase
    get_list_session_use_case: ListUserChatSessionsUseCase
    add_message_use_case: AddChatMessageUseCase
    delete_message_use_case: DeleteChatSessionUseCase


def build_chat_session_usecases() -> ChatSessionUseCaseDict:
    """
    Factory Function สำหรับดึง Mongo Connection และ Inject เข้า
    MongoChatSessionRepository ร่วมกับ Chatbot Session Use Cases
    """
    mongo_db = get_mongodb_database()
    session_repo = MongoChatSessionRepository(db=mongo_db)

    return {
        "create_session_use_case": CreateChatSessionUseCase(session_repo=session_repo),
        "get_history_use_case": GetChatHistoryUseCase(session_repo=session_repo),
        "get_session_use_case": GetChatSessionUseCase(session_repo=session_repo),
        "get_list_session_use_case": ListUserChatSessionsUseCase(
            session_repo=session_repo
        ),
        "add_message_use_case": AddChatMessageUseCase(session_repo=session_repo),
        "delete_message_use_case": DeleteChatSessionUseCase(session_repo=session_repo),
    }
