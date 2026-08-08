import logging
from typing import Any

from pinecone import GrpcIndex, Index, Pinecone

from app.core.config import settings

logger = logging.getLogger(__name__)


class PineconeDatabase:
    client: Pinecone | None = None
    index: Any = None


pinecone_instance = PineconeDatabase()


async def connect_to_pinecone() -> None:
    """เปิดการเชื่อมต่อ Pinecone Client และโหลด Index Instance"""
    logger.info("Connecting to Pinecone...")

    # 1. ตรวจสอบ API Key
    if not settings.PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY is not configured in settings/env")

    # 2. ตรวจสอบ Index Name (ป้องกันปัญหา PineconeValueError)
    if not settings.PINECONE_INDEX_NAME:
        raise ValueError("PINECONE_INDEX_NAME is not configured in settings/env")

    pinecone_instance.client = Pinecone(api_key=settings.PINECONE_API_KEY)

    # 3. ระบุชื่อแบบ Keyword Argument (name=...)
    pinecone_instance.index = pinecone_instance.client.Index(
        name=settings.PINECONE_INDEX_NAME
    )
    logger.info(
        f"Successfully connected to Pinecone index: '{settings.PINECONE_INDEX_NAME}'!"
    )


async def close_pinecone_connection() -> None:
    """ปิดการเชื่อมต่อ Pinecone Client"""
    logger.info("Closing Pinecone connection...")
    pinecone_instance.client = None
    pinecone_instance.index = None
    logger.info("Pinecone connection cleared.")


def get_pinecone_index() -> Index | GrpcIndex:
    """Dependency injection helper สำหรับเรียกใช้ Pinecone Index Instance"""
    if pinecone_instance.index is None:
        raise RuntimeError("Pinecone connection is not initialized.")
    return pinecone_instance.index
