import logging
from typing import TypedDict

import grpc
import grpc.aio

from app.api.di.chatbot_di import build_chatbot_usecases
from app.api.di.knowledge_file_di import build_knowledge_file_usecase
from app.api.grpc.v1 import (
    chat_pb2_grpc,
    knowledge_file_pb2_grpc,
    multi_tenant_chatbot_pb2_grpc,
)
from app.api.grpc.v1.chat_servicer import ChatServicer
from app.api.grpc.v1.knowledge_file_servicer import KnowledgeFileGrpcServicer
from app.api.grpc.v1.multi_tenant_chatbot_service import ChatbotGrpcService
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

logger = logging.getLogger("uvicorn")

# TODO: ใช้ตอน mTLS
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# CERTS_DIR = os.path.join(BASE_DIR, "certs")


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


async def start_grpc_server(
    host: str = "[::]",
    port: int = 8000,
    # TODO: ใช้ตอน mTLS
    # ca_cert_path: str = os.path.join(CERTS_DIR, "ca.crt"),
    # server_cert_path: str = os.path.join(CERTS_DIR, "server.crt"),
    # server_key_path: str = os.path.join(CERTS_DIR, "server.key"),
) -> grpc.aio.Server:
    """
    Factory Function สำหรับดึง Connection / Config มาประกอบเป็น UseCase
    เหมือนกับที่ get_generate_answer_usecase() ใน deps.py ทำ
    """
    server = grpc.aio.server()

    di = build_generate_answer_usecase()
    chat_usecase = di["generateAnswerUsecase"]
    upload_chunk_file = di["uploadChunkFileUsecase"]

    chat_servicer = ChatServicer(
        chat_usecase=chat_usecase,
        upload_file_usecase=upload_chunk_file,
    )
    chat_pb2_grpc.add_ChatGRPCServicer_to_server(chat_servicer, server)

    # Multi Tenant Chatbot blueprint
    chatbot_usecases = build_chatbot_usecases()
    chatbot_servicer = ChatbotGrpcService(
        create_use_case=chatbot_usecases["create_use_case"],
        get_use_case=chatbot_usecases["get_use_case"],
        list_use_case=chatbot_usecases["list_use_case"],
        update_use_case=chatbot_usecases["update_use_case"],
        delete_use_case=chatbot_usecases["delete_use_case"],
    )
    multi_tenant_chatbot_pb2_grpc.add_ChatbotServiceServicer_to_server(
        chatbot_servicer, server
    )

    knowledge_file_usecase = build_knowledge_file_usecase()
    knowledge_file_servicer = KnowledgeFileGrpcServicer(
        process_ingest_use_case=knowledge_file_usecase["createKnowledgeDocUseCase"],
        get_file_use_case=knowledge_file_usecase["getKnowledgeDocUseCase"],
        list_files_use_case=knowledge_file_usecase["listKnowledgeDocsUseCase"],
        delete_file_use_case=knowledge_file_usecase["deleteKnowledgeDocUseCase"],
    )
    knowledge_file_pb2_grpc.add_KnowledgeFileServiceServicer_to_server(
        knowledge_file_servicer, server
    )
    # 4. โหลด Credentials สำหรับ mTLS
    # root_ca = load_file(ca_cert_path)
    # server_key = load_file(server_key_path)
    # server_cert = load_file(server_cert_path)

    # # 5. สร้าง SSL Server Credentials และบังคับตรวจ Client Certificate (mTLS)
    # server_credentials = grpc.ssl_server_credentials(
    #     [(server_key, server_cert)],
    #     root_certificates=root_ca,
    #     # require_client_certificate=True คือหัวใจสำคัญของการทำ mTLS
    #     require_client_auth=True,
    # )

    server_address = f"{host}:{port}"
    # TODO: ใช้ตอน mTLS
    # server.add_secure_port(server_address, server_credentials)
    server.add_insecure_port(server_address)
    await server.start()
    return server


def load_file(file_path: str) -> bytes:
    """ฟังก์ชัน helper สำหรับอ่านไฟล์ certificate/key"""
    with open(file_path, "rb") as f:
        return f.read()
