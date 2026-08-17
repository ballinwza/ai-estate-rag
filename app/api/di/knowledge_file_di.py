from typing import TypedDict

from app.api.v1.deps import (
    get_chunker_service,
    get_embedder_service,
    get_parser_service,
)
from app.core.mongodb import get_mongodb_database
from app.core.pinecone import get_pinecone_index
from app.infrastructure.persistence.mongodb.knowledge_file_repository import (
    MongoKnowledgeFileRepository,
)
from app.infrastructure.persistence.vector_store.pinecone_repository import (
    PineconeRepository,
)
from app.usecases.multi_tenant.knowledge_file_usecase import (
    CreateKnowledgeDocUseCase,
    DeleteKnowledgeDocUseCase,
    GetKnowledgeDocUseCase,
    ListKnowledgeDocsUseCase,
)


class KnowledgeFileUseCaseDict(TypedDict):
    createKnowledgeDocUseCase: CreateKnowledgeDocUseCase
    getKnowledgeDocUseCase: GetKnowledgeDocUseCase
    listKnowledgeDocsUseCase: ListKnowledgeDocsUseCase
    deleteKnowledgeDocUseCase: DeleteKnowledgeDocUseCase


def build_knowledge_file_usecase() -> KnowledgeFileUseCaseDict:
    # mongo_repo = MongoDocumentRepository(database=get_mongodb_database())
    pinecone_repo = PineconeRepository(pc_index=get_pinecone_index())
    embedder_service = get_embedder_service()
    parser_service = get_parser_service()
    chunker_service = get_chunker_service()
    mongo_knowledge = MongoKnowledgeFileRepository(db=get_mongodb_database())

    return {
        "createKnowledgeDocUseCase": CreateKnowledgeDocUseCase(
            pinecone_repo=pinecone_repo,
            mongo_repo=mongo_knowledge,
            embedder_service=embedder_service,
            parser_service=parser_service,
            chunker_service=chunker_service,
        ),
        "getKnowledgeDocUseCase": GetKnowledgeDocUseCase(file_repo=mongo_knowledge),
        "listKnowledgeDocsUseCase": ListKnowledgeDocsUseCase(
            file_repo=mongo_knowledge,
        ),
        "deleteKnowledgeDocUseCase": DeleteKnowledgeDocUseCase(
            file_repo=mongo_knowledge, vector_repo=pinecone_repo
        ),
    }
