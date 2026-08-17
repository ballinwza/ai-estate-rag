from datetime import datetime, timezone
from typing import Any

from app.domain.entities.knowledge_file import (
    CreateKnowledgeFile,
    DeleteKnowledgeFile,
    GetKnowledgeFile,
    ListKnowledgeFiles,
)
from app.domain.entities.multi_tenant_doc import (
    Chunk,
    FileStatus,
    KnowledgeFiles,
    MetadataVectorRecord,
)
from app.domain.repositories.multi_tenant.knowledge_file_repository import (
    KnowledgeFileRepository,
)
from app.infrastructure.llm.chunker import ChunkerService
from app.infrastructure.llm.embedder import EmbedderService
from app.infrastructure.llm.llm import LlmService
from app.infrastructure.persistence.mongodb.knowledge_file_repository import (
    MongoKnowledgeFileRepository,
)
from app.infrastructure.persistence.vector_store.pinecone_repository import (
    PineconeRepository,
)
from app.schemas.multi_tenant import VectorRecordSchema


class CreateKnowledgeDocUseCase:
    """
    Flow การทำงาน:
    1. สร้าง Record ไฟล์ใน MongoDB (สถานะ PENDING)
    2. Parse เอกสารและตัดแบ่ง Chunk
    3. สร้าง Vector Embeddings ด้วย Gemini
    4. บันทึก Vector ลง Pinecone (ฉีด user_id/chatbot_id เพื่อทำ Multi-tenant Filter)
    5. อัปเดตข้อมูล Chunk ย้อนกลับใน MongoDB และเปลี่ยนสถานะเป็น COMPLETED
    """

    def __init__(
        self,
        parser_service: LlmService,
        mongo_repo: MongoKnowledgeFileRepository,
        pinecone_repo: PineconeRepository,
        embedder_service: EmbedderService,
        chunker_service: ChunkerService,
    ):

        self.embedder_service = embedder_service
        self.parser_service = parser_service
        self.chunker_service = chunker_service
        self.mongo_repo = mongo_repo
        self.pinecone_repo = pinecone_repo

    async def execute(self, dto: CreateKnowledgeFile) -> KnowledgeFiles:
        # 1. สร้าง Record เริ่มต้นใน MongoDB
        initial_knowledge_file = KnowledgeFiles(
            user_id=dto.user_id,
            chatbot_id=dto.chatbot_id,
            filename=dto.filename,
            file_type=dto.file_type,
            file_size_bytes=len(dto.file_content),
            status=FileStatus.PENDING,
        )

        saved_file = await self.mongo_repo.create(initial_knowledge_file)
        file_id = str(saved_file.id)

        # 1. สกัดข้อความจากเอกสาร PDF หรือ รูปภาพ
        extracted_doc = await self.parser_service.parse_chunk_file(
            dto.file_content, dto.filename, dto.file_type
        )
        try:
            # 2. Parse และทำ Chunking
            chunks: list[Chunk] = await self.chunker_service.process_and_chunk(
                extracted_doc
            )

            # 3. สร้าง Embeddings สำหรับทุก Chunk ด้วย Gemini
            embeddings = await self.embedder_service.embed_chunks(
                chunks=chunks,
                user_id=dto.user_id,
                chatbot_id=dto.chatbot_id,
                file_id=file_id,
                filename=dto.filename,
            )

            # 4. เตรียมข้อมูล VectorRecord และบันทึกลง Pinecone
            dump_chunks: list[dict[str, Any]] = []

            vector_records: list[dict[str, Any]] = []

            for idx, (chunk, vector_values) in enumerate(zip(chunks, embeddings)):
                vector_id = f"{file_id}_{idx}"

                metadata = MetadataVectorRecord(
                    user_id=dto.user_id,
                    chatbot_id=dto.chatbot_id,
                    file_id=file_id,
                    chunk_index=idx,
                    text_content=chunk.text_content,
                    page_number=chunk.page_number,
                    filename=dto.filename,
                )

                chunk_for_doc = Chunk(
                    vector_id=vector_id,
                    chunk_index=idx,
                    text_content=chunk.text_content,
                    page_number=chunk.page_number,
                    token_count=1,
                )
                dump_chunks.append(
                    chunk_for_doc.model_dump(by_alias=True, exclude_none=True)
                )

                vectorRecord = VectorRecordSchema(
                    id=vector_id,
                    values=vector_values.values,
                    metadata=metadata.model_dump(by_alias=True, exclude_none=True),
                )

                vector_records.append(
                    vectorRecord.model_dump(by_alias=True, exclude_none=True)
                )

            await self.pinecone_repo.upsert_vectors_with_namespace(
                vector_records, user_id=dto.user_id, chatbot_id=dto.chatbot_id
            )

            total_pages = max([c.page_number for c in chunks], default=1)
            updated_data = {
                "chunks": dump_chunks,
                "total_chunks": len(chunks),
                "total_page": total_pages,
                "status": FileStatus.COMPLETED,
                "text_content": extracted_doc.get("full_text", "Nothing"),
            }

            saved_sucessed = await self.mongo_repo.update(
                file_id=file_id, user_id=dto.user_id, update_data=updated_data
            )
            if not saved_sucessed:
                raise Exception(f"File with id {file_id} not found")

            return saved_sucessed

        except Exception as e:
            fail_data = {
                "status": FileStatus.FAILED,  # [cite: 2]
                "error_message": str(e),  # [cite: 2]
                "updated_at": datetime.now(timezone.utc),
            }
            await self.mongo_repo.update(
                file_id=file_id, user_id=dto.user_id, update_data=fail_data
            )
            raise e


