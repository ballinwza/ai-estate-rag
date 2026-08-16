from collections.abc import AsyncIterable

import grpc.aio

from app.api.grpc.v1 import chat_pb2, chat_pb2_grpc
from app.schemas.multi_tenant import IngestDocumentDTO
from app.usecases.generate_answer import GenerateAnswerUseCase
from app.usecases.multi_tenant.create_knowledge_doc import CreateKnowledgeDocUseCase
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
        create_knowledge_usecase: CreateKnowledgeDocUseCase,
    ):
        self._chat_usecase = chat_usecase
        self._upload_file_usecase = upload_file_usecase
        self._create_knowledge_usecase = create_knowledge_usecase

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

    async def UploadFileStramMultiTenant(
        self, request_iterator: AsyncIterable[chat_pb2.UploadFileStreamRequest], context
    ) -> chat_pb2.UploadFileStreamResponse:

        file_buffer = bytearray()
        user_id = ""
        chatbot_id = ""
        filename = ""
        file_type = ""

        # 1. วนลูปอ่าน Stream ที่ Client ทยอยส่งมาทีละ chunk
        async for chunk_request in request_iterator:
            # ดึง Metadata จาก Chunk แรก (หรือ Chunk ที่แนบ metadata มา)
            if chunk_request.HasField("metadata"):
                user_id = chunk_request.metadata.user_id
                chatbot_id = chunk_request.metadata.chatbot_id
                filename = chunk_request.metadata.filename
                file_type = chunk_request.metadata.file_type

            # รวม binary chunk เข้าไปใน buffer
            if chunk_request.chunk_data:
                file_buffer.extend(chunk_request.chunk_data)

        # 2. แปลง buffer เป็น bytes ก้อนเดียว แล้วสร้าง DTO ส่งให้ Use Case
        dto = IngestDocumentDTO(
            user_id=user_id,
            chatbot_id=chatbot_id,
            filename=filename,
            file_type=file_type,
            file_content=bytes(file_buffer),  # ส่ง bytes ก้อนสมบูรณ์
        )

        # 3. เรียก Use Case ให้ทำงานตามปกติ
        result = await self._create_knowledge_usecase.execute(dto)

        return chat_pb2.UploadFileStreamResponse(
            file_id=result.id,
            status=result.status.value,
            message="Upload and processing started successfully",
        )
