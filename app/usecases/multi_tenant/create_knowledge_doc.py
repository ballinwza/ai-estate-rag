from typing import Any

from app.domain.entities.multi_tenant_doc import (
    Chunk,
    FileStatus,
    KnowledgeFiles,
    MetadataVectorRecord,
    VectorRecord,
)
from app.infrastructure.llm.chunker import ChunkerService
from app.infrastructure.llm.embedder import EmbedderService
from app.infrastructure.llm.llm import LlmService
from app.infrastructure.persistence.mongodb.document_repository import (
    MongoDocumentRepository,
)
from app.infrastructure.persistence.vector_store.pinecone_repository import (
    PineconeRepository,
)
from app.schemas.multi_tenant import IngestDocumentDTO


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
        mongo_repo: MongoDocumentRepository,
        pinecone_repo: PineconeRepository,
        embedder_service: EmbedderService,
        chunker_service: ChunkerService,
    ):

        self.embedder_service = embedder_service
        self.parser_service = parser_service
        self.chunker_service = chunker_service
        self.mongo_repo = mongo_repo
        self.pinecone_repo = pinecone_repo

    async def execute(self, dto: IngestDocumentDTO) -> KnowledgeFiles:
        # 1. สร้าง Record เริ่มต้นใน MongoDB

        initial_knowledge_file = KnowledgeFiles(
            user_id=dto.user_id,
            chatbot_id=dto.chatbot_id,
            filename=dto.filename,
            file_type=dto.file_type,
            file_size_bytes=len(dto.file_content),
            status=FileStatus.PENDING,
        )

        knowledge_file_model = initial_knowledge_file.model_dump(
            by_alias=True, exclude_none=True
        )

        saved_file = await self.mongo_repo.insert_document(knowledge_file_model)
        file_id = str(saved_file.inserted_id)

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

                test = VectorRecord(
                    id=vector_id,
                    values=vector_values.values,
                    metadata=metadata.model_dump(by_alias=True, exclude_none=True),
                )

                vector_records.append(test.model_dump(by_alias=True, exclude_none=True))

            # แยก Namespace ตาม tenant (เช่น chatbot_id หรือ user_id)
            namespace = f"tenant_{dto.user_id}_{dto.chatbot_id}"

            await self.pinecone_repo.upsert_vectors_with_namespace(
                vector_records, namespace=namespace
            )

            updated_data = {
                "chunks": dump_chunks,
                "total_chunks": len(chunks),
                "status": FileStatus.COMPLETED,
                "text_content": extracted_doc.get("full_text", "Nothing"),
            }

            saved_sucessed = await self.mongo_repo.update_by_id_response(
                file_id, updated_data
            )
            if not saved_sucessed:
                raise Exception(f"File with id {file_id} not found")

            # TODO: แปลง id กลับมาเป็น str ก่อน

            result = KnowledgeFiles(**saved_sucessed)
            return result

        except Exception as e:
            # เก็บ Error และเปลี่ยนสถานะเป็น FAILED
            await self.mongo_repo.update_by_id(
                file_id, {"status": FileStatus.FAILED, "error_message": str(e)}
            )
            raise e
