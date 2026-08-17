from abc import ABC, abstractmethod

from app.domain.entities.multi_tenant_doc import ChatbotBlueprint


class MultiTenantChatbotRepository(ABC):
    """
    [ต้องสร้างเพิ่ม] Implement ใน Infrastructure Layer (เช่น mongodb_repository.py)
    หน้าที่: CRUD ข้อมูล Chatbot Blueprint ใน MongoDB
    """

    @abstractmethod
    async def create(self, chatbot: ChatbotBlueprint) -> ChatbotBlueprint:
        pass

    @abstractmethod
    async def get_by_id(self, chatbot_id: str, user_id: str) -> ChatbotBlueprint | None:
        pass

    @abstractmethod
    async def list_by_user_id(
        self, user_id: str, limit: int = 100, offset: int = 0
    ) -> list[ChatbotBlueprint]:
        pass

    @abstractmethod
    async def update(
        self, chatbot_id: str, user_id: str, update_data: dict
    ) -> ChatbotBlueprint | None:
        pass

    @abstractmethod
    async def delete(self, chatbot_id: str, user_id: str) -> bool:
        pass
