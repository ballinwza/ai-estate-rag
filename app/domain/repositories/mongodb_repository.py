from abc import ABC, abstractmethod

from bson import ObjectId


class MongoDocumentRepository(ABC):
    """Interface สำหรับการจัดการข้อมูลเอกสารในส่วน Persistence Layer"""

    @abstractmethod
    async def save_document(self, document_data: dict) -> str:
        """บันทึกข้อมูลเอกสารสกัดลง Database และคืนค่า document_id"""

    @abstractmethod
    async def delete_document(self, document_id: str | ObjectId) -> bool:
        """บันทึกข้อมูลเอกสารสกัดลง Database และคืนค่า document_id"""
