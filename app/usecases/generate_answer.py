from app.infrastructure.llm.embedder import EmbedderService
from app.infrastructure.llm.llm import LlmService
from app.infrastructure.persistence.mongodb.document_repository import (
    MongoDocumentRepository,
)
from app.infrastructure.persistence.vector_store.pinecone_repository import (
    PineconeRepository,
)
from app.schemas.chat import ChatResponse


class GenerateAnswerUseCase:
    def __init__(
        self,
        vector_repo: PineconeRepository,
        mongo_repo: MongoDocumentRepository,
        embedder: EmbedderService,
        llm: LlmService,
    ) -> None:
        self.vector_repo = vector_repo
        self.mongo_repo = mongo_repo
        self.embedder = embedder
        self.llm = llm

    async def execute(self, query_text: str, top_k: int = 3) -> ChatResponse:
        # 1. แปลงคำถามให้เป็น Vector
        query_vector = await self.embedder.embed_query(query_text)

        # 2. ค้นหา Chunks ที่เกี่ยวข้องจาก Pinecone
        matched_ids = await self.vector_repo.search_similar_document_ids(
            query_vector=query_vector, top_k=top_k
        )

        if not matched_ids:
            return ChatResponse(message="ไม่พบข้อมูลที่เกี่ยวข้อง")

        full_documents = await self.mongo_repo.get_documents_source_by_ids(matched_ids)

        formatted_contexts = []
        for doc in full_documents:
            context_item = (
                f"[Source: {doc['filename']} | Page: {doc['page_number']}]\n"
                f"Content:\n{doc['full_text']}"
            )
            formatted_contexts.append(context_item)

        context_str = "\n\n---\n\n".join(formatted_contexts)

        # 4. สร้าง Prompt ส่งให้ LLM ตอบคำถาม
        prompt = f"""คุณเป็นผู้ช่วยตอบคำถาม โปรดตอบคำถามโดยอ้างอิงจากข้อมูลบริบท (Context) ที่กำหนดให้อย่างถูกต้อง
[Instruction]
-สร้างคำตอบเป็น list อ่านแล้วเข้าใจง่าย
-ความยาวคำตอบไม่เกิน 500คำ
-เป็นผู้หญิง พูดจาสุภาพ เรียบร้อย ตรงประเด็น
-ต้องอ้างอิงแหล่งที่มาของข้อมูล
-หากตอบไม่ได้ ไม่มีข้อมูล ให้บอกว่าตอบไม่ได้ ห้ามมั่วเด็ดขาด
-ให้ระบุที่มาของข้อมูล (Filename และ Page) ทุกครั้งอ้างอิงตอบคำถาม

[Context]
{context_str}

[Question]
{query_text}
"""
        response = await self.llm.get_llm_answer(prompt)

        return ChatResponse(message=response)
