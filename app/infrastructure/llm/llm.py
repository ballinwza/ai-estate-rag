import ast
import base64
import io
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
            return await self._parse_pdf(content)
        elif "image" in file_type or filename.endswith((".png", ".jpg", ".jpeg")):
            return await self._parse_image(content, file_type or "image/jpeg")
        else:
            raise ValueError("รองรับเฉพาะไฟล์ประเภท PDF และรูปภาพ (PNG, JPG, JPEG) เท่านั้น")

    async def _parse_pdf(self, content: bytes) -> dict[str, Any]:
        pdf_reader = pypdf.PdfReader(io.BytesIO(content))

        pages_data = []
        full_text_list = []

        for idx, page in enumerate(pdf_reader.pages):
            text = page.extract_text() or ""
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
        res_content = str(response.content).strip()

        extracted_text = ""

        # เช็คว่าถ้าเป็น str ให้ลองแปลงเป็น List/Dict
        if isinstance(res_content, str):
            try:
                # แปลง String "[{'type': 'text', ...}]" ให้เป็น Python List จริงๆ
                parsed_data = ast.literal_eval(res_content)

                if isinstance(parsed_data, list) and len(parsed_data) > 0:
                    # ดึงเอาเฉพาะฟิลด์ 'text' ออกมา
                    extracted_text = parsed_data[0].get("text", "")
                else:
                    extracted_text = res_content
            except (ValueError, SyntaxError):
                # ถ้าแปลงไม่ได้ ให้ใช้ค่า res_content ตรงๆ
                extracted_text = res_content

        elif isinstance(res_content, list) and len(res_content) > 0:
            extracted_text = (
                res_content[0].get("text", "")
                if isinstance(res_content[0], dict)
                else str(res_content[0])
            )

        extracted_text = extracted_text.strip()

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
