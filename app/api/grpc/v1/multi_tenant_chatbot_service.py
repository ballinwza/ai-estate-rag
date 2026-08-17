import grpc
import grpc.aio
from google.protobuf.timestamp_pb2 import Timestamp

from app.api.dto.multi_tenant_dto import (
    CreateMultiTenantChatbotDTO,
    DeleteMultiTenantChatbotDTO,
    GetMultiTenantChatbotDTO,
    ListMultiTenantChatbotsDTO,
    UpdateMultiTenantChatbotDTO,
)
from app.api.grpc.v1 import multi_tenant_chatbot_pb2, multi_tenant_chatbot_pb2_grpc
from app.domain.entities.multi_tenant_doc import ChatbotBlueprint
from app.usecases.multi_tenant.chatbot import (
    CreateMultiTenantChatbotUseCase,
    DeleteMultiTenantChatbotUseCase,
    GetMultiTenantChatbotUseCase,
    ListUserMultiTenantChatbotsUseCase,
    UpdateMultiTenantChatbotUseCase,
)

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================


def datetime_to_timestamp(dt) -> Timestamp:
    """แปลง datetime.datetime (UTC) ให้เป็น google.protobuf.Timestamp"""
    ts = Timestamp()
    if dt:
        ts.FromDatetime(dt)
    return ts


def domain_to_proto(
    chatbot: ChatbotBlueprint,
) -> multi_tenant_chatbot_pb2.ChatbotBlueprint:
    """แปลง Pydantic Domain Model เป็น gRPC Protobuf Message"""
    return multi_tenant_chatbot_pb2.ChatbotBlueprint(
        id=chatbot.id or "",
        user_id=chatbot.user_id,
        name=chatbot.name,
        description=chatbot.description,
        system_prompt=chatbot.system_prompt,
        created_at=datetime_to_timestamp(chatbot.created_at),
        updated_at=datetime_to_timestamp(chatbot.updated_at),
    )


# ==============================================================================
# gRPC SERVICE / CONTROLLER
# ==============================================================================


