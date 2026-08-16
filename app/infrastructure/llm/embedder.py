from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import SecretStr

from app.domain.entities.multi_tenant_doc import (
    Chunk,
    MetadataVectorRecord,
    VectorRecord,
)


class EmbedderService:
    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-text-embedding-001",
        output_dimensionality: int = 768,
    ) -> None:
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=model_name,
            api_key=SecretStr(api_key),
            output_dimensionality=output_dimensionality,
        )

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """สร้าง เวกเตอร์ พร้อมกันหลายๆ ข้อความ (Async Batch)"""
        if not texts:
            return []
        return await self.embeddings.aembed_documents(texts)

    async def embed_query(self, text: str) -> list[float]:
        """สร้าง เวกเตอร์ สำหรับข้อความคำถามเดียว"""
        if not text:
            return []
        return await self.embeddings.aembed_query(text)

    async def embed_chunks(
        self,
        chunks: list[Chunk],
        user_id: str,
        chatbot_id: str,
        file_id: str,
        filename: str,
    ) -> list[VectorRecord]:
        """
        รับ list[Chunk] จาก process_and_chunk แล้วทำการ:
        1. ดึงเฉพาะ text_content ออกมาเป็น list[str]
        2. เรียกใช้ embed_documents (แบบ Async) เพื่อแปลงเป็น Vector Embeddings (list[float])
        3. สร้าง VectorRecord พร้อม MetadataVectorRecord ห่อกลับคืนไป
        """
        if not chunks:
            return []

        # 1. รวบรวมข้อความทั้งหมดจาก Chunks เพื่อเตรียมทำ Batch Embedding
        texts_to_embed = [chunk.text_content for chunk in chunks]

        # 2. ใช้ aembed_documents (Async) สำหรับประมวลผลรายการข้อความก้อนใหญ่พร้อมกัน
        vectors_list: list[list[float]] = await self.embeddings.aembed_documents(
            texts_to_embed
        )

        # 3. ประกอบข้อมูลกลับเป็น list[VectorRecord] ตาม Schema
        vector_records: list[VectorRecord] = []

        for chunk, vector_values in zip(chunks, vectors_list):
            # กำหนด Unique Vector ID สำหรับ Pinecone (เช่น fileId_chunkIndex)
            unique_vector_id = f"{file_id}_chunk_{chunk.chunk_index}"

            # อัปเดต vector_id กลับเข้าไปใน Chunk Object
            chunk.vector_id = unique_vector_id

            # สร้าง Metadata
            metadata = MetadataVectorRecord(
                user_id=user_id,
                chatbot_id=chatbot_id,
                file_id=str(file_id),
                filename=filename,
                chunk_index=chunk.chunk_index,
                text_content=chunk.text_content,
                page_number=chunk.page_number,
            )

            # สร้าง VectorRecord
            record = VectorRecord(
                id=unique_vector_id,
                values=vector_values,  # list[float]
                metadata=metadata,
            )

            vector_records.append(record)

        return vector_records
