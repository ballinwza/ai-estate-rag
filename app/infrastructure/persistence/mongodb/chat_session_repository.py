import logging
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.entities.chat_session import ChatMessage, ChatSession
from app.domain.repositories.multi_tenant.chat_session_repository import (
    ChatSessionRepository,
)

logger = logging.getLogger(__name__)


class MongoChatSessionRepository(ChatSessionRepository):
    """
    Infrastructure Implementation สำหรับจัดการ ChatSession บน MongoDB
    รองรับ Multi-tenant Isolation ด้วยการกรอง user_id ในทุกๆ Query Operations
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        # กำหนด Collection สำหรับเก็บข้อมูลประวัติการคุย
        self.collection = db["chat_sessions"]

    async def create_session(self, session: ChatSession) -> ChatSession:
        """สร้าง ChatSession ใหม่ลงใน MongoDB"""
        session_dict = session.model_dump(by_alias=True, exclude_none=True)

        result = await self.collection.insert_one(session_dict)

        # กำหนด String ID ที่ถูกสร้างจาก MongoDB ให้กับ Entity
        session.id = str(result.inserted_id)
        return session

    async def get_session_by_id(
        self, session_id: str, user_id: str
    ) -> ChatSession | None:
        """ดึงข้อมูล ChatSession โดยต้องระบุ user_id ของ owner เสมอ (Multi-tenant Protection)"""
        if not ObjectId.is_valid(session_id):
            return None

        document = await self.collection.find_one(
            {
                "_id": ObjectId(session_id),
                "user_id": user_id,  # Multi-tenant Safety Filter
            }
        )

        if not document:
            return None

        document["_id"] = str(document["_id"])
        return ChatSession(**document)

    async def list_by_user_id(
        self,
        user_id: str,
        chatbot_id: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ChatSession]:
        """ดึงรายการ ChatSession ทั้งหมดของผู้ใช้ โดยสามารถ Filter ตาม chatbot_id เพิ่มเติมได้"""
        query: dict[str, Any] = {"user_id": user_id}
        if chatbot_id:
            query["chatbot_id"] = chatbot_id

        cursor = (
            self.collection.find(query)
            .sort("updated_at", -1)  # เรียงตามห้องที่มีความเคลื่อนไหวล่าสุด
            .skip(offset)
            .limit(limit)
        )

        sessions: list[ChatSession] = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            sessions.append(ChatSession(**doc))

        return sessions

    async def append_message(
        self, session_id: str, user_id: str, message: ChatMessage
    ) -> ChatSession | None:
        """
        บันทึก ChatMessage ใหม่ต่อท้ายอาร์เรย์ `messages` แบบ Atomic operation ($push)
        พร้อมอัปเดตเวลา `updated_at` ของ Session
        """
        if not ObjectId.is_valid(session_id):
            return None

        now = datetime.now(timezone.utc)
        message_dict = message.model_dump()

        result = await self.collection.find_one_and_update(
            {
                "_id": ObjectId(session_id),
                "user_id": user_id,  # Multi-tenant Safety Filter
            },
            {
                "$push": {"messages": message_dict},
                "$set": {"updated_at": now},
            },
            return_document=True,
        )

        if not result:
            return None

        result["_id"] = str(result["_id"])
        return ChatSession(**result)

    async def update(
        self, session_id: str, user_id: str, update_data: dict[str, Any]
    ) -> ChatSession | None:
        """อัปเดตข้อมูล Session เช่น session_title"""
        if not ObjectId.is_valid(session_id):
            return None

        update_data["updated_at"] = datetime.now(timezone.utc)

        # ป้องกันไม่ให้แก้ไข _id หรือ user_id โดยตรง
        update_data.pop("_id", None)
        update_data.pop("id", None)
        update_data.pop("user_id", None)

        result = await self.collection.find_one_and_update(
            {
                "_id": ObjectId(session_id),
                "user_id": user_id,  # Multi-tenant Safety Filter
            },
            {"$set": update_data},
            return_document=True,
        )

        if not result:
            return None

        result["_id"] = str(result["_id"])
        return ChatSession(**result)

    async def delete_session(self, session_id: str, user_id: str) -> bool:
        """ลบ ChatSession ตาม session_id และ user_id"""
        if not ObjectId.is_valid(session_id):
            return False

        result = await self.collection.delete_one(
            {
                "_id": ObjectId(session_id),
                "user_id": user_id,  # Multi-tenant Safety Filter
            }
        )

        return result.deleted_count > 0
