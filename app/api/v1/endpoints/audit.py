from fastapi import APIRouter, status
from pydantic import BaseModel

# สร้าง Router สำหรับ API V1
history_router = APIRouter(prefix="/audit", tags=["History & Logging"])


class Response(BaseModel):
    message: str
    status: str


@history_router.get(
    "/logs",
    response_model=Response,
    status_code=status.HTTP_200_OK,
    summary="Hello World Endpoint",
    description="ดึงรายการประวัติการถาม-ตอบย้อนหลัง (History Log) สำหรับโชว์ Admin Log หน้าระบบ",
)
async def logs():
    return Response(
        message="Hello World! Welcome to Enterprise RAG API", status="success"
    )


@history_router.get(
    "/logs/{log_id}",
    response_model=Response,
    status_code=status.HTTP_200_OK,
    summary="Hello World Endpoint",
    description="ดึงรายละเอียด Log รายตัว รวมถึง Query และ Context Snippet เพื่อแสดงผลใน Source Inspector Panel",
)
async def log_id(id: str):
    return Response(
        message="Hello World! Welcome to Enterprise RAG API", status="success"
    )