class GetKnowledgeDocUseCase:
    """Use Case สำหรับดึงข้อมูลเอกสารรายไฟล์ พร้อมตรวจสอบ Owner (Multi-tenant)"""

    def __init__(self, file_repo: KnowledgeFileRepository):
        self.file_repo = file_repo

    async def execute(self, dto: GetKnowledgeFile) -> KnowledgeFiles:
        file_doc = await self.file_repo.get_by_id(file_id=dto.id, user_id=dto.user_id)
        if not file_doc:
            raise ValueError(
                f"Knowledge file with ID '{dto.id}' not found for this user."
            )
        return file_doc


class ListKnowledgeDocsUseCase:
    """Use Case สำหรับดึงรายการเอกสารทั้งหมดภายใต้ Chatbot นั้นๆ"""

    def __init__(self, file_repo: KnowledgeFileRepository):
        self.file_repo = file_repo

    async def execute(self, dto: ListKnowledgeFiles) -> list[KnowledgeFiles]:
        return await self.file_repo.list_by_chatbot_id(
            user_id=dto.user_id,
            chatbot_id=dto.chatbot_id,
            limit=dto.limit,
            offset=dto.offset,
        )


class DeleteKnowledgeDocUseCase:
    """Use Case สำหรับลบเอกสารทั้งใน MongoDB และ Vector DB (Pinecone)"""

    def __init__(
        self,
        file_repo: KnowledgeFileRepository,
        vector_repo: PineconeRepository,
    ):
        self.file_repo = file_repo
        self.vector_repo = vector_repo

    async def execute(self, dto: DeleteKnowledgeFile) -> bool:
        # 1. ตรวจสอบว่าไฟล์มีอยู่จริงหรือไม่
        file_doc = await self.file_repo.get_by_filter(
            {
                "chatbot_id": dto.chatbot_id,
                "user_id": dto.user_id,
            }
        )
        if not file_doc:
            raise ValueError(
                f"Knowledge file with ID '{dto.chatbot_id}' not found for this user."
            )

        # 2. ลบ Vectors ใน Vector DB ลบตาม file_id
        await self.vector_repo.delete_by_file_id(
            file_id=str(file_doc.id), user_id=dto.user_id, chatbot_id=dto.chatbot_id
        )

        # 3. ลบ Document Metadata ใน MongoDB
        return await self.file_repo.delete(file_id=dto.chatbot_id, user_id=dto.user_id)
