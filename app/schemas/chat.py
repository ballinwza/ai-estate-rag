from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    message: str = Field(
        description="ข้อความแจ้งสถานะการทำงาน",
    )


class ChatRequest(BaseModel):
    question: str = Field(examples=["สรุปเอกสาร"])
