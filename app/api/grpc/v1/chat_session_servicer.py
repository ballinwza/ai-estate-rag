import logging

import grpc
import grpc.aio
from google.protobuf.empty_pb2 import Empty
from google.protobuf.timestamp_pb2 import Timestamp

from app.api.grpc.v1 import chat_session_pb2, chat_session_pb2_grpc
from app.domain.entities.chat_session import ChatMessage, ChatSession, MessageRole
from app.usecases.multi_tenant.chat_session_usecase import (
    AddChatMessageDTO,
    AddChatMessageUseCase,
    CreateChatSessionDTO,
    CreateChatSessionUseCase,
    DeleteChatSessionUseCase,
    GetChatHistoryUseCase,
    GetChatSessionUseCase,
    ListUserChatSessionsUseCase,
)

logger = logging.getLogger("grpc")


# ==============================================================================
# HELPER FUNCTIONS (Domain <-> Protobuf Converter)
# ==============================================================================


def datetime_to_timestamp(dt) -> Timestamp:
    """แปลง datetime.datetime (UTC) ให้เป็น google.protobuf.Timestamp"""
    ts = Timestamp()
    if dt:
        ts.FromDatetime(dt)
    return ts


def role_domain_to_proto(role: MessageRole) -> chat_session_pb2.MessageRole:
    """แปลง MessageRole Enum จาก Domain Model ไปเป็น Protobuf Enum"""
    mapping = {
        MessageRole.USER: chat_session_pb2.MessageRole.USER,
        MessageRole.AI: chat_session_pb2.MessageRole.AI,
        MessageRole.SYSTEM: chat_session_pb2.MessageRole.SYSTEM,
    }
    return mapping.get(role, chat_session_pb2.MessageRole.MESSAGE_ROLE_UNSPECIFIED)


def role_proto_to_domain(proto_role: chat_session_pb2.MessageRole) -> MessageRole:
    """แปลง MessageRole Enum จาก Protobuf ไปเป็น Domain Model"""
    mapping = {
        chat_session_pb2.MessageRole.USER: MessageRole.USER,
        chat_session_pb2.MessageRole.AI: MessageRole.AI,
        chat_session_pb2.MessageRole.SYSTEM: MessageRole.SYSTEM,
    }
    return mapping.get(proto_role, MessageRole.USER)


def message_domain_to_proto(message: ChatMessage) -> chat_session_pb2.ChatMessage:
    """แปลง ChatMessage Domain Entity เป็น Protobuf Message"""
    return chat_session_pb2.ChatMessage(
        role=role_domain_to_proto(message.role),
        content=message.content,
        created_at=datetime_to_timestamp(message.created_at),
    )


def session_domain_to_proto(session: ChatSession) -> chat_session_pb2.ChatSession:
    """แปลง ChatSession Domain Entity เป็น Protobuf Message"""
    proto_messages = [message_domain_to_proto(msg) for msg in session.messages]

    return chat_session_pb2.ChatSession(
        id=session.id or "",
        user_id=session.user_id,
        chatbot_id=session.chatbot_id,
        session_title=session.session_title,
        messages=proto_messages,
        created_at=datetime_to_timestamp(session.created_at),
        updated_at=datetime_to_timestamp(session.updated_at),
    )


# ==============================================================================
# gRPC SERVICE / CONTROLLER
# ==============================================================================


