from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict

from esmerald.openapi.enums import APIKeyIn, SecuritySchemeType
from esmerald.openapi.models import SecurityScheme


class HTTPAuthorizationCredentials(BaseModel):
    scheme: str
    credentials: str


class Bearer(SecurityScheme):
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

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
            type=type_,
            description=description,
            bearerFormat=bearerFormat,
            name=name,
            **kwargs,
        )
        self.scheme_name = scheme_name or self.__class__.__name__
        self.security_scheme_in = in_
        self.name = name or "Authorization"
        self.scheme = scheme or "bearer"
