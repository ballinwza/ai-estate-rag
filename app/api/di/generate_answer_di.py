from typing import TypedDict

from app.api.v1.deps import (
    get_chunker_service,
    get_embedder_service,
    get_parser_service,
)
from app.core.mongodb import get_mongodb_database
from app.core.pinecone import get_pinecone_index
from app.infrastructure.persistence.mongodb.document_repository import (
    MongoDocumentRepository,
)
from app.infrastructure.persistence.vector_store.pinecone_repository import (
    PineconeRepository,
)
from app.usecases.generate_answer import GenerateAnswerUseCase
from app.usecases.upload_chunk_file import UploadChunkFileUseCase


class GenerateAnswerDict(TypedDict):
    generateAnswerUsecase: GenerateAnswerUseCase
    uploadChunkFileUsecase: UploadChunkFileUseCase


def build_generate_answer_usecase() -> GenerateAnswerDict:
    """
    Factory Function สำหรับดึง Connection / Config มาประกอบเป็น UseCase
    เหมือนกับที่ get_generate_answer_usecase() ใน deps.py ทำ
    """
    mongo_repo = MongoDocumentRepository(database=get_mongodb_database())
    pinecone_repo = PineconeRepository(pc_index=get_pinecone_index())
    embedder_service = get_embedder_service()
    parser_service = get_parser_service()
    chunker_service = get_chunker_service()

    return {
        "generateAnswerUsecase": GenerateAnswerUseCase(
            vector_repo=pinecone_repo,
            mongo_repo=mongo_repo,
            embedder=embedder_service,
            llm=parser_service,
        ),
        "uploadChunkFileUsecase": UploadChunkFileUseCase(
            mongo_repo=mongo_repo,
            pinecone_repo=pinecone_repo,
            parser_service=parser_service,
            embedder_service=embedder_service,
            chunker_service=chunker_service,
        ),
    }
