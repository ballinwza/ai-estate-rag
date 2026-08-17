import logging
from collections.abc import AsyncIterable
from datetime import datetime

import grpc
import grpc.aio
from google.protobuf.timestamp_pb2 import Timestamp

# Import โค้ดที่คอมไพล์มาจาก .proto
from app.api.grpc.v1 import knowledge_file_pb2, knowledge_file_pb2_grpc
from app.domain.entities.knowledge_file import (
    CreateKnowledgeFile,
    DeleteKnowledgeFile,
    GetKnowledgeFile,
    ListKnowledgeFiles,
)
from app.domain.entities.multi_tenant_doc import Chunk, FileStatus, KnowledgeFiles
from app.usecases.multi_tenant.knowledge_file_usecase import (
    CreateKnowledgeDocUseCase,
    DeleteKnowledgeDocUseCase,
    GetKnowledgeDocUseCase,
    ListKnowledgeDocsUseCase,
)

logger = logging.getLogger(__name__)


# --- Helper Functions สำหรับ Mapping Data ---


def datetime_to_timestamp(dt: datetime | None) -> Timestamp:
    """แปลง Python datetime เป็น google.protobuf.Timestamp"""
    ts = Timestamp()
    if dt:
        ts.FromDatetime(dt)
    return ts


def domain_chunk_to_proto(chunk: Chunk) -> knowledge_file_pb2.Chunk:
    """แปลง Domain Entity Chunk เป็น Protobuf Message Chunk"""
    return knowledge_file_pb2.Chunk(
        vector_id=str(chunk.vector_id),
        chunk_index=chunk.chunk_index,
        text_content=chunk.text_content,
        page_number=chunk.page_number,
        token_count=chunk.token_count,
    )


def domain_file_to_proto(file: KnowledgeFiles) -> knowledge_file_pb2.KnowledgeFile:
    """แปลง Domain Entity KnowledgeFiles เป็น Protobuf Message KnowledgeFile"""
    # Mapping Enum FileStatus[cite: 3]
    status_map = {
        FileStatus.PENDING: knowledge_file_pb2.PENDING,
        FileStatus.COMPLETED: knowledge_file_pb2.COMPLETED,
        FileStatus.FAILED: knowledge_file_pb2.FAILED,
    }
    pb_status = status_map.get(file.status, knowledge_file_pb2.PENDING)

    pb_chunks = [domain_chunk_to_proto(c) for c in file.chunks]

    return knowledge_file_pb2.KnowledgeFile(
        id=file.id or "",
        user_id=file.user_id,
        chatbot_id=file.chatbot_id,
        filename=file.filename,
        file_type=file.file_type,
        file_size_bytes=file.file_size_bytes,
        status=pb_status,
        total_chunks=file.total_chunks,
        chunks=pb_chunks,
        total_page=file.total_page,
        text_content=file.text_content if file.text_content else None,
        error_message=file.error_message if file.error_message else None,
        created_at=datetime_to_timestamp(file.created_at),
        updated_at=datetime_to_timestamp(file.updated_at),
    )


# --- Servicer Implementation ---


class KnowledgeFileGrpcServicer(knowledge_file_pb2_grpc.KnowledgeFileServiceServicer):
    """
    gRPC Controller / Presentation Layer สำหรับจัดการ Knowledge Files และ RAG
    """

    def __init__(
        self,
        process_ingest_use_case: CreateKnowledgeDocUseCase,
        get_file_use_case: GetKnowledgeDocUseCase,
        list_files_use_case: ListKnowledgeDocsUseCase,
        delete_file_use_case: DeleteKnowledgeDocUseCase,
    ):
        self.process_ingest_use_case = process_ingest_use_case
        self.get_file_use_case = get_file_use_case
        self.list_files_use_case = list_files_use_case
        self.delete_file_use_case = delete_file_use_case

    async def CreateKnowledgeFile(
        self,
        request_iterator: AsyncIterable[knowledge_file_pb2.UploadFileStreamRequest],
        context,
    ) -> knowledge_file_pb2.UploadFileStreamResponse:
        """RPC สำหรับประมวลผลและสร้าง Ingestion เอกสารเข้า Vector DB"""
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

        dto = CreateKnowledgeFile(
            user_id=user_id,
            chatbot_id=chatbot_id,
            filename=filename,
            file_type=file_type,
            file_content=bytes(file_buffer),  # ส่ง bytes ก้อนสมบูรณ์
        )

        result = await self.process_ingest_use_case.execute(dto)

        return knowledge_file_pb2.UploadFileStreamResponse(
            file_id=result.id,
            status=result.status.value,
            message="Upload and processing started successfully",
        )

    async def GetKnowledgeFile(
        self,
        request: knowledge_file_pb2.GetKnowledgeFileRequest,
        context: grpc.aio.ServicerContext,
    ) -> knowledge_file_pb2.GetKnowledgeFileResponse:
        """RPC สำหรับดึงข้อมูลเอกสารตาม file_id"""
        try:
            dto = GetKnowledgeFile(
                id=request.id,
                user_id=request.user_id,
            )

            file_doc = await self.get_file_use_case.execute(dto)
            if not file_doc:
                await context.abort(
                    grpc.StatusCode.NOT_FOUND, "Knowledge file not found"
                )

            return knowledge_file_pb2.GetKnowledgeFileResponse(
                file=domain_file_to_proto(file_doc)
            )
        except ValueError as ve:
            await context.abort(grpc.StatusCode.NOT_FOUND, str(ve))
        except Exception as e:
            logger.error(f"Error in GetKnowledgeFile: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {e}")

    async def ListKnowledgeFiles(
        self,
        request: knowledge_file_pb2.ListKnowledgeFilesRequest,
        context: grpc.aio.ServicerContext,
    ) -> knowledge_file_pb2.ListKnowledgeFilesResponse:
        """RPC สำหรับดึงรายการเอกสารทั้งหมดของ Chatbot"""
        try:
            limit = request.limit if request.limit > 0 else 20
            offset = max(request.offset, 0)

            dto = ListKnowledgeFiles(
                user_id=request.user_id,
                chatbot_id=request.chatbot_id,
                limit=limit,
                offset=offset,
            )

            files = await self.list_files_use_case.execute(dto)
            pb_files = [domain_file_to_proto(f) for f in files]

            return knowledge_file_pb2.ListKnowledgeFilesResponse(
                files=pb_files,
                total_count=len(pb_files),
            )
        except Exception as e:
            logger.error(f"Error in ListKnowledgeFiles: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {e}")

    async def DeleteKnowledgeFile(
        self,
        request: knowledge_file_pb2.DeleteKnowledgeFileRequest,
        context: grpc.aio.ServicerContext,
    ) -> knowledge_file_pb2.DeleteKnowledgeFileResponse:
        """RPC สำหรับลบเอกสารออกจาก MongoDB และ Vector DB"""
        try:
            dto = DeleteKnowledgeFile(
                chatbot_id=request.chatbot_id,
                user_id=request.user_id,
            )

            success = await self.delete_file_use_case.execute(dto)

            return knowledge_file_pb2.DeleteKnowledgeFileResponse(
                success=success,
                message="File deleted successfully"
                if success
                else "Failed to delete file",
            )
        except ValueError as ve:
            await context.abort(grpc.StatusCode.NOT_FOUND, str(ve))
        except Exception as e:
            logger.error(f"Error in DeleteKnowledgeFile: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {e}")
