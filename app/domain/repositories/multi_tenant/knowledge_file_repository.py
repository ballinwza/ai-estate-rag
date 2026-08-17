from abc import ABC, abstractmethod
from typing import Any

from app.domain.entities.multi_tenant_doc import KnowledgeFiles


class KnowledgeFileRepository(ABC):
    @abstractmethod
    async def create(self, file: KnowledgeFiles) -> KnowledgeFiles:
        """สร้างเอกสารใหม่ใน MongoDB"""

    @abstractmethod
    async def get_by_id(self, file_id: str, user_id: str) -> KnowledgeFiles | None:
        """ดึงเอกสารตาม file_id และ user_id (Multi-tenant check)"""

    @abstractmethod
    async def get_by_filter(self, filter: dict[str, Any]) -> KnowledgeFiles | None:
        """ดึงเอกสารตาม file_id และ user_id (Multi-tenant check)"""

    @abstractmethod
    async def list_by_chatbot_id(
        self, user_id: str, chatbot_id: str, limit: int, offset: int
    ) -> list[KnowledgeFiles]:
        """ดึงรายการเอกสารทั้งหมดของ chatbot ตาม user_id"""

    @abstractmethod
    async def update(
        self, file_id: str, user_id: str, update_data: dict[str, Any]
    ) -> KnowledgeFiles | None:
        """อัปเดตข้อมูลเอกสาร"""

    @abstractmethod
    async def delete(self, file_id: str, user_id: str) -> bool:
        """ลบเอกสารออกจาก Database"""