class ChatSessionGrpcService(chat_session_pb2_grpc.ChatSessionServiceServicer):
    """
    gRPC Controller / Presentation Layer สำหรับจัดการ Chat Session และ Chat Message
    ทำหน้าที่รับ-ส่ง gRPC Requests/Responses และ Delegate การทำงานให้ Use Cases
    """

    def __init__(
        self,
        create_session_usecase: CreateChatSessionUseCase,
        get_session_usecase: GetChatSessionUseCase,
        get_chat_history_usecase: GetChatHistoryUseCase,
        list_sessions_usecase: ListUserChatSessionsUseCase,
        add_message_usecase: AddChatMessageUseCase,
        delete_session_usecase: DeleteChatSessionUseCase,
    ):
        self.create_session_usecase = create_session_usecase
        self.get_session_usecase = get_session_usecase
        self.get_chat_history_usecase = get_chat_history_usecase
        self.list_sessions_usecase = list_sessions_usecase
        self.add_message_usecase = add_message_usecase
        self.delete_session_usecase = delete_session_usecase

    async def CreateChatSession(
        self,
        request: chat_session_pb2.CreateChatSessionRequest,
        context: grpc.aio.ServicerContext,
    ) -> chat_session_pb2.CreateChatSessionResponse:
        """RPC สำหรับสร้าง Chat Session ใหม่"""
        try:
            dto = CreateChatSessionDTO(
                user_id=request.user_id,
                chatbot_id=request.chatbot_id,
                session_title=request.session_title
                if request.session_title
                else "New Chat",
            )
            session = await self.create_session_usecase.execute(dto)
            return chat_session_pb2.CreateChatSessionResponse(
                session=session_domain_to_proto(session)
            )
        except Exception as e:
            logger.error(f"Error in CreateChatSession: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL, f"Failed to create chat session: {e}"
            )

    async def GetChatSession(
        self,
        request: chat_session_pb2.GetChatSessionRequest,
        context: grpc.aio.ServicerContext,
    ) -> chat_session_pb2.GetChatSessionResponse:
        """RPC สำหรับดึงข้อมูล Session และประวัติการสนทนาตาม Session ID"""
        try:
            session = await self.get_session_usecase.execute(
                session_id=request.id,
                user_id=request.user_id,
            )

            if not session:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Not found session")

            return chat_session_pb2.GetChatSessionResponse(
                session=session_domain_to_proto(session)
            )
        except ValueError as e:
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"Error in GetChatSession: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal server error: {e}")

    async def ListChatSessions(
        self,
        request: chat_session_pb2.ListChatSessionsRequest,
        context: grpc.aio.ServicerContext,
    ) -> chat_session_pb2.ListChatSessionsResponse:
        """RPC สำหรับดึงรายการ Chat Sessions ของผู้ใช้"""
        try:
            chatbot_id = request.chatbot_id if request.chatbot_id else None
            sessions = await self.list_sessions_usecase.execute(
                user_id=request.user_id,
                chatbot_id=chatbot_id,
            )

            proto_sessions = [session_domain_to_proto(s) for s in sessions]
            return chat_session_pb2.ListChatSessionsResponse(
                sessions=proto_sessions,
                total_count=len(proto_sessions),
            )
        except Exception as e:
            logger.error(f"Error in ListChatSessions: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL, f"Failed to list chat sessions: {e}"
            )

    async def AddChatMessage(
        self,
        request: chat_session_pb2.AddChatMessageRequest,
        context: grpc.aio.ServicerContext,
    ) -> chat_session_pb2.AddChatMessageResponse:
        """RPC สำหรับเพิ่มข้อความสนทนาลงใน Session"""
        try:
            domain_role = role_proto_to_domain(request.role)
            dto = AddChatMessageDTO(
                session_id=request.session_id,
                user_id=request.user_id,
                role=domain_role,
                content=request.content,
            )
            added_message = await self.add_message_usecase.execute(dto)
            return chat_session_pb2.AddChatMessageResponse(
                message=message_domain_to_proto(added_message)
            )
        except ValueError as e:
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            logger.error(f"Error in AddChatMessage: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL, f"Failed to add chat message: {e}"
            )

    async def DeleteChatSession(
        self,
        request: chat_session_pb2.DeleteChatSessionRequest,
        context: grpc.aio.ServicerContext,
    ) -> Empty:
        """RPC สำหรับลบ Chat Session"""
        try:
            success = await self.delete_session_usecase.execute(
                session_id=request.id,
                user_id=request.user_id,
            )
            if not success:
                await context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    "Chat session not found or already deleted",
                )
            return Empty()
        except Exception as e:
            logger.error(f"Error in DeleteChatSession: {e}")
            await context.abort(
                grpc.StatusCode.INTERNAL, f"Failed to delete chat session: {e}"
            )
