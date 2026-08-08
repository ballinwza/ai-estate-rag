from langchain_text_splitters import RecursiveCharacterTextSplitter


class ChunkerService:
    def __init__(self) -> None:
        self._init_ = ""

    async def get_recursive(self, full_text: str) -> list[str]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # ขนาดข้อความต่อ 1 chunk
            chunk_overlap=50,  # ข้อความเกยกันเพื่อรักษาบริบทเชื่อมโยง
        )
        chunks = text_splitter.split_text(full_text)
        return chunks
