from typing import Any

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.domain.entities.multi_tenant_doc import Chunk


class ChunkerService:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        encoding_name: str = "cl100k_base",  # Tokenizer standard ของ OpenAI/Tiktoken
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.get_encoding(encoding_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self._count_tokens,
            separators=["\n\n", "\n", " ", ""],
        )

    async def get_recursive(self, full_text: str) -> list[str]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # ขนาดข้อความต่อ 1 chunk
            chunk_overlap=50,  # ข้อความเกยกันเพื่อรักษาบริบทเชื่อมโยง
        )
        chunks = text_splitter.split_text(full_text)
        return chunks

    async def process_and_chunk(self, extracted_doc: dict[str, Any]) -> list[Chunk]:
        """
        ประมวลผลไฟล์ bytes และแปลงเป็น List[Chunk]
        รองรับทั้ง PDF และ Text File
        """
        pages_data = extracted_doc.get("pages", [])

        # 2. ทำ Chunking แยกตามแต่ละหน้าเพื่อเก็บ page_number ที่แม่นยำ
        chunks: list[Chunk] = []
        global_chunk_index = 0

        for page_info in pages_data:
            page_text = page_info.get("text", "")
            page_num = page_info.get("page_number", 1)

            if not page_text.strip():
                continue

            # ตัดข้อความในหน้านั้นๆ เป็น Chunks ย่อยตาม chunk_size (token)
            split_texts = self.text_splitter.split_text(page_text)

            for text_segment in split_texts:
                token_count = self._count_tokens(text_segment)

                chunk = Chunk(
                    vector_id="",  # จะถูกเติมโดย Use Case เมื่อบันทึกลง DB
                    chunk_index=global_chunk_index,
                    text_content=text_segment,
                    page_number=page_num,
                    token_count=token_count,
                )
                chunks.append(chunk)
                global_chunk_index += 1

        return chunks

    def _count_tokens(self, text: str) -> int:
        """Helper function สำหรับคำนวณจำนวน Token"""
        return len(self.tokenizer.encode(text))
