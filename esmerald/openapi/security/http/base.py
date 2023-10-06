from typing import Any, Literal, Optional

from esmerald.openapi.enums import APIKeyIn, Header, SecuritySchemeType
from esmerald.openapi.security.base import HTTPBase


class Basic(HTTPBase):
    def __init__(
        self,
        *,
        type_: Literal[
            "apiKey", "http", "mutualTLS", "oauth2", "openIdConnect"
        ] = SecuritySchemeType.http.value,
        bearerFormat: Optional[str] = None,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        in_: Optional[Literal["query", "header", "cookie"]] = APIKeyIn.header.value,
        name: Optional[str] = None,
        scheme: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(
            type_=type_,
            bearerFormat=bearerFormat,
            description=description,
            name=name or "Basic",
            in_=in_,
            scheme=scheme or "basic",
            scheme_name=scheme_name or self.__class__.__name__,
            **kwargs,
        )


class Bearer(HTTPBase):
    def __init__(
        self,
        *,
        type_: Literal[
            "apiKey", "http", "mutualTLS", "oauth2", "openIdConnect"
        ] = SecuritySchemeType.http.value,
        bearerFormat: Optional[str] = None,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        in_: Optional[Literal["query", "header", "cookie"]] = APIKeyIn.header.value,
        name: Optional[str] = None,
        scheme: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(
            type_=type_,
            bearerFormat=bearerFormat,
            description=description,
            name=name or Header.authorization,
            in_=in_,
            scheme=scheme or "bearer",
            scheme_name=scheme_name or self.__class__.__name__,
            **kwargs,
        )


class Digest(HTTPBase):
    def __init__(
        self,
        *,
        type_: Literal[
            "apiKey", "http", "mutualTLS", "oauth2", "openIdConnect"
        ] = SecuritySchemeType.http.value,
        bearerFormat: Optional[str] = None,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        in_: Optional[Literal["query", "header", "cookie"]] = APIKeyIn.header.value,
        name: Optional[str] = None,
        scheme: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(
            type_=type_,
            bearerFormat=bearerFormat,
            description=description,
            name=name or Header.authorization,
            in_=in_,
            scheme=scheme or "digest",
            scheme_name=scheme_name or self.__class__.__name__,
            **kwargs,
        )
