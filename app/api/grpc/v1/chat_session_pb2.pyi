import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MessageRole(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MESSAGE_ROLE_UNSPECIFIED: _ClassVar[MessageRole]
    USER: _ClassVar[MessageRole]
    AI: _ClassVar[MessageRole]
    SYSTEM: _ClassVar[MessageRole]
MESSAGE_ROLE_UNSPECIFIED: MessageRole
USER: MessageRole
AI: MessageRole
SYSTEM: MessageRole

class ChatMessage(_message.Message):
    __slots__ = ("role", "content", "created_at")
    ROLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    role: MessageRole
    content: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, role: _Optional[_Union[MessageRole, str]] = ..., content: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ChatSession(_message.Message):
    __slots__ = ("id", "user_id", "chatbot_id", "session_title", "messages", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CHATBOT_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_TITLE_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: str
    chatbot_id: str
    session_title: str
    messages: _containers.RepeatedCompositeFieldContainer[ChatMessage]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., user_id: _Optional[str] = ..., chatbot_id: _Optional[str] = ..., session_title: _Optional[str] = ..., messages: _Optional[_Iterable[_Union[ChatMessage, _Mapping]]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateChatSessionRequest(_message.Message):
    __slots__ = ("user_id", "chatbot_id", "session_title")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CHATBOT_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_TITLE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    chatbot_id: str
    session_title: str
    def __init__(self, user_id: _Optional[str] = ..., chatbot_id: _Optional[str] = ..., session_title: _Optional[str] = ...) -> None: ...

class CreateChatSessionResponse(_message.Message):
    __slots__ = ("session",)
    SESSION_FIELD_NUMBER: _ClassVar[int]
    session: ChatSession
    def __init__(self, session: _Optional[_Union[ChatSession, _Mapping]] = ...) -> None: ...

class GetChatSessionRequest(_message.Message):
    __slots__ = ("id", "user_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: str
    def __init__(self, id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class GetChatSessionResponse(_message.Message):
    __slots__ = ("session",)
    SESSION_FIELD_NUMBER: _ClassVar[int]
    session: ChatSession
    def __init__(self, session: _Optional[_Union[ChatSession, _Mapping]] = ...) -> None: ...

class ListChatSessionsRequest(_message.Message):
    __slots__ = ("user_id", "chatbot_id", "page_size", "page_token")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CHATBOT_ID_FIELD_NUMBER: _ClassVar[int]
    PAGE_SIZE_FIELD_NUMBER: _ClassVar[int]
    PAGE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    chatbot_id: str
    page_size: int
    page_token: int
    def __init__(self, user_id: _Optional[str] = ..., chatbot_id: _Optional[str] = ..., page_size: _Optional[int] = ..., page_token: _Optional[int] = ...) -> None: ...

class ListChatSessionsResponse(_message.Message):
    __slots__ = ("sessions", "total_count")
    SESSIONS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    sessions: _containers.RepeatedCompositeFieldContainer[ChatSession]
    total_count: int
    def __init__(self, sessions: _Optional[_Iterable[_Union[ChatSession, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class AddChatMessageRequest(_message.Message):
    __slots__ = ("session_id", "user_id", "role", "content")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_id: str
    role: MessageRole
    content: str
    def __init__(self, session_id: _Optional[str] = ..., user_id: _Optional[str] = ..., role: _Optional[_Union[MessageRole, str]] = ..., content: _Optional[str] = ...) -> None: ...

class AddChatMessageResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: ChatMessage
    def __init__(self, message: _Optional[_Union[ChatMessage, _Mapping]] = ...) -> None: ...

class DeleteChatSessionRequest(_message.Message):
    __slots__ = ("id", "user_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: str
    def __init__(self, id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...
