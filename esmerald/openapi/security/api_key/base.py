from typing import Any, Literal, Optional

from esmerald.openapi.enums import APIKeyIn, SecuritySchemeType
from esmerald.openapi.security.base import HTTPBase


class APIKeyInQuery(HTTPBase):
    def __init__(
        self,
        *,
        type_: Literal[
            "apiKey", "http", "mutualTLS", "oauth2", "openIdConnect"
        ] = SecuritySchemeType.apiKey.value,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        in_: Optional[Literal["query", "header", "cookie"]] = APIKeyIn.query.value,
        name: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(
            type_=type_,
            description=description,
            name=name,
            in_=in_,
            scheme_name=scheme_name or self.__class__.__name__,
            **kwargs,
        )


class APIKeyInHeader(HTTPBase):
    def __init__(
        self,
        *,
        type_: Literal[
            "apiKey", "http", "mutualTLS", "oauth2", "openIdConnect"
        ] = SecuritySchemeType.apiKey.value,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        in_: Optional[Literal["query", "header", "cookie"]] = APIKeyIn.header.value,
        name: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(
            type_=type_,
            description=description,
            name=name,
            in_=in_,
            scheme_name=scheme_name or self.__class__.__name__,
            **kwargs,
        )


class APIKeyInCookie(HTTPBase):
    def __init__(
        self,
        *,
        type_: Literal[
            "apiKey", "http", "mutualTLS", "oauth2", "openIdConnect"
        ] = SecuritySchemeType.apiKey.value,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        in_: Optional[Literal["query", "header", "cookie"]] = APIKeyIn.cookie.value,
        name: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(
            type_=type_,
            description=description,
            name=name,
            in_=in_,
            scheme_name=scheme_name or self.__class__.__name__,
            **kwargs,
        )
