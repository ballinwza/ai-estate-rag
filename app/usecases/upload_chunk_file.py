import io
import logging
from datetime import datetime, timezone

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


class UploadChunkFileUseCase:
    """Use Case สำหรับควบคุมขั้นตอนการอ่านข้อความ ทำ Embedding และบันทึกลง Database"""

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

    async def execute(
        self, file_bytes: bytes, filename: str, content_type: str = "application/pdf"
    ) -> ProcessDocumentOutput:

        # 1. สกัดข้อความจากเอกสาร PDF หรือ รูปภาพ (ส่งเป็น bytes หรือ BytesIO)
        # Note: ปรับ parse_file ให้รองรับ bytes หรือ io.BytesIO(file_bytes)
        file_obj = io.BytesIO(file_bytes)
        extracted_text = await self.parser_service.parse_chunk_file(
            file_obj, filename=filename, content_type=content_type
        )

        # 2. บันทึกลง Database ผ่าน Repository Layer
        document_data = DocumentCreateSchema(
            filename=filename or "unknown",
            content_type=content_type or "unknown",
            total_pages=extracted_text.get("total_pages", 1),
            full_text=extracted_text.get("full_text", ""),
            pages=extracted_text.get("pages", []),
            created_at=datetime.now(timezone.utc),
        )

        chunks = await self.chunker_service.get_recursive(
            extracted_text.get("full_text", "")
        )
        if not chunks:
            raise ValueError("No text chunks generated from the document.")

        document_id = await self.mongo_repo.save_document(
            document_data.model_dump(by_alias=True)
        )

        # 3. Pinecone upsert & Rollback handling
        embeddings = await self.embedder_service.embed_documents(chunks)
        try:
            await self.pinecone_repo.upsert_vectors(
                document_id=document_id,
                chunks=chunks,
                embeddings=embeddings,
                extra_metadata={"filename": filename},
            )
        except Exception as e:
            logger.error(
                f"Pinecone upsert failed for doc_id {document_id}. Rolling back Mongo document. Error: {e}"
            )
            await self.mongo_repo.delete_document(document_id)
            raise RuntimeError(
                f"Failed to process vectors. Document creation rolled back. Cause: {e}"
            ) from e

        # 4. ส่งคืนผลลัพธ์ข้อมูล
        return ProcessDocumentOutput(
            document_id=str(document_id),
            filename=filename or "unknown",
            extracted_text=extracted_text.get("full_text", ""),
            file_type=content_type or "unknown",
            message="สกัดข้อความและจัดเก็บลง Database/Pinecone เรียบร้อยแล้ว",
        )
