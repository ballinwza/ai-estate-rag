from typing import Annotated

from fastapi import Depends
from langchain_google_genai import ChatGoogleGenerativeAI
from motor.motor_asyncio import AsyncIOMotorDatabase
from pinecone import GrpcIndex, Index

from app.core.config import settings
from app.core.mongodb import get_mongodb_database
from app.core.pinecone import get_pinecone_index
from app.infrastructure.llm.chunker import ChunkerService
from app.infrastructure.llm.embedder import EmbedderService
from app.infrastructure.llm.file_parser import FileParserService
from app.infrastructure.persistence.mongodb.document_repository_impl import (
    MongoDocumentRepositoryImpl,
)
from app.infrastructure.persistence.vector_store.pinecone_repository_impl import (
    PineconeRepositoryImpl,
)
from app.usecases.process_document import ProcessDocumentUseCase

MongoDB = Annotated[AsyncIOMotorDatabase, Depends(get_mongodb_database)]
PineconeIndex = Annotated[Index | GrpcIndex, Depends(get_pinecone_index)]


def get_process_document_usecase(
    db: MongoDB,
    pc_index: PineconeIndex,
) -> ProcessDocumentUseCase:
    """รวมการประกอบ Repository + Use Case ไว้ในที่เดียว"""

    mongo_repo = MongoDocumentRepositoryImpl(database=db)
    pinecone_repo = PineconeRepositoryImpl(pc_index=pc_index)
    parser_service = FileParserService(
        llm=ChatGoogleGenerativeAI(model=settings.LLM_MODEL_NAME)
    )
    embedder_service = EmbedderService(
        api_key=settings.GOOGLE_API_KEY,
        model_name=settings.EMBEDDING_MODEL_NAME,
        output_dimensionality=settings.PINECONE_DIMENSION,
    )
    chunker_service = ChunkerService()

    return ProcessDocumentUseCase(
        mongo_repo=mongo_repo,
        pinecone_repo=pinecone_repo,
        parser_service=parser_service,
        embedder_service=embedder_service,
        chunker_service=chunker_service,
    )


# Type Alias หลักสำหรับนำไปใช้ใน Router
ProcessDocumentUseCaseDep = Annotated[
    ProcessDocumentUseCase, Depends(get_process_document_usecase)
]
