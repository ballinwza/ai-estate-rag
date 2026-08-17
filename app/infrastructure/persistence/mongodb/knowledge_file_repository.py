import logging
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.entities.multi_tenant_doc import KnowledgeFiles
from app.domain.repositories.multi_tenant.knowledge_file_repository import (
    KnowledgeFileRepository,
)

logger = logging.getLogger(__name__)


class MongoKnowledgeFileRepository(KnowledgeFileRepository):
    """
    Infrastructure Implementation สำหรับจัดการ KnowledgeFiles บน MongoDB
    รองรับการกรองตาม user_id เสมอเพื่อรักษาความปลอดภัยระดับ Multi-tenant Isolation
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        # กำหนด Collection สำหรับเก็บข้อมูลเอกสารคลังความรู้
        self.collection = db["knowledge_files"]

    async def create(self, file: KnowledgeFiles) -> KnowledgeFiles:
        """
        สร้างเอกสารใหม่ลงใน MongoDB
        """
        # แปลง Pydantic Model เป็น dict
        # (exclude _id หากเป็น None เพื่อให้ MongoDB สร้าง ObjectId ให้อัตโนมัติ)
        file_dict = file.model_dump(by_alias=True, exclude_none=True)

        result = await self.collection.insert_one(file_dict)

        # กำหนด id ที่ได้รับการสร้างจาก MongoDB กลับเข้าไปใน Model
        file.id = str(result.inserted_id)
        return file

    async def get_by_id(self, file_id: str, user_id: str) -> KnowledgeFiles | None:
        """
        ดึงข้อมูลเอกสารตาม file_id โดยระบุ user_id ของ owner เสมอ (Multi-tenant Security Check)
        """
        if not ObjectId.is_valid(file_id):
            return None

        document = await self.collection.find_one(
            {
                "_id": ObjectId(file_id),
                "user_id": user_id,  # Multi-tenant Safety Filter
            }
        )

        if not document:
            return None

        # แปลง ObjectId เป็น string ก่อนส่งคืน Pydantic Model
        document["_id"] = str(document["_id"])
        return KnowledgeFiles(**document)

    async def get_by_filter(self, filter: dict[str, Any]) -> KnowledgeFiles | None:
        """
        ดึงข้อมูลเอกสารตาม file_id โดยระบุ user_id ของ owner เสมอ (Multi-tenant Security Check)
        """

        document = await self.collection.find_one(filter)

        if not document:
            return None

        # แปลง ObjectId เป็น string ก่อนส่งคืน Pydantic Model
        document["_id"] = str(document["_id"])
        return KnowledgeFiles(**document)

    async def list_by_chatbot_id(
        self, user_id: str, chatbot_id: str, limit: int = 20, offset: int = 0
    ) -> list[KnowledgeFiles]:
        """
        ดึงรายการเอกสารทั้งหมดของ chatbot_id ภายใต้ user_id นั้นๆ (พร้อม Pagination)
        """
        cursor = (
            self.collection.find(
                {
                    "user_id": user_id,  # Multi-tenant Filter
                    "chatbot_id": chatbot_id,
                }
            )
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )

        files: list[KnowledgeFiles] = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            files.append(KnowledgeFiles(**doc))

        return files

    async def update(
        self, file_id: str, user_id: str, update_data: dict[str, Any]
    ) -> KnowledgeFiles | None:
        """
        อัปเดตข้อมูลเอกสาร (เช่น เปลี่ยนสถานะเป็น PROCESSED, บันทึก chunks หรือ error_message)
        """
        if not ObjectId.is_valid(file_id):
            return None

        # อัปเดตเวลา updated_at เสมอเมื่อมีการแก้ไข
        update_data["updated_at"] = datetime.now(timezone.utc)

        # ป้องกันไม่ให้แก้มือในส่วน _id หรือ user_id Direct Key
        update_data.pop("_id", None)
        update_data.pop("id", None)

        result = await self.collection.find_one_and_update(
            {
                "_id": ObjectId(file_id),
                "user_id": user_id,  # Multi-tenant Safety Filter
            },
            {"$set": update_data},
            return_document=True,
        )

        if not result:
            return None

        result["_id"] = str(result["_id"])
        return KnowledgeFiles(**result)

    async def delete(self, file_id: str, user_id: str) -> bool:
        """
        ลบเอกสารออกจาก MongoDB
        """

        result = await self.collection.delete_one(
            {
                "chatbot_id": file_id,
                "user_id": user_id,
            }
        )

        return result.deleted_count > 0
