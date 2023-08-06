from typing import ClassVar as _ClassVar
from typing import Optional as _Optional

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message

DESCRIPTOR: _descriptor.FileDescriptor

class EmbeddingInfoRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class EmbeddingInfoResponse(_message.Message):
    __slots__ = ["vector_size"]
    VECTOR_SIZE_FIELD_NUMBER: _ClassVar[int]
    vector_size: int
    def __init__(self, vector_size: _Optional[int] = ...) -> None: ...

class EmbeddingRequest(_message.Message):
    __slots__ = ["data"]
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    def __init__(self, data: _Optional[bytes] = ...) -> None: ...

class EmbeddingResponse(_message.Message):
    __slots__ = ["embeddings"]
    EMBEDDINGS_FIELD_NUMBER: _ClassVar[int]
    embeddings: bytes
    def __init__(self, embeddings: _Optional[bytes] = ...) -> None: ...
