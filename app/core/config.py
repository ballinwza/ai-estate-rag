from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================================
    # 1. Application Settings (FastAPI & Server)
    # ==========================================
    PROJECT_NAME: str = "AI Estate RAG"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # ==========================================
    # 2. Database Settings (MongoDB / Motor)
    # ==========================================
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "property_db"

    # ==========================================
    # 3. Vector Database (Pinecone)
    # ==========================================
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "ai-estate-rag"
    PINECONE_DIMENSION: int = 768

    # ==========================================
    # 4. LLM & AI Services (Google Gemini / LangChain)
    # ==========================================
    GOOGLE_API_KEY: str = ""
    LLM_MODEL_NAME: str = "gemini-1.5-flash"
    EMBEDDING_MODEL_NAME: str = "models/text-embedding-004"

    # ==========================================
    # 5. GCP & Deployment Configurations
    # ==========================================
    GCP_PROJECT_ID: str = ""
    GCP_REGION: str = "asia-southeast1"

    # ตั้งค่าให้โหลดจากไฟล์ .env และมองข้ามตัวแปรเกิน
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    return Settings()


# Singleton Instance สำหรับเรียกใช้นอก FastAPI DI
settings = get_settings()
