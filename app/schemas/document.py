from pydantic import BaseModel, Field


class ProcessDocumentOutput(BaseModel):
    """Schema สำหรับข้อมูลตอบกลับหลังจากการอัปโหลดและประมวลผลเอกสาร"""

    document_id: str = Field(..., description="ID ของเอกสารที่ถูกประมวลผลและบันทึก")
    filename: str = Field(..., description="ชื่อไฟล์ที่อัปโหลด")
    extracted_text: str = Field(..., description="ข้อความที่สกัดได้จากไฟล์ PDF หรือรูปภาพ")
    file_type: str = Field(..., description="ชนิดของไฟล์ เช่น pdf, image/png")
    message: str = Field(
        default="ประมวลผลและบันทึกเอกสารสำเร็จ",
        description="ข้อความแจ้งสถานะการทำงาน",
    )
