import logging
from typing import Any

from app.domain.entities.multi_tenant_doc import (
    MetadataVectorRecord,
    VectorRecord,
)
from app.domain.entities.rag import (
    RagResponse,
    RagSearchSimilarRequest,
    SearchResultItem,
)
from app.infrastructure.llm.embedder import EmbedderService
from app.infrastructure.llm.llm import LlmService
from app.infrastructure.persistence.mongodb.multi_tenant_repository import (
    MongoMultiTenantChatbotRepository,
)
from app.infrastructure.persistence.vector_store.pinecone_repository import (
    PineconeRepository,
)

logger = logging.getLogger(__name__)


class RagSearchSimilarUseCase:
    """
    Use Case สำหรับการทำ RAG (Retrieval-Augmented Generation):
    1. แปลง คำถาม (Query) เป็น Vector
    2. ค้นหา Context ที่เกี่ยวข้องที่สุดจาก Pinecone
    3. นำ Context ไปให้ LLM (Gemini) สรุปและสร้าง Message คำตอบ
    4. คืนค่า Message คำตอบพร้อมกับ Sources อ้างอิง
    """

    def __init__(
        self,
        pinecone_repo: PineconeRepository,
        embedder_service: EmbedderService,
        mongo_multi_tenant: MongoMultiTenantChatbotRepository,
        llm_service: LlmService,  # เพิ่ม LLM Service สำหรับสร้างคำตอบ
    ):
        self.pinecone_repo = pinecone_repo
        self.embedder_service = embedder_service
        self.llm_service = llm_service
        self.mongo_multi_tenant = mongo_multi_tenant

    async def execute(self, dto: RagSearchSimilarRequest) -> RagResponse:
        # 1. แปลง Query Text เป็น Vector Embedding
        query_vector: list[float] = await self.embedder_service.embed_query(
            dto.query_text
        )

        # 2. เตรียม Extra Metadata Filter กรณีระบุ file_id
        extra_filter = {}
        if dto.file_id:
            extra_filter["file_id"] = {"$eq": dto.file_id}

        # 3. ค้นหา Vectors ที่คล้ายกันจาก Pinecone Repository
        raw_matches = await self.pinecone_repo.search_similar_multi_tenant(
            query_vector=query_vector,
            user_id=dto.user_id,
            chatbot_id=dto.chatbot_id,
            top_k=dto.top_k,
            filter_metadata=extra_filter if extra_filter else None,
        )

        # 4. Extract Text Content สำหรับส่งให้ LLM และ Map เข้า Domain Models
        sources: list[SearchResultItem] = []
        context_texts: list[str] = []

        for match in raw_matches:
            raw_metadata: dict[str, Any] = match.get("metadata", {})
            text_content = raw_metadata.get("text_content", "")

            if text_content:
                context_texts.append(text_content)

            # Map MetadataVectorRecord
            metadata_record = MetadataVectorRecord(
                user_id=raw_metadata.get("user_id", dto.user_id),
                chatbot_id=raw_metadata.get("chatbot_id", dto.chatbot_id),
                file_id=raw_metadata.get("file_id", ""),
                chunk_index=int(raw_metadata.get("chunk_index", 0)),
                text_content=text_content,
                page_number=int(raw_metadata.get("page_number", 1)),
                filename=raw_metadata.get("filename", ""),
            )

            # Map VectorRecord
            vector_record = VectorRecord(
                id=match.get("id"),
                values=match.get("values", []),
                metadata=metadata_record,
            )

            sources.append(
                SearchResultItem(
                    score=float(match.get("score", 0.0)),
                    record=vector_record,
                )
            )

        chatbot = await self.mongo_multi_tenant.get_by_id(
            dto.chatbot_id, user_id=dto.user_id
        )
        system_promp = chatbot.system_prompt if chatbot else None

        # 5. ให้ LLM สร้าง Message คำตอบจาก Context ที่ค้นได้
        if not context_texts:
            answer_message = "ขออภัยครับ ไม่พบข้อมูลคลังความรู้ที่เกี่ยวข้องกับคำถามของคุณ"
        else:
            prompt = f"""คุณเป็นผู้ช่วยตอบคำถาม โปรดตอบคำถามโดยอ้างอิงจากข้อมูลบริบท (Context) ที่กำหนดให้อย่างถูกต้อง
            [Instruction]
            {system_promp}
            
            [Context]
            {context_texts}
            
            [Question]
            {dto.query_text}
            """

            answer_message = await self.llm_service.get_llm_answer(prompt)

        # 6. คืนค่าทั้ง Message คำตอบ และ Sources
        return RagResponse(
            answer_message=answer_message,
            sources=sources,
        )
