from datetime import datetime, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.entities.multi_tenant_doc import ChatbotBlueprint
from app.domain.repositories.multi_tenant.multi_tenant_repository import (
    MultiTenantChatbotRepository,
)


class MongoMultiTenantChatbotRepository(MultiTenantChatbotRepository):
    """
    Infrastructure Implementation สำหรับจัดการ Chatbot Blueprint บน MongoDB
    รองรับการกรองตาม user_id เสมอเพื่อรักษาความปลอดภัยระดับ Multi-tenant Isolation
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        # กำหนด Collection สำหรับเก็บข้อมูล Chatbot Blueprint
        self.collection = db["chatbot_blueprints"]

    async def create(self, chatbot: ChatbotBlueprint) -> ChatbotBlueprint:
        """สร้าง Chatbot Blueprint ใหม่ลงใน MongoDB"""
        # แปลง Pydantic Model เป็น dict (exclude _id หากเป็น None เพื่อให้ Mongo Gen ให้อัตโนมัติ)
        chatbot_dict = chatbot.model_dump(by_alias=True, exclude_none=True)

        result = await self.collection.insert_one(chatbot_dict)

        # คืนค่า Blueprint พร้อม id ที่ได้สร้างจาก MongoDB
        chatbot.id = str(result.inserted_id)
        return chatbot

    async def get_by_id(self, chatbot_id: str, user_id: str) -> ChatbotBlueprint | None:
        """ดึงข้อมูล Chatbot Blueprint ตาม id โดยต้องระบุ user_id ของ owner เสมอ"""
        if not ObjectId.is_valid(chatbot_id):
            return None

        document = await self.collection.find_one(
            {
                "_id": ObjectId(chatbot_id),
                "user_id": user_id,  # Multi-tenant Safety Filter
            }
        )

        if not document:
            return None

        # แปลง Object _id ของ MongoDB ให้เป็น string ก่อนป้อนเข้า Pydantic Model
        document["_id"] = str(document["_id"])
        return ChatbotBlueprint(**document)

    async def list_by_user_id(
        self, user_id: str, limit: int = 100, offset: int = 0
    ) -> list[ChatbotBlueprint]:
        """ดึงรายการ Chatbot Blueprint ทั้งหมดของ user นั้นๆ"""
        cursor = (
            self.collection.find({"user_id": user_id})
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )

        chatbots = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            chatbots.append(ChatbotBlueprint(**doc))

        return chatbots

    async def update(
        self, chatbot_id: str, user_id: str, update_data: dict
    ) -> ChatbotBlueprint | None:
        """อัปเดตข้อมูล Chatbot Blueprint Specific Field (เช่น name, description, system_prompt)"""
        if not ObjectId.is_valid(chatbot_id):
            return None

        # อัปเดตเวลา updated_at เป็นปัจจุบัน
        update_data["updated_at"] = datetime.now(timezone.utc)

        updated_doc = await self.collection.find_one_and_update(
            filter={
                "_id": ObjectId(chatbot_id),
                "user_id": user_id,  # Multi-tenant Safety Filter
            },
            update={"$set": update_data},
            return_document=True,  # คืนค่า document หลังอัปเดตเรียบร้อยแล้ว
        )

        if not updated_doc:
            return None

        updated_doc["_id"] = str(updated_doc["_id"])
        return ChatbotBlueprint(**updated_doc)

    async def delete(self, chatbot_id: str, user_id: str) -> bool:
        """ลบ Chatbot Blueprint ออกจากระบบ"""
        if not ObjectId.is_valid(chatbot_id):
            return False

        result = await self.collection.delete_one(
            {
                "_id": ObjectId(chatbot_id),
                "user_id": user_id,  # Multi-tenant Safety Filter
            }
        )

        return result.deleted_count > 0
