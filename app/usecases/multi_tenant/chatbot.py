from datetime import datetime, timezone

from app.api.dto.multi_tenant_dto import (
    CreateMultiTenantChatbotDTO,
    DeleteMultiTenantChatbotDTO,
    GetMultiTenantChatbotDTO,
    ListMultiTenantChatbotsDTO,
    UpdateMultiTenantChatbotDTO,
)
from app.domain.entities.multi_tenant_doc import ChatbotBlueprint
from app.domain.repositories.multi_tenant.multi_tenant_repository import (
    MultiTenantChatbotRepository,
)


class CreateMultiTenantChatbotUseCase:
    """Use Case สำหรับการสร้าง Chatbot Blueprint ใหม่"""

    def __init__(self, chatbot_repo: MultiTenantChatbotRepository):
        self.chatbot_repo = chatbot_repo

    async def execute(self, dto: CreateMultiTenantChatbotDTO) -> ChatbotBlueprint:
        chatbot = ChatbotBlueprint(
            user_id=dto.user_id,
            name=dto.name,
            description=dto.description,
            system_prompt=dto.system_prompt,
        )
        return await self.chatbot_repo.create(chatbot)


class GetMultiTenantChatbotUseCase:
    """Use Case สำหรับดึงข้อมูล Chatbot Blueprint ตาม ID (พร้อมตรวจสอบ Owner)"""

    def __init__(self, chatbot_repo: MultiTenantChatbotRepository):
        self.chatbot_repo = chatbot_repo

    async def execute(self, dto: GetMultiTenantChatbotDTO) -> ChatbotBlueprint | None:
        chatbot = await self.chatbot_repo.get_by_id(
            chatbot_id=dto.chatbot_id, user_id=dto.user_id
        )
        if not chatbot:
            raise ValueError(
                f"Chatbot with ID '{dto.chatbot_id}' not found for this user."
            )
        return chatbot


class ListUserMultiTenantChatbotsUseCase:
    """Use Case สำหรับดึงรายการ Chatbot Blueprint ทั้งหมดของผู้ใช้งาน (Multi-tenant Filter)"""

    def __init__(self, chatbot_repo: MultiTenantChatbotRepository):
        self.chatbot_repo = chatbot_repo

    async def execute(self, dto: ListMultiTenantChatbotsDTO) -> list[ChatbotBlueprint]:
        return await self.chatbot_repo.list_by_user_id(
            user_id=dto.user_id, limit=dto.limit, offset=dto.offset
        )


class UpdateMultiTenantChatbotUseCase:
    """Use Case สำหรับแก้ไขข้อมูล Chatbot Blueprint ( name, description, system_prompt )"""

    def __init__(self, chatbot_repo: MultiTenantChatbotRepository):
        self.chatbot_repo = chatbot_repo

    async def execute(self, dto: UpdateMultiTenantChatbotDTO) -> ChatbotBlueprint:
        # เตรียมข้อมูลเฉพาะ Field ที่มีการส่งมาแก้ไข
        update_data = {}
        if dto.name is not None:
            update_data["name"] = dto.name
        if dto.description is not None:
            update_data["description"] = dto.description
        if dto.system_prompt is not None:
            update_data["system_prompt"] = dto.system_prompt

        if not update_data:
            raise ValueError("No fields provided to update.")

        # อัปเดต เวลา updated_at
        update_data["updated_at"] = datetime.now(timezone.utc)

        updated_chatbot = await self.chatbot_repo.update(
            chatbot_id=dto.chatbot_id, user_id=dto.user_id, update_data=update_data
        )

        if not updated_chatbot:
            raise ValueError(
                f"Chatbot with ID '{dto.chatbot_id}' not found or update failed."
            )

        return updated_chatbot


class DeleteMultiTenantChatbotUseCase:
    """Use Case สำหรับลบ Chatbot Blueprint"""

    def __init__(self, chatbot_repo: MultiTenantChatbotRepository):
        self.chatbot_repo = chatbot_repo

    async def execute(self, dto: DeleteMultiTenantChatbotDTO) -> bool:
        deleted = await self.chatbot_repo.delete(
            chatbot_id=dto.chatbot_id, user_id=dto.user_id
        )
        if not deleted:
            raise ValueError(f"Failed to delete chatbot with ID '{dto.chatbot_id}'.")
        return True
