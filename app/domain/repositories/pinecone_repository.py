from abc import ABC, abstractmethod
from typing import Any


class PineconeRepository(ABC):
    """Interface สำหรับการจัดการข้อมูลเอกสารในส่วน Persistence Layer"""

    @abstractmethod
    async def upsert_vectors(
        self,
        document_id: str,
        chunks: list[str],
        embeddings: list[list[float]],
        extra_metadata: dict[str, Any] | None = None,
    ) -> None:
        """แปลง chunks และ embeddings เพื่อบันทึกลง Vector Database"""

    @abstractmethod
    async def search_similar(
        self, query_vector: list[float], top_k: int = 5
    ) -> list[dict[str, Any]]:
        """ค้นหา vectors ที่ใกล้เคียงที่สุด"""
