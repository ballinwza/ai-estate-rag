import logging
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult

logger = logging.getLogger(__name__)


class MongoDocumentRepository:
    """Implementation สำหรับบันทึกเอกสารลง MongoDB"""

    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.collection = database["documents"]

    async def insert_document(self, document_data: dict) -> InsertOneResult:
        result = await self.collection.insert_one(document_data)
        return result

    async def update_by_filer(self, filter: dict, document_data: dict) -> UpdateResult:
        update_data = {"$set": document_data}

        result = await self.collection.update_one(filter, update_data)
        return result

    async def update_by_id(self, id: str, document_data: dict) -> UpdateResult:
        filter_query = {"_id": ObjectId(id)}
        update_data = {"$set": document_data}

        result = await self.collection.update_one(filter_query, update_data)

        return result

    async def update_by_filter_response(
        self, filter: dict, document_data: dict
    ) -> dict | None:
        update_data = {"$set": document_data}

        result = await self.collection.find_one_and_update(
            filter,
            update_data,
            return_document=ReturnDocument.AFTER,
        )
        result["_id"] = str(result["_id"])
        return result

    async def update_by_id_response(self, id: str, document_data: dict) -> dict | None:
        filter_query = {"_id": ObjectId(id)}
        update_data = {"$set": document_data}

        result = await self.collection.find_one_and_update(
            filter_query,
            update_data,
            return_document=ReturnDocument.AFTER,
        )
        result["_id"] = str(result["_id"])
        return result

    # Un generic
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

    async def get_documents_by_ids(self, matched_ids: list[str]) -> list[str]:
        object_ids = [ObjectId(doc_id) for doc_id in matched_ids]

        cursor = self.collection.find({"_id": {"$in": object_ids}})

        # ต้องใช้ async for เพื่อดึงข้อมูลเข้า Dictionary
        doc_map = {}
        async for doc in cursor:
            doc_map[str(doc["_id"])] = doc.get("full_text", "")

        # เรียงลำดับตาม Pinecone
        ordered_documents = [
            doc_map[doc_id] for doc_id in matched_ids if doc_id in doc_map
        ]

        return ordered_documents

    async def get_documents_source_by_ids(
        self, matched_ids: list[str]
    ) -> list[dict[str, Any]]:
        # 1. แปลง string IDs เป็น ObjectId
        object_ids = [ObjectId(doc_id) for doc_id in matched_ids]

        # 2. ค้นหาเอกสารจาก MongoDB
        cursor = self.collection.find({"_id": {"$in": object_ids}})

        doc_map = {}
        async for doc in cursor:
            # ดึง page_number จากหน้าแรก (หรือลูปดึงหากมีหลายหน้า)
            pages = doc.get("pages", [])
            page_num = pages[0].get("page_number", 1) if pages else 1

            # ดึงข้อมูลพร้อม Metadata ที่ต้องการนำไปใช้อ้างอิง
            doc_map[str(doc["_id"])] = {
                "filename": doc.get("filename", "Unknown"),
                "page_number": page_num,
                "full_text": doc.get("full_text", ""),
            }

        # 3. จัดเรียงลำดับตามความเกี่ยวข้องจาก Pinecone
        ordered_documents = [
            doc_map[doc_id] for doc_id in matched_ids if doc_id in doc_map
        ]

        return ordered_documents
