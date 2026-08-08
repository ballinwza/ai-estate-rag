import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class DatabaseSettings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "property_db"

    class Config:
        env_file = ".env"
        extra = "ignore"


class Database:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None


db_instance = Database()


async def connect_to_mongo() -> None:
    """เปิดการเชื่อมต่อ MongoDB Client"""
    settings = DatabaseSettings()
    logger.info("Connecting to MongoDB...")
    db_instance.client = AsyncIOMotorClient(
        settings.mongodb_uri,
        maxPoolSize=10,
        minPoolSize=1,
    )
    db_instance.db = db_instance.client[settings.mongodb_db_name]
    logger.info("Successfully connected to MongoDB!")


async def close_mongo_connection() -> None:
    """ปิดการเชื่อมต่อ MongoDB Client"""
    logger.info("Closing MongoDB connection...")
    if db_instance.client:
        db_instance.client.close()
        logger.info("MongoDB connection closed.")


def get_mongodb_database() -> AsyncIOMotorDatabase:
    """Dependency injection helper สำหรับเรียกใช้ Async Database Instance"""
    if db_instance.db is None:
        raise RuntimeError("Database connection is not initialized.")
    return db_instance.db
