# app/api/grpc/rag_servicer.py
import logging

import grpc
import grpc.aio

from app.api.grpc.v1 import rag_pb2, rag_pb2_grpc
from app.domain.entities.rag import RagResponse, RagSearchSimilarRequest
from app.usecases.multi_tenant.rag_usecase import RagSearchSimilarUseCase

logger = logging.getLogger(__name__)


class RagGrpcServicer(rag_pb2_grpc.RagServiceServicer):
    """
    gRPC Servicer สำหรับจัดการ RAG และ Vector Similarity Search
    ทำหน้าที่เป็น Adapter แปลง Protobuf Message -> Pydantic DTO -> UseCase -> Protobuf Response
    """

    def __init__(self, search_similar_use_case: RagSearchSimilarUseCase):
        self.search_similar_use_case = search_similar_use_case

    async def SearchSimilar(
        self,
        request: rag_pb2.RagSearchSimilarRequestDTO,
        context: grpc.aio.ServicerContext,
    ) -> rag_pb2.RagResponseDTO:
        try:
            # 1. แปลง Protobuf Request Message เป็น Pydantic Request DTO
            request_dto = RagSearchSimilarRequest(
                user_id=request.user_id,
                chatbot_id=request.chatbot_id,
                query_text=request.query_text,
                top_k=request.top_k if request.top_k > 0 else 5,
                file_id=request.knowledge_file_id
                if request.HasField("knowledge_file_id")
                else None,
            )

            # 2. เรียกใช้งาน Use Case
            use_case_result: RagResponse = await self.search_similar_use_case.execute(
                request_dto
            )

            # 3. แปลง Pydantic Response DTO กลับเป็น Protobuf Response Message
            pb_sources = []
            for source_item in use_case_result.sources:
                record_dto = source_item.record
                metadata_dto = record_dto.metadata

                # แปลง MetadataVectorRecordDTO -> pb2.MetadataVectorRecordDTO
                pb_metadata = rag_pb2.MetadataVectorRecordDTO(
                    user_id=metadata_dto.user_id,
                    chatbot_id=metadata_dto.chatbot_id,
                    file_id=metadata_dto.file_id,
                    chunk_index=metadata_dto.chunk_index,
                    text_content=metadata_dto.text_content,
                    page_number=metadata_dto.page_number,
                    filename=metadata_dto.filename,
                )

                # แปลง VectorRecordDTO -> pb2.VectorRecordDTO
                pb_vector_record = rag_pb2.VectorRecordDTO(
                    id=record_dto.id if record_dto.id else "",
                    values=record_dto.values,
                    metadata=pb_metadata,
                )

                # แปลง SearchVectorRecordItemDTO -> pb2.SearchVectorRecordItemDTO
                pb_source_item = rag_pb2.SearchVectorRecordItemDTO(
                    score=source_item.score,
                    record=pb_vector_record,
                )
                pb_sources.append(pb_source_item)

            # คืนค่า rag_pb2.RagResponseDTO ตามที่สร้างใน proto
            return rag_pb2.RagResponseDTO(
                answer_message=use_case_result.answer_message,
                sources=pb_sources,
            )

        except ValueError as ve:
            logger.warning(f"Validation error in SearchSimilar: {ve}")
            await context.abort(
                grpc.StatusCode.INVALID_ARGUMENT,
                f"Invalid argument: {ve}",
            )

        except Exception as e:
            logger.error(f"Unexpected error in SearchSimilar Servicer: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL,
                "An internal error occurred while processing the RAG search request.",
            )
