from abc import ABC, abstractmethod
from typing import Any

from app.domain.entities.chat_session import ChatMessage, ChatSession


class ChatSessionRepository(ABC):
    """
    [ต้องสร้างเพิ่ม] Implement ใน Infrastructure Layer (เช่น mongodb/chat_session_repository.py)
    หน้าที่: ดำเนินการ CRUD ข้อมูล ChatSession และ ChatMessage ใน MongoDB
    """

    @abstractmethod
    async def create_session(self, session: ChatSession) -> ChatSession:
        "Create chat session"

    @abstractmethod
    async def get_session_by_id(
        self, session_id: str, user_id: str
    ) -> ChatSession | None:
        "Get chat session"

    @abstractmethod
    async def list_by_user_id(
        self,
        user_id: str,
        chatbot_id: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ChatSession]:
        "Get chat sessionlist"

    @abstractmethod
    async def append_message(
        self, session_id: str, user_id: str, message: ChatMessage
    ) -> ChatSession | None:
        "Assert message"

    @abstractmethod
    async def update(
        self, session_id: str, user_id: str, update_data: dict[str, Any]
    ) -> ChatSession | None:
        "Update session"

    @abstractmethod
    async def delete_session(self, session_id: str, user_id: str) -> bool:
        "Delete chat session"
