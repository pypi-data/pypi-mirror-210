from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class _Cache(_message.Message):
    __slots__ = ["cache_name"]
    CACHE_NAME_FIELD_NUMBER: _ClassVar[int]
    cache_name: str
    def __init__(self, cache_name: _Optional[str] = ...) -> None: ...

class _CreateCacheRequest(_message.Message):
    __slots__ = ["cache_name"]
    CACHE_NAME_FIELD_NUMBER: _ClassVar[int]
    cache_name: str
    def __init__(self, cache_name: _Optional[str] = ...) -> None: ...

class _CreateCacheResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class _CreateSigningKeyRequest(_message.Message):
    __slots__ = ["ttl_minutes"]
    TTL_MINUTES_FIELD_NUMBER: _ClassVar[int]
    ttl_minutes: int
    def __init__(self, ttl_minutes: _Optional[int] = ...) -> None: ...

class _CreateSigningKeyResponse(_message.Message):
    __slots__ = ["expires_at", "key"]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    expires_at: int
    key: str
    def __init__(self, key: _Optional[str] = ..., expires_at: _Optional[int] = ...) -> None: ...

class _DeleteCacheRequest(_message.Message):
    __slots__ = ["cache_name"]
    CACHE_NAME_FIELD_NUMBER: _ClassVar[int]
    cache_name: str
    def __init__(self, cache_name: _Optional[str] = ...) -> None: ...

class _DeleteCacheResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class _FlushCacheRequest(_message.Message):
    __slots__ = ["cache_name"]
    CACHE_NAME_FIELD_NUMBER: _ClassVar[int]
    cache_name: str
    def __init__(self, cache_name: _Optional[str] = ...) -> None: ...

class _FlushCacheResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class _ListCachesRequest(_message.Message):
    __slots__ = ["next_token"]
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    next_token: str
    def __init__(self, next_token: _Optional[str] = ...) -> None: ...

class _ListCachesResponse(_message.Message):
    __slots__ = ["cache", "next_token"]
    CACHE_FIELD_NUMBER: _ClassVar[int]
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    cache: _containers.RepeatedCompositeFieldContainer[_Cache]
    next_token: str
    def __init__(self, cache: _Optional[_Iterable[_Union[_Cache, _Mapping]]] = ..., next_token: _Optional[str] = ...) -> None: ...

class _ListSigningKeysRequest(_message.Message):
    __slots__ = ["next_token"]
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    next_token: str
    def __init__(self, next_token: _Optional[str] = ...) -> None: ...

class _ListSigningKeysResponse(_message.Message):
    __slots__ = ["next_token", "signing_key"]
    NEXT_TOKEN_FIELD_NUMBER: _ClassVar[int]
    SIGNING_KEY_FIELD_NUMBER: _ClassVar[int]
    next_token: str
    signing_key: _containers.RepeatedCompositeFieldContainer[_SigningKey]
    def __init__(self, signing_key: _Optional[_Iterable[_Union[_SigningKey, _Mapping]]] = ..., next_token: _Optional[str] = ...) -> None: ...

class _RevokeSigningKeyRequest(_message.Message):
    __slots__ = ["key_id"]
    KEY_ID_FIELD_NUMBER: _ClassVar[int]
    key_id: str
    def __init__(self, key_id: _Optional[str] = ...) -> None: ...

class _RevokeSigningKeyResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class _SigningKey(_message.Message):
    __slots__ = ["expires_at", "key_id"]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    KEY_ID_FIELD_NUMBER: _ClassVar[int]
    expires_at: int
    key_id: str
    def __init__(self, key_id: _Optional[str] = ..., expires_at: _Optional[int] = ...) -> None: ...
