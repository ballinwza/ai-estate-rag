from fastapi import APIRouter, HTTPException, UploadFile, status

from app.api.v1.deps import ProcessDocumentUseCaseDep
from app.usecases.process_document import ProcessDocumentOutput

document_router = APIRouter(
    prefix="/documents",
    tags=["Document Processing"],
    # dependencies=[Depends(verify_api_key)],
)


@document_router.post(
    "/upload",
    response_model=ProcessDocumentOutput,
    status_code=status.HTTP_201_CREATED,
    summary="อัปโหลดเอกสาร PDF หรือรูปภาพอสังหาฯ",
    description="อ่านและสกัดข้อความจากเอกสาร/รูปภาพ เพื่อนำข้อมูลไปปรับใช้กับระบบ RAG และบันทึกลง Database",
)
async def upload_document(
    usecase: ProcessDocumentUseCaseDep, file: UploadFile
) -> ProcessDocumentOutput:
    try:
        return await usecase.execute(file)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาดภายในเซิร์ฟเวอร์: {err}",
        )
