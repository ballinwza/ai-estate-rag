import asyncio
from typing import Any

from pinecone import GrpcIndex, Index


class PineconeRepository:
    """Implementation สำหรับบันทึกเอกสารลง Pinecone DB"""

    def __init__(self, pc_index: Index | GrpcIndex) -> None:
        self.index = pc_index

    async def upsert_vectors(
        self,
        document_id: str,
        chunks: list[str],
        embeddings: list[list[float]],
        extra_metadata: dict[str, Any] | None = None,
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("จำนวน chunks และ embeddings ต้องเท่ากัน")

        extra_meta = extra_metadata or {}
        vectors_to_upsert = []

        for idx, (chunk, vector_values) in enumerate(zip(chunks, embeddings)):
            vector_id = f"{document_id}_{idx}"

            metadata = {
                "document_id": str(document_id),
                "chunk_index": idx,
                "text": chunk,
                **extra_meta,  # แนบ metadata อื่นๆ เช่น filename, content_type เพิ่มเติมได้
            }

            vectors_to_upsert.append(
                {
                    "id": vector_id,
                    "values": vector_values,
                    "metadata": metadata,
                }
            )

        # Upsert ข้อมูลขึ้น Pinecone Index
        # หมายเหตุ: Pinecone SDK เป็น Sync Call หากต้องการความลื่นไหลแบบ Async สามารถรันผ่าน threadpool ได้
        self.index.upsert(vectors=vectors_to_upsert)

    async def search_similar(
        self, query_vector: list[float], top_k: int = 5
    ) -> list[dict[str, Any]]:
        response = self.index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True,
        )
        return response.to_dict().get("matches", [])

    async def search_similar_document_ids(
        self, query_vector: list[float], top_k: int = 5
    ) -> list[str]:
        # รัน Sync function บน Executor เพื่อให้รองรับ Async/Await
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                namespace="__default__",
            ),
        )

        matched_doc_ids = []
        # 2. ดึงค่าจาก field 'document_id' ใน metadata
        for match in response.matches:
            if match.metadata and "document_id" in match.metadata:
                matched_doc_ids.append(str(match.metadata["document_id"]))

        return matched_doc_ids
