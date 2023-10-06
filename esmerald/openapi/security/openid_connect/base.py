from typing import Any, Literal, Optional, Union

from pydantic import AnyUrl

from esmerald.openapi.enums import SecuritySchemeType
from esmerald.openapi.security.base import HTTPBase


class OpenIdConnect(HTTPBase):
    def __init__(
        self,
        *,
        type_: Literal[
            "apiKey", "http", "mutualTLS", "oauth2", "openIdConnect"
        ] = SecuritySchemeType.openIdConnect.value,
        openIdConnectUrl: Optional[Union[AnyUrl, str]] = None,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(
            type_=type_,
            description=description,
            scheme_name=scheme_name or self.__class__.__name__,
            openIdConnectUrl=openIdConnectUrl,
            **kwargs,
        )
