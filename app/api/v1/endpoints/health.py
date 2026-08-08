from fastapi import APIRouter, status
from pydantic import BaseModel

# สร้าง Router สำหรับ API V1
health_router = APIRouter()


# DTO สำหรับ Hello World Response (สอดคล้องกับ schemas/)
class HelloWorldResponse(BaseModel):
    message: str
    status: str


@health_router.get(
    "/health",
    response_model=HelloWorldResponse,
    status_code=status.HTTP_200_OK,
    summary="Hello World Endpoint",
    description="Endpoint สำหรับทดสอบการเชื่อมต่อ API เบื้องต้น",
)
async def get_hello_world():
    return HelloWorldResponse(
        message="Hello World! Welcome to Enterprise RAG API", status="success"
    )
