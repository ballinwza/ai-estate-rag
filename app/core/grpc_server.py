import logging

import grpc
import grpc.aio

from app.api.grpc.v1 import chat_pb2_grpc
from app.api.grpc.v1.chat_servicer import ChatServicer
from app.api.v1.deps import (
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

logger = logging.getLogger("uvicorn")


def build_generate_answer_usecase() -> GenerateAnswerUseCase:
    """
    Factory Function สำหรับดึง Connection / Config มาประกอบเป็น UseCase
    เหมือนกับที่ get_generate_answer_usecase() ใน deps.py ทำ
    """
    mongo_repo = MongoDocumentRepository(database=get_mongodb_database())
    pinecone_repo = PineconeRepository(pc_index=get_pinecone_index())
    embedder_service = get_embedder_service()
    parser_service = get_parser_service()

    return GenerateAnswerUseCase(
        vector_repo=pinecone_repo,
        mongo_repo=mongo_repo,
        embedder=embedder_service,
        llm=parser_service,
    )


async def start_grpc_server(host: str = "[::]", port: int = 50052) -> grpc.aio.Server:
    """
    Factory Function สำหรับดึง Connection / Config มาประกอบเป็น UseCase
    เหมือนกับที่ get_generate_answer_usecase() ใน deps.py ทำ
    """
    server = grpc.aio.server()

    # 1. Instantiates Dependencies/UseCase
    chat_usecase = build_generate_answer_usecase()

    # 2. ส่ง UseCase เข้า Servicer
    chat_servicer = ChatServicer(chat_usecase=chat_usecase)

    # 3. ลงทะเบียน Servicer เข้า Server
    chat_pb2_grpc.add_ChatGRPCServicer_to_server(chat_servicer, server)

    server_address = f"{host}:{port}"
    server.add_insecure_port(server_address)
    await server.start()
    return server
