from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RagSearchSimilarRequestDTO(_message.Message):
    __slots__ = ("user_id", "chatbot_id", "query_text", "top_k", "knowledge_file_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CHATBOT_ID_FIELD_NUMBER: _ClassVar[int]
    QUERY_TEXT_FIELD_NUMBER: _ClassVar[int]
    TOP_K_FIELD_NUMBER: _ClassVar[int]
    KNOWLEDGE_FILE_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    chatbot_id: str
    query_text: str
    top_k: int
    knowledge_file_id: str
    def __init__(self, user_id: _Optional[str] = ..., chatbot_id: _Optional[str] = ..., query_text: _Optional[str] = ..., top_k: _Optional[int] = ..., knowledge_file_id: _Optional[str] = ...) -> None: ...

class RagResponseDTO(_message.Message):
    __slots__ = ("answer_message", "sources")
    ANSWER_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SOURCES_FIELD_NUMBER: _ClassVar[int]
    answer_message: str
    sources: _containers.RepeatedCompositeFieldContainer[SearchVectorRecordItemDTO]
    def __init__(self, answer_message: _Optional[str] = ..., sources: _Optional[_Iterable[_Union[SearchVectorRecordItemDTO, _Mapping]]] = ...) -> None: ...

class SearchVectorRecordItemDTO(_message.Message):
    __slots__ = ("score", "record")
    SCORE_FIELD_NUMBER: _ClassVar[int]
    RECORD_FIELD_NUMBER: _ClassVar[int]
    score: float
    record: VectorRecordDTO
    def __init__(self, score: _Optional[float] = ..., record: _Optional[_Union[VectorRecordDTO, _Mapping]] = ...) -> None: ...

class VectorRecordDTO(_message.Message):
    __slots__ = ("id", "values", "metadata")
    ID_FIELD_NUMBER: _ClassVar[int]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    id: str
    values: _containers.RepeatedScalarFieldContainer[float]
    metadata: MetadataVectorRecordDTO
    def __init__(self, id: _Optional[str] = ..., values: _Optional[_Iterable[float]] = ..., metadata: _Optional[_Union[MetadataVectorRecordDTO, _Mapping]] = ...) -> None: ...

class MetadataVectorRecordDTO(_message.Message):
    __slots__ = ("user_id", "chatbot_id", "file_id", "chunk_index", "text_content", "page_number", "filename")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    CHATBOT_ID_FIELD_NUMBER: _ClassVar[int]
    FILE_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_INDEX_FIELD_NUMBER: _ClassVar[int]
    TEXT_CONTENT_FIELD_NUMBER: _ClassVar[int]
    PAGE_NUMBER_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    chatbot_id: str
    file_id: str
    chunk_index: int
    text_content: str
    page_number: int
    filename: str
    def __init__(self, user_id: _Optional[str] = ..., chatbot_id: _Optional[str] = ..., file_id: _Optional[str] = ..., chunk_index: _Optional[int] = ..., text_content: _Optional[str] = ..., page_number: _Optional[int] = ..., filename: _Optional[str] = ...) -> None: ...
