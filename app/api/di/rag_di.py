from typing import TypedDict

from app.api.v1.deps import (
    get_embedder_service,
    get_parser_service,
)
from app.core.mongodb import get_mongodb_database
from app.core.pinecone import get_pinecone_index
from app.infrastructure.persistence.mongodb.multi_tenant_repository import (
    MongoMultiTenantChatbotRepository,
)
from app.infrastructure.persistence.vector_store.pinecone_repository import (
    PineconeRepository,
)
from app.usecases.multi_tenant.rag_usecase import RagSearchSimilarUseCase


class RagUseCaseDict(TypedDict):
    ragSearchSimilarUseCase: RagSearchSimilarUseCase


def build_rag_usecase() -> RagUseCaseDict:
    pinecone_repo = PineconeRepository(pc_index=get_pinecone_index())
    embedder_service = get_embedder_service()
    parser_service = get_parser_service()
    mongo_chatbot = MongoMultiTenantChatbotRepository(db=get_mongodb_database())

    return {
        "ragSearchSimilarUseCase": RagSearchSimilarUseCase(
            pinecone_repo=pinecone_repo,
            mongo_multi_tenant=mongo_chatbot,
            embedder_service=embedder_service,
            llm_service=parser_service,
        )
    }
