import base64
import io
import json
import mimetypes
from typing import Any

import pypdf
from fastapi import UploadFile
from langchain.chat_models import BaseChatModel


class LlmService:
    """Service สำหรับสกัดข้อความจากเอกสาร PDF หรือรูปภาพ"""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    async def get_llm_answer(self, prompt: str):
        response = await self.llm.ainvoke(prompt)
        return response

    async def parse_file(self, file: UploadFile) -> dict[str, Any]:
        content = await file.read()
        file_type = file.content_type or ""
        filename = (file.filename or "").lower()

        if "pdf" in file_type or filename.endswith(".pdf"):
            return self._parse_pdf_sync(content)
        elif "image" in file_type or filename.endswith((".png", ".jpg", ".jpeg")):
            return await self._parse_image(content, file_type or "image/jpeg")
        else:
            raise ValueError("รองรับเฉพาะไฟล์ประเภท PDF และรูปภาพ (PNG, JPG, JPEG) เท่านั้น")

    async def parse_chunk_file(
        self,
        file_input: bytes | bytearray | io.BytesIO,
        filename: str,
        content_type: str,
    ) -> dict[str, Any]:
        """
        สกัดข้อความจากข้อมูล binary (bytes, bytearray, io.BytesIO)
        รองรับไฟล์ PDF และ รูปภาพ
        """
        # 1. แปลงข้อมูลอินพุตให้เป็น bytes ก้อนเดียว
        if isinstance(file_input, io.BytesIO):
            content = file_input.getvalue()
        elif isinstance(file_input, (bytes, bytearray)):
            content = bytes(file_input)
        else:
            raise ValueError(
                "file_input ต้องเป็นประเภท bytes, bytearray หรือ io.BytesIO เท่านั้น"
            )

        filename_lower = filename.lower()
        file_type = content_type or ""

        # 2. คาดเดา Mime Type จากนามสกุลไฟล์ หากไม่ได้ระบุ content_type มา
        if not file_type and filename:
            guessed_type, _ = mimetypes.guess_type(filename)
            file_type = guessed_type or ""

        # 3. แยกเส้นทางการ Parse ตามประเภทไฟล์
        if "pdf" in file_type or filename_lower.endswith(".pdf"):
            return self._parse_pdf_sync(content)
        elif "image" in file_type or filename_lower.endswith((".png", ".jpg", ".jpeg")):
            # Fallback Mime Type สำหรับรูปภาพ
            mime = file_type if "image" in file_type else "image/jpeg"
            return await self._parse_image(content, mime)
        else:
            raise ValueError("รองรับเฉพาะไฟล์ประเภท PDF และรูปภาพ (PNG, JPG, JPEG) เท่านั้น")

    def _parse_pdf_sync(self, content: bytes) -> dict[str, Any]:
        """
        Helper function สำหรับสกัดข้อความจาก PDF (Synchronous)
        """
        try:
            pdf_reader = pypdf.PdfReader(io.BytesIO(content))
        except Exception as e:
            raise ValueError(f"ไม่สามารถอ่านไฟล์ PDF ได้ ไฟล์อาจชำรุดหรือติดรหัสผ่าน: {str(e)}")

        pages_data = []
        full_text_list = []

        for idx, page in enumerate(pdf_reader.pages):
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""

            text_cleaned = text.strip()

            if text_cleaned:
                full_text_list.append(text_cleaned)
                pages_data.append(
                    {
                        "page_number": idx + 1,
                        "char_length": len(text_cleaned),
                        "text": text_cleaned,
                    }
                )

        return {
            "total_pages": len(pdf_reader.pages),
            "full_text": "\n\n".join(full_text_list),  # สำหรับดึงอ่านภาพรวม
            "pages": pages_data,  # สำหรับทำ Reference / Chunking รายหน้า
        }

    async def _parse_image(self, content: bytes, mime_type: str) -> dict[str, Any]:
        if not self.llm:
            raise ValueError("จำเป็นต้องใช้ LLM ในการอ่านไฟล์รูปภาพ")

        base64_image = base64.b64encode(content).decode("utf-8")
        message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "กรุณาอ่านและสกัดข้อความทั้งหมดที่ปรากฏอยู่ในภาพนี้อย่างละเอียด "
                        "ตอบกลับเฉพาะข้อความที่อ่านได้เท่านั้น ไม่ต้องเติมข้อความใดๆเพิ่ม นอกจากข้อความที่อ่านได้ "
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                },
            ],
        }

        response = await self.llm.ainvoke([message])
        if hasattr(response, "content"):
            extracted_text = str(response.content).strip()
        else:
            extracted_text = str(response).strip()

        # กรณี LLM คืนค่ามาเป็น JSON String หรือ List String แบบหลวมๆ
        if extracted_text.startswith("[") or extracted_text.startswith("{"):
            try:
                parsed = json.loads(extracted_text)
                if (
                    isinstance(parsed, list)
                    and len(parsed) > 0
                    and isinstance(parsed[0], dict)
                ):
                    extracted_text = parsed[0].get("text", extracted_text)
            except Exception:
                pass  # หาก parse json ไม่ผ่าน ให้ใช้ค่าเดิมตรงๆ

        return {
            "total_pages": 1,
            "full_text": extracted_text,
            "pages": [
                {
                    "page_number": 1,
                    "char_length": len(extracted_text),
                    "text": extracted_text,
                }
            ],
        }
