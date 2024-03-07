from enum import Enum


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return self.value  # type: ignore

    def __repr__(self) -> str:
        return str(self)


class HttpMethod(StrEnum, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"


class MediaType(StrEnum, Enum):
    JSON = "application/json"
    HTML = "text/html"
    TEXT = "text/plain"
    MESSAGE_PACK = "application/x-msgpack"
    TEXT_CHARSET = "text/plain; charset=utf-8"
    PNG = "image/png"
    OCTET = "application/octet-stream"


class OpenAPIMediaType(StrEnum, Enum):
    OPENAPI_YAML = "application/vnd.oai.openapi"
    OPENAPI_JSON = "application/vnd.oai.openapi+json"


class EncodingType(StrEnum, Enum):
    JSON = "application/json"
    MULTI_PART = "multipart/form-data"
    URL_ENCODED = "application/x-www-form-urlencoded"


class ScopeType(StrEnum, Enum):
    HTTP = "http"
    WEBSOCKET = "websocket"


class ParamType(StrEnum, Enum):
    PATH = "path"
    QUERY = "query"
    COOKIE = "cookie"
    HEADER = "header"
