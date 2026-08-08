import logging

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.results import DeleteResult

from app.domain.repositories.mongodb_repository import MongoDocumentRepository

logger = logging.getLogger(__name__)


class MongoDocumentRepositoryImpl(MongoDocumentRepository):
    """Implementation สำหรับบันทึกเอกสารลง MongoDB"""

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.collection = database["documents"]

    async def save_document(self, document_data: dict) -> str:
        result = await self.collection.insert_one(document_data)
        return str(result.inserted_id)

    async def delete_document(self, document_id: str | ObjectId) -> bool:
        """
        ลบเอกสารออกจาก MongoDB ตาม document_id
        ใช้สำหรับการ Rollback เมื่อการประมวลผลขั้นตอนอื่นล้มเหลว
        """
        try:
            # แปลง string ID ให้เป็น ObjectId
            obj_id = (
                ObjectId(document_id) if isinstance(document_id, str) else document_id
            )

            result: DeleteResult = await self.collection.delete_one({"_id": obj_id})

            if result.deleted_count > 0:
                logger.info(
                    f"Successfully rolled back (deleted) document: {document_id}"
                )
                return True
            else:
                logger.warning(
                    f"Document with id {document_id} not found for deletion."
                )
                return False

        except Exception as e:
            logger.error(
                f"Failed to delete document {document_id} during rollback: {e}"
            )
            raise RuntimeError(
                f"Failed to process vectors. Document creation rolled back. Cause: {e}"
            ) from e
