import asyncio
import logging
from typing import Any

from pinecone import GrpcIndex, Index

logger = logging.getLogger(__name__)


class PineconeRepository:
    """Implementation สำหรับบันทึกเอกสารลง Pinecone DB"""

    def __init__(self, pc_index: Index | GrpcIndex) -> None:
        self.index = pc_index

    async def upsert_vectors_with_namespace(
        self, records: list[Any], user_id: str, chatbot_id: str | None = None
    ) -> None:
        try:
            namespace = f"tenant_{user_id}_{chatbot_id}"
            self.index.upsert(vectors=records, namespace=namespace)
        except Exception as e:
            logger.error(
                f"Failed to upsert vectors from Pinecone for chatbot_id {chatbot_id}: {e}"
            )
            raise e

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

    async def delete_by_file_id(
        self, file_id: str, user_id: str, chatbot_id: str
    ) -> None:
        """
        ลบ Vectors ทั้งหมดที่ตรงกับ file_id ออกจาก Pinecone
        โดยใช้ Metadata Filtering หรือ Namespace เพื่อความปลอดภัยในระดับ Multi-tenant Isolation[cite: 1, 2, 3]
        """
        try:
            namespace = f"tenant_{user_id}_{chatbot_id}"

            filter_query = {
                "file_id": {"$eq": file_id},
                "user_id": {"$eq": user_id},
            }

            if chatbot_id:
                filter_query["chatbot_id"] = {"$eq": chatbot_id}

            self.index.delete(filter=filter_query, namespace=namespace)

            logger.info(
                f"Successfully deleted vectors for file_id: {file_id} (user_id: {user_id})"
            )

        except Exception as e:
            logger.error(
                f"Failed to delete vectors from Pinecone for file_id {file_id}: {e}"
            )
            raise e

    async def search_similar_multi_tenant(
        self,
        query_vector: list[float],
        user_id: str,
        chatbot_id: str,
        top_k: int = 5,
        filter_metadata: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        ค้นหา Vector ที่มีความคล้ายคลึงที่สุดตาม query_vector
        บังคับกรองข้อมูลด้วย user_id และ chatbot_id เพื่อรักษาความปลอดภัย Multi-tenant Isolation
        """
        try:
            # 1. กำหนด Multi-tenant Metadata Filter เป็นค่าพื้นฐาน[cite: 1, 3]
            query_filter: dict[str, Any] = {
                "user_id": {"$eq": user_id},
                "chatbot_id": {"$eq": chatbot_id},
            }

            # 2. รวม Filter เพิ่มเติมที่อาจถูกส่งมา (เช่น กรองตาม file_id)
            if filter_metadata:
                query_filter.update(filter_metadata)

            # 3. กำหนด Namespace ตาม Tenant (ใช้แบบ Namespace Pattern)
            namespace = f"tenant_{user_id}_{chatbot_id}"

            # 4. เรียกค้นหาบน Pinecone Index (รวม text_content และ metadata กลับมาด้วย)
            response = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                filter=query_filter,
                namespace=namespace,
            )

            results = []
            for match in response.get("matches", []):
                results.append(
                    {
                        "id": match.get("id"),
                        "score": match.get("score"),
                        "metadata": match.get("metadata", {}),
                    }
                )

            return results

        except Exception as e:
            logger.error(f"Error querying Pinecone vector store: {e}")
            raise e
