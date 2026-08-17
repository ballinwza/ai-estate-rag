import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FileStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PENDING: _ClassVar[FileStatus]
    COMPLETED: _ClassVar[FileStatus]
    FAILED: _ClassVar[FileStatus]
PENDING: FileStatus
COMPLETED: FileStatus
FAILED: FileStatus

class Chunk(_message.Message):
    __slots__ = ("vector_id", "chunk_index", "text_content", "page_number", "token_count")
    VECTOR_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_INDEX_FIELD_NUMBER: _ClassVar[int]
    TEXT_CONTENT_FIELD_NUMBER: _ClassVar[int]
    PAGE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    TOKEN_COUNT_FIELD_NUMBER: _ClassVar[int]
    vector_id: str
    chunk_index: int
    text_content: str
    page_number: int
    token_count: int
    def __init__(self, vector_id: _Optional[str] = ..., chunk_index: _Optional[int] = ..., text_content: _Optional[str] = ..., page_number: _Optional[int] = ..., token_count: _Optional[int] = ...) -> None: ...

class KnowledgeFile(_message.Message):
    __slots__ = ("id", "user_id", "chatbot_id", "filename", "file_type", "file_size_bytes", "status", "total_chunks", "chunks", "total_page", "text_content", "error_message", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CHATBOT_ID_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    FILE_TYPE_FIELD_NUMBER: _ClassVar[int]
    FILE_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CHUNKS_FIELD_NUMBER: _ClassVar[int]
    CHUNKS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PAGE_FIELD_NUMBER: _ClassVar[int]
    TEXT_CONTENT_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: str
    chatbot_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    status: FileStatus
    total_chunks: int
    chunks: _containers.RepeatedCompositeFieldContainer[Chunk]
    total_page: int
    text_content: str
    error_message: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., user_id: _Optional[str] = ..., chatbot_id: _Optional[str] = ..., filename: _Optional[str] = ..., file_type: _Optional[str] = ..., file_size_bytes: _Optional[int] = ..., status: _Optional[_Union[FileStatus, str]] = ..., total_chunks: _Optional[int] = ..., chunks: _Optional[_Iterable[_Union[Chunk, _Mapping]]] = ..., total_page: _Optional[int] = ..., text_content: _Optional[str] = ..., error_message: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class FileMetadata(_message.Message):
    __slots__ = ("user_id", "chatbot_id", "filename", "file_type")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CHATBOT_ID_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    FILE_TYPE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    chatbot_id: str
    filename: str
    file_type: str
    def __init__(self, user_id: _Optional[str] = ..., chatbot_id: _Optional[str] = ..., filename: _Optional[str] = ..., file_type: _Optional[str] = ...) -> None: ...

class UploadFileStreamRequest(_message.Message):
    __slots__ = ("metadata", "chunk_data")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CHUNK_DATA_FIELD_NUMBER: _ClassVar[int]
    metadata: FileMetadata
    chunk_data: bytes
    def __init__(self, metadata: _Optional[_Union[FileMetadata, _Mapping]] = ..., chunk_data: _Optional[bytes] = ...) -> None: ...

class UploadFileStreamResponse(_message.Message):
    __slots__ = ("file_id", "status", "total_chunks", "total_bytes", "message", "created_at")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_CHUNKS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_BYTES_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    status: FileStatus
    total_chunks: int
    total_bytes: int
    message: str
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, file_id: _Optional[str] = ..., status: _Optional[_Union[FileStatus, str]] = ..., total_chunks: _Optional[int] = ..., total_bytes: _Optional[int] = ..., message: _Optional[str] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class GetKnowledgeFileRequest(_message.Message):
    __slots__ = ("id", "user_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    user_id: str
    def __init__(self, id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class GetKnowledgeFileResponse(_message.Message):
    __slots__ = ("file",)
    FILE_FIELD_NUMBER: _ClassVar[int]
    file: KnowledgeFile
    def __init__(self, file: _Optional[_Union[KnowledgeFile, _Mapping]] = ...) -> None: ...

class ListKnowledgeFilesRequest(_message.Message):
    __slots__ = ("user_id", "chatbot_id", "limit", "offset")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CHATBOT_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    chatbot_id: str
    limit: int
    offset: int
    def __init__(self, user_id: _Optional[str] = ..., chatbot_id: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class ListKnowledgeFilesResponse(_message.Message):
    __slots__ = ("files", "total_count")
    FILES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    files: _containers.RepeatedCompositeFieldContainer[KnowledgeFile]
    total_count: int
    def __init__(self, files: _Optional[_Iterable[_Union[KnowledgeFile, _Mapping]]] = ..., total_count: _Optional[int] = ...) -> None: ...

class DeleteKnowledgeFileRequest(_message.Message):
    __slots__ = ("chatbot_id", "user_id")
    CHATBOT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    chatbot_id: str
    user_id: str
    def __init__(self, chatbot_id: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class DeleteKnowledgeFileResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: _Optional[bool] = ..., message: _Optional[str] = ...) -> None: ...
