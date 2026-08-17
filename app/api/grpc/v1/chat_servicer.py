import grpc.aio

from app.api.grpc.v1 import chat_pb2, chat_pb2_grpc
from app.usecases.generate_answer import GenerateAnswerUseCase
from app.usecases.upload_chunk_file import UploadChunkFileUseCase


class ChatServicer(chat_pb2_grpc.ChatGRPCServicer):
    """
    gRPC Servicer ทำหน้าที่เป็น Controller / Transport Layer
    รับ Protobuf Request -> เรียก UseCase -> คืน Protobuf Response
    """

    def __init__(
        self,
        chat_usecase: GenerateAnswerUseCase,
        upload_file_usecase: UploadChunkFileUseCase,
    ):
        self._chat_usecase = chat_usecase
        self._upload_file_usecase = upload_file_usecase

    async def Query(
        self, request: chat_pb2.ChatRequest, context: grpc.aio.ServicerContext
    ) -> chat_pb2.ChatResponse:
        try:
            # 1. ดึงข้อมูลจาก Protobuf Request
            question = request.question

            # 2. เรียกใช้งาน UseCase
            result = await self._chat_usecase.execute(query_text=question, top_k=3)

            # 3. แปลงผลลัพธ์กลับเป็น Protobuf Response
            response_message = (
                result.message if hasattr(result, "message") else str(result)
            )

            return chat_pb2.ChatResponse(message=response_message)

        except ValueError as err:
            # แมป ValueError เป็น gRPC INVALID_ARGUMENT (คล้าย 400 Bad Request)
            await context.abort(code=grpc.StatusCode.INVALID_ARGUMENT, details=str(err))
        except Exception as err:
            # แมป Error อื่นๆ เป็น gRPC INTERNAL (คล้าย 500 Internal Server Error)
            await context.abort(
                code=grpc.StatusCode.INTERNAL,
                details=f"เกิดข้อผิดพลาดภายในเซิร์ฟเวอร์: {err}",
            )

    async def UploadPdf(
        self,
        request_iterator: grpc.aio.StreamStreamCall,
        context: grpc.aio.ServicerContext,
    ) -> chat_pb2.UploadPdfResponse:
        try:
            filename = "uploaded_document.pdf"
            file_bytes = bytearray()

            # 1. รวบรวม Chunks จาก gRPC Stream
            async for request in request_iterator:
                if request.HasField("metadata"):
                    filename = request.metadata.filename
                elif request.HasField("chunk_data"):
                    file_bytes.extend(request.chunk_data)

            if not file_bytes:
                await context.abort(
                    code=grpc.StatusCode.INVALID_ARGUMENT,
                    details="Received empty file stream.",
                )

            # 2. ส่ง bytes และ filename ให้ UseCase ทำงาน
            result = await self._upload_file_usecase.execute(
                file_bytes=bytes(file_bytes),
                filename=filename,
                content_type="application/pdf",
            )

            # 3. ส่ง Response กลับไปให้ Client
            return chat_pb2.UploadPdfResponse(
                file_id=result.document_id,
                success=True,
                message=f"Uploaded and processed {result.filename} successfully.",
            )

        except ValueError as err:
            await context.abort(code=grpc.StatusCode.INVALID_ARGUMENT, details=str(err))
        except Exception as err:
            await context.abort(
                code=grpc.StatusCode.INTERNAL,
                details=f"เกิดข้อผิดพลาดในการประมวลผลไฟล์: {err}",
            )
