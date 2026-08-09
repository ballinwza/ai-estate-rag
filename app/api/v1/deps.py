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
from app.infrastructure.llm.llm import LlmService
from app.infrastructure.persistence.mongodb.document_repository import (
    MongoDocumentRepository,
)
from app.infrastructure.persistence.vector_store.pinecone_repository import (
    PineconeRepository,
)
from app.usecases.generate_answer import GenerateAnswerUseCase
from app.usecases.process_document import ProcessDocumentUseCase

MongoDB = Annotated[AsyncIOMotorDatabase, Depends(get_mongodb_database)]
PineconeIndex = Annotated[Index | GrpcIndex, Depends(get_pinecone_index)]


# --- 1. Repositories Dependencies ---
def get_mongo_repo(db: MongoDB) -> MongoDocumentRepository:
    return MongoDocumentRepository(database=db)


def get_pinecone_repo(pc_index: PineconeIndex) -> PineconeRepository:
    return PineconeRepository(pc_index=pc_index)


# --- 2. External / Application Services Dependencies ---
def get_parser_service() -> LlmService:
    return LlmService(llm=ChatGoogleGenerativeAI(model=settings.LLM_MODEL_NAME))


def get_embedder_service() -> EmbedderService:
    return EmbedderService(
        api_key=settings.GOOGLE_API_KEY,
        model_name=settings.EMBEDDING_MODEL_NAME,
        output_dimensionality=settings.PINECONE_DIMENSION,
    )


def get_chunker_service() -> ChunkerService:
    return ChunkerService()


# --- Type Aliases สำหรับนำไปใช้ต่อได้ง่าย ---
MongoRepoDep = Annotated[MongoDocumentRepository, Depends(get_mongo_repo)]
PineconeRepoDep = Annotated[PineconeRepository, Depends(get_pinecone_repo)]
ParserServiceDep = Annotated[LlmService, Depends(get_parser_service)]
EmbedderServiceDep = Annotated[EmbedderService, Depends(get_embedder_service)]
ChunkerServiceDep = Annotated[ChunkerService, Depends(get_chunker_service)]


def get_process_document_usecase(
    mongo_repo: MongoRepoDep,
    pinecone_repo: PineconeRepoDep,
    parser_service: ParserServiceDep,
    embedder_service: EmbedderServiceDep,
    chunker_service: ChunkerServiceDep,
) -> ProcessDocumentUseCase:
    """รวมการประกอบ Repository + Use Case ไว้ในที่เดียว"""

    return ProcessDocumentUseCase(
        mongo_repo=mongo_repo,
        pinecone_repo=pinecone_repo,
        parser_service=parser_service,
        embedder_service=embedder_service,
        chunker_service=chunker_service,
    )


def get_generate_answer_usecase(
    mongo_repo: MongoRepoDep,
    pinecone_repo: PineconeRepoDep,
    embedder_service: EmbedderServiceDep,
    parser_service: ParserServiceDep,
) -> GenerateAnswerUseCase:
    return GenerateAnswerUseCase(
        vector_repo=pinecone_repo,
        mongo_repo=mongo_repo,
        embedder=embedder_service,
        llm=parser_service,
    )


# Type Alias หลักสำหรับนำไปใช้ใน Router
ProcessDocumentUseCaseDep = Annotated[
    ProcessDocumentUseCase, Depends(get_process_document_usecase)
]

ChatUsecaseDep = Annotated[GenerateAnswerUseCase, Depends(get_generate_answer_usecase)]
