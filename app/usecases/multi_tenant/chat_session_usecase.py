import logging

from app.domain.entities.chat_session import (
    AddChatMessageDTO,
    ChatMessage,
    ChatSession,
    CreateChatSessionDTO,
    GetChatHistoryDTO,
)
from app.domain.repositories.multi_tenant.chat_session_repository import (
    ChatSessionRepository,
)

logger = logging.getLogger("grpc")


class CreateChatSessionUseCase:
    """
    Use Case: สร้างห้องสนทนาใหม่ (Chat Session)
    """

    def __init__(self, session_repo: ChatSessionRepository):
        self.session_repo = session_repo

    async def execute(self, dto: CreateChatSessionDTO) -> "ChatSession":
        logger.info(
            f"Creating chat session for user: {dto.user_id}, chatbot: {dto.chatbot_id}"
        )

        # นำ Schema ChatSession มาสร้าง instance
        # from app.domain.entities import ChatSession
        new_session = ChatSession(
            user_id=dto.user_id,
            chatbot_id=dto.chatbot_id,
            session_title=dto.session_title or "New Chat",
            messages=[],
        )

        saved_session = await self.session_repo.create_session(new_session)
        return saved_session


class AddChatMessageUseCase:
    """
    Use Case: บันทึกข้อความ (Message) ลงใน Session
    """

    def __init__(self, session_repo: ChatSessionRepository):
        self.session_repo = session_repo

    async def execute(self, dto: AddChatMessageDTO) -> ChatMessage:
        logger.info(f"Appending message to session: {dto.session_id}")

        # ตรวจสอบว่า Session มีอยู่จริงและเป็นของผู้ใช้คนนี้หรือไม่
        session = await self.session_repo.get_session_by_id(dto.session_id, dto.user_id)
        if not session:
            raise ValueError(
                f"Chat session {dto.session_id} not found for user {dto.user_id}"
            )

        # from app.domain.entities import ChatMessage
        new_message = ChatMessage(role=dto.role, content=dto.content)

        success = await self.session_repo.append_message(
            dto.session_id, dto.user_id, new_message
        )
        if not success:
            raise RuntimeError(f"Failed to append message to session {dto.session_id}")

        return new_message


class GetChatHistoryUseCase:
    """
    Use Case: ดึงประวัติการคุยทั้งหมดใน Session
    """

    def __init__(self, session_repo: ChatSessionRepository):
        self.session_repo = session_repo

    async def execute(self, dto: GetChatHistoryDTO) -> list[ChatMessage]:
        session = await self.session_repo.get_session_by_id(dto.session_id, dto.user_id)
        if not session:
            raise ValueError(f"Chat session {dto.session_id} not found")

        return session.messages


class GetChatSessionUseCase:
    """
    Use Case: ดึงข้อมูล ChatSession สมบูรณ์ (รวมทั้ง Header ข้อมูลห้อง และ Messages)
    """

    def __init__(self, session_repo: ChatSessionRepository):
        self.session_repo = session_repo

    async def execute(self, session_id: str, user_id: str) -> ChatSession | None:
        session = await self.session_repo.get_session_by_id(
            session_id=session_id, user_id=user_id
        )
        if not session:
            raise ValueError(f"Chat session {session_id} not found for user {user_id}")
        return session


class ListUserChatSessionsUseCase:
    """
    Use Case: ดึงรายการห้องสนทนาทั้งหมดของผู้ใช้ (เลือก Filter ตาม Chatbot ได้)
    """

    def __init__(self, session_repo: ChatSessionRepository):
        self.session_repo = session_repo

    async def execute(
        self, user_id: str, chatbot_id: str | None = None
    ) -> list[ChatSession]:
        return await self.session_repo.list_by_user_id(
            user_id=user_id, chatbot_id=chatbot_id
        )


class DeleteChatSessionUseCase:
    """
    Use Case: ลบห้องสนทนา
    """

    def __init__(self, session_repo: ChatSessionRepository):
        self.session_repo = session_repo

    async def execute(self, session_id: str, user_id: str) -> bool:
        logger.info(f"Deleting chat session: {session_id} for user: {user_id}")
        return await self.session_repo.delete_session(
            session_id=session_id, user_id=user_id
        )
