import logging
from datetime import datetime, timezone

from fastapi import UploadFile

from app.domain.entities.document import DocumentCreateSchema
from app.infrastructure.llm.chunker import ChunkerService
from app.infrastructure.llm.embedder import EmbedderService
from app.infrastructure.llm.llm import LlmService
from app.infrastructure.persistence.mongodb.document_repository import (
    MongoDocumentRepository,
)
from app.infrastructure.persistence.vector_store.pinecone_repository import (
    PineconeRepository,
)
from app.schemas.document import ProcessDocumentOutput

logger = logging.getLogger(__name__)


class ProcessDocumentUseCase:
    """Use Case สำหรับควบคุมขั้นตอนการอัปโหลด อ่านข้อความ และบันทึกลง Database"""

    def __init__(
        self,
        mongo_repo: MongoDocumentRepository,
        pinecone_repo: PineconeRepository,
        parser_service: LlmService,
        embedder_service: EmbedderService,
        chunker_service: ChunkerService,
    ) -> None:
        self.mongo_repo = mongo_repo
        self.pinecone_repo = pinecone_repo
        self.parser_service = parser_service
        self.embedder_service = embedder_service
        self.chunker_service = chunker_service

    async def execute(self, file: UploadFile) -> ProcessDocumentOutput:
        # 1. สกัดข้อความจากเอกสาร PDF หรือ รูปภาพ
        extracted_text = await self.parser_service.parse_file(file)

        # 2. บันทึกลง Database ผ่าน Repository Layer
        document_data = DocumentCreateSchema(
            filename=file.filename or "unknown",
            content_type=file.content_type or "unknown",
            total_pages=extracted_text.get("total_pages", 1),
            full_text=extracted_text.get("full_text", ""),
            pages=extracted_text.get("pages", []),
            created_at=datetime.now(timezone.utc),
        )
        chunks = await self.chunker_service.get_recursive(
            extracted_text.get("full_text", "unknow")
        )
        if not chunks:
            raise ValueError("Not have chunks")

        document_id = await self.mongo_repo.save_document(
            document_data.model_dump(by_alias=True)
        )

        # Pinecone upsert

        embeddings = await self.embedder_service.embed_documents(chunks)
        try:
            await self.pinecone_repo.upsert_vectors(
                document_id=document_id,
                chunks=chunks,
                embeddings=embeddings,
                extra_metadata={"filename": file.filename},
            )
        except Exception as e:
            logger.error(
                f"Pinecone upsert failed for doc_id {document_id}. Rolling back Mongo document. Error: {e}"
            )
            # 🔄 Rollback: ลบข้อมูลใน Mongo ทิ้งเพื่อไม่ให้เกิด Orphan Data
            await self.mongo_repo.delete_document(document_id)
            raise RuntimeError(
                f"Failed to process vectors. Document creation rolled back. Cause: {e}"
            ) from e

        # 3. ส่งคืนผลลัพธ์ข้อมูลตาม ProcessDocumentOutput Schema
        return ProcessDocumentOutput(
            document_id=str(document_id),
            filename=file.filename or "unknown",
            extracted_text=extracted_text.get("full_text", ""),  # ส่ง full_text กลับไป
            file_type=file.content_type or "unknown",
            # total_pages=extracted_text.get("total_pages", 1),  # (Optional) เพิ่มถ้าใน Output มี
            message="สกัดข้อความและจัดเก็บลง Database เรียบร้อยแล้ว",
        )