class ChatbotGrpcService(multi_tenant_chatbot_pb2_grpc.ChatbotServiceServicer):
    """
    gRPC Controller / Presentation Layer สำหรับจัดการ Chatbot Blueprint
    ทำหน้าที่รับ-ส่ง gRPC Requests/Responses และ Delegate การทำงานให้ Use Cases
    """

    def __init__(
        self,
        create_use_case: CreateMultiTenantChatbotUseCase,
        get_use_case: GetMultiTenantChatbotUseCase,
        list_use_case: ListUserMultiTenantChatbotsUseCase,
        update_use_case: UpdateMultiTenantChatbotUseCase,
        delete_use_case: DeleteMultiTenantChatbotUseCase,
    ):
        self.create_use_case = create_use_case
        self.get_use_case = get_use_case
        self.list_use_case = list_use_case
        self.update_use_case = update_use_case
        self.delete_use_case = delete_use_case

    async def CreateMultiTenantChatbot(
        self,
        request: multi_tenant_chatbot_pb2.CreateMultiTenantChatbotRequest,
        context: grpc.aio.ServicerContext,
    ) -> multi_tenant_chatbot_pb2.CreateMultiTenantChatbotResponse:
        """RPC สำหรับสร้าง Chatbot Blueprint"""
        try:
            dto = CreateMultiTenantChatbotDTO(
                user_id=request.user_id,
                name=request.name,
                description=request.description,
                system_prompt=request.system_prompt,
            )
            chatbot = await self.create_use_case.execute(dto)
            return multi_tenant_chatbot_pb2.CreateMultiTenantChatbotResponse(
                chatbot=domain_to_proto(chatbot)
            )
        except Exception as e:
            await context.abort(
                grpc.StatusCode.INTERNAL, f"Failed to create chatbot: {e}"
            )

    async def GetMultiTenantChatbot(
        self,
        request: multi_tenant_chatbot_pb2.GetMultiTenantChatbotRequest,
        context: grpc.aio.ServicerContext,
    ) -> multi_tenant_chatbot_pb2.GetMultiTenantChatbotResponse:
        """RPC สำหรับดึงข้อมูล Chatbot Blueprint ตาม ID"""
        try:
            dto = GetMultiTenantChatbotDTO(
                chatbot_id=request.id, user_id=request.user_id
            )
            chatbot = await self.get_use_case.execute(dto)
            if chatbot == None:
                await context.abort(grpc.StatusCode.NOT_FOUND, "Not found Chatbot")

            return multi_tenant_chatbot_pb2.GetMultiTenantChatbotResponse(
                chatbot=domain_to_proto(chatbot)
            )
        except ValueError as e:
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            await context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {e}")

    async def ListMultiTenantChatbots(
        self,
        request: multi_tenant_chatbot_pb2.ListMultiTenantChatbotsRequest,
        context: grpc.aio.ServicerContext,
    ) -> multi_tenant_chatbot_pb2.ListMultiTenantChatbotsResponse:
        """RPC สำหรับดึงรายการ Chatbot Blueprint ( Pagination )"""
        try:
            limit = request.page_size if request.page_size > 0 else 10
            offset = max(request.page_token, 0)

            dto = ListMultiTenantChatbotsDTO(
                user_id=request.user_id,
                limit=limit,
                offset=offset,
            )
            chatbots = await self.list_use_case.execute(dto)

            proto_chatbots = [domain_to_proto(c) for c in chatbots]

            # กำหนด next_page_token ถ้าได้จำนวนข้อมูลเท่ากับ limit (แปลว่าอาจจะมีหน้าถัดไป)
            next_page_token = offset + len(chatbots) if len(chatbots) == limit else 0

            return multi_tenant_chatbot_pb2.ListMultiTenantChatbotsResponse(
                chatbots=proto_chatbots,
                next_page_token=next_page_token,
                total_count=len(proto_chatbots),
            )
        except Exception as e:
            await context.abort(
                grpc.StatusCode.INTERNAL, f"Failed to list chatbots: {e}"
            )

    async def UpdateMultiTenantChatbot(
        self,
        request: multi_tenant_chatbot_pb2.UpdateMultiTenantChatbotRequest,
        context: grpc.aio.ServicerContext,
    ) -> multi_tenant_chatbot_pb2.UpdateMultiTenantChatbotResponse:
        """RPC สำหรับแก้ไข Chatbot Blueprint (รองรับ FieldMask)"""
        try:
            update_fields = {}

            # ถ้ามีการส่ง FieldMask มา ให้แก้ไขเฉพาะ field ที่ระบุ
            if request.HasField("update_mask") and request.update_mask.paths:
                paths = request.update_mask.paths
                if "name" in paths:
                    update_fields["name"] = request.name
                if "description" in paths:
                    update_fields["description"] = request.description
                if "system_prompt" in paths:
                    update_fields["system_prompt"] = request.system_prompt
            else:
                # ถ้าไม่ได้ระบุ FieldMask ให้ดูจากฟิลด์ที่ไม่ว่าง
                if request.name:
                    update_fields["name"] = request.name
                if request.description:
                    update_fields["description"] = request.description
                if request.system_prompt:
                    update_fields["system_prompt"] = request.system_prompt

            dto = UpdateMultiTenantChatbotDTO(
                chatbot_id=request.id, user_id=request.user_id, **update_fields
            )

            updated_chatbot = await self.update_use_case.execute(dto)
            return multi_tenant_chatbot_pb2.UpdateMultiTenantChatbotResponse(
                chatbot=domain_to_proto(updated_chatbot)
            )
        except ValueError as e:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
        except Exception as e:
            await context.abort(
                grpc.StatusCode.INTERNAL, f"Failed to update chatbot: {e}"
            )

    async def DeleteMultiTenantChatbot(
        self,
        request: multi_tenant_chatbot_pb2.DeleteMultiTenantChatbotRequest,
        context: grpc.aio.ServicerContext,
    ) -> multi_tenant_chatbot_pb2.DeleteMultiTenantChatbotResponse:
        """RPC สำหรับลบ Chatbot Blueprint"""
        try:
            dto = DeleteMultiTenantChatbotDTO(
                chatbot_id=request.id, user_id=request.user_id
            )
            success = await self.delete_use_case.execute(dto)
            return multi_tenant_chatbot_pb2.DeleteMultiTenantChatbotResponse(
                success=success, message="Chatbot blueprint deleted successfully."
            )
        except ValueError as e:
            await context.abort(grpc.StatusCode.NOT_FOUND, str(e))
        except Exception as e:
            await context.abort(
                grpc.StatusCode.INTERNAL, f"Failed to delete chatbot: {e}"
            )
