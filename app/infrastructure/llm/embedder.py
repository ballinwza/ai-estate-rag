from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pydantic import SecretStr


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
