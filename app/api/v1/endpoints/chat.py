from fastapi import APIRouter, HTTPException, status

from app.api.v1.deps import ChatUsecaseDep
from app.schemas.chat import ChatRequest, ChatResponse

chat_router = APIRouter()


@chat_router.post(
    "/query",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="ตอบคำถามโดยใช้ AI",
    description="รับคำถามผู้ใช้ ค้นหาใน Vector DB , ดึงข้อมูลมาสรุปเป็น Executive Summary Format พร้อมคืนค่า Source Citations และ Performance Metrics (Latency / Token Usage)",
)
async def receive_question(req: ChatRequest, usecase: ChatUsecaseDep):
    try:
        return await usecase.execute(query_text=req.question, top_k=3)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาดภายในเซิร์ฟเวอร์: {err}",
        )
