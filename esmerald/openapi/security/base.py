from typing import Any, Literal, Optional, Union

from pydantic import AnyUrl, ConfigDict

from esmerald.openapi.models import SecurityScheme


class HTTPBase(SecurityScheme):
    """
    Base for all HTTP security headers.
    """

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def __init__(
        self,
        *,
        type_: Optional[Literal["apiKey", "http", "mutualTLS", "oauth2", "openIdConnect"]] = None,
        bearerFormat: Optional[str] = None,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        in_: Optional[Literal["query", "header", "cookie"]] = None,
        name: Optional[str] = None,
        scheme: Optional[str] = None,
        openIdConnectUrl: Optional[Union[AnyUrl, str]] = None,
        **kwargs: Any,
    ):
        super().__init__(  # type: ignore
            type=type_,
            bearerFormat=bearerFormat,
            description=description,
            name=name,
            security_scheme_in=in_,
            scheme_name=scheme_name,
            scheme=scheme,
            openIdConnectUrl=openIdConnectUrl,
            **kwargs,
        )
