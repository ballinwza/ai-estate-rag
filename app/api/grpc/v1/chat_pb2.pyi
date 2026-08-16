import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
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

class ChatRequest(_message.Message):
    __slots__ = ("question",)
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    question: str
    def __init__(self, question: _Optional[str] = ...) -> None: ...

class ChatResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class PdfMetadata(_message.Message):
    __slots__ = ("filename", "file_size")
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    FILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    filename: str
    file_size: int
    def __init__(self, filename: _Optional[str] = ..., file_size: _Optional[int] = ...) -> None: ...

class UploadPdfRequest(_message.Message):
    __slots__ = ("metadata", "chunk_data")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CHUNK_DATA_FIELD_NUMBER: _ClassVar[int]
    metadata: PdfMetadata
    chunk_data: bytes
    def __init__(self, metadata: _Optional[_Union[PdfMetadata, _Mapping]] = ..., chunk_data: _Optional[bytes] = ...) -> None: ...

class UploadPdfResponse(_message.Message):
    __slots__ = ("file_id", "success", "message")
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    file_id: str
    success: bool
    message: str
    def __init__(self, file_id: _Optional[str] = ..., success: _Optional[bool] = ..., message: _Optional[str] = ...) -> None: ...

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
