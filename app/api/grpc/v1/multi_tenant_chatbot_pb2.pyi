import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import field_mask_pb2 as _field_mask_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ChatbotBlueprint(_message.Message):
    __slots__ = ("id", "user_id", "name", "description", "system_prompt", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_PROMPT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: str
    name: str
    description: str
    system_prompt: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., user_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., system_prompt: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateMultiTenantChatbotRequest(_message.Message):
    __slots__ = ("user_id", "name", "description", "system_prompt")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_PROMPT_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    name: str
    description: str
    system_prompt: str
    def __init__(self, user_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., system_prompt: _Optional[str] = ...) -> None: ...

class CreateMultiTenantChatbotResponse(_message.Message):
    __slots__ = ("chatbot",)
    CHATBOT_FIELD_NUMBER: _ClassVar[int]
    chatbot: ChatbotBlueprint
    def __init__(self, chatbot: _Optional[_Union[ChatbotBlueprint, _Mapping]] = ...) -> None: ...

class GetMultiTenantChatbotRequest(_message.Message):
    __slots__ = ("id", "user_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: str
    def __init__(self, id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class GetMultiTenantChatbotResponse(_message.Message):
    __slots__ = ("chatbot",)
    CHATBOT_FIELD_NUMBER: _ClassVar[int]
    chatbot: ChatbotBlueprint
    def __init__(self, chatbot: _Optional[_Union[ChatbotBlueprint, _Mapping]] = ...) -> None: ...

class ListMultiTenantChatbotsRequest(_message.Message):
    __slots__ = ("user_id", "page_size", "page_token")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    page_size: int
    page_token: int
    def __init__(self, user_id: _Optional[str] = ..., page_size: _Optional[int] = ..., page_token: _Optional[int] = ...) -> None: ...

class ListMultiTenantChatbotsResponse(_message.Message):
    __slots__ = ("chatbots", "next_page_token", "total_count")
    CHATBOTS_FIELD_NUMBER: _ClassVar[int]
    NEXT_PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    chatbots: _containers.RepeatedCompositeFieldContainer[ChatbotBlueprint]
    next_page_token: int
    total_count: int
    def __init__(self, chatbots: _Optional[_Iterable[_Union[ChatbotBlueprint, _Mapping]]] = ..., next_page_token: _Optional[int] = ..., total_count: _Optional[int] = ...) -> None: ...

class UpdateMultiTenantChatbotRequest(_message.Message):
    __slots__ = ("id", "user_id", "name", "description", "system_prompt", "update_mask")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_PROMPT_FIELD_NUMBER: _ClassVar[int]
    UPDATE_MASK_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: str
    name: str
    description: str
    system_prompt: str
    update_mask: _field_mask_pb2.FieldMask
    def __init__(self, id: _Optional[str] = ..., user_id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., system_prompt: _Optional[str] = ..., update_mask: _Optional[_Union[_field_mask_pb2.FieldMask, _Mapping]] = ...) -> None: ...

class UpdateMultiTenantChatbotResponse(_message.Message):
    __slots__ = ("chatbot",)
    CHATBOT_FIELD_NUMBER: _ClassVar[int]
    chatbot: ChatbotBlueprint
    def __init__(self, chatbot: _Optional[_Union[ChatbotBlueprint, _Mapping]] = ...) -> None: ...

class DeleteMultiTenantChatbotRequest(_message.Message):
    __slots__ = ("id", "user_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: str
    def __init__(self, id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class DeleteMultiTenantChatbotResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: _Optional[bool] = ..., message: _Optional[str] = ...) -> None: ...
