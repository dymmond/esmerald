from typing import Any, Dict, Literal, Optional, Union

from esmerald.openapi.enums import SecuritySchemeType
from esmerald.openapi.models import OAuthFlows
from esmerald.openapi.security.base import HTTPBase


class OAuth2(HTTPBase):
    """
    The OAuth2 scheme.

    For every parameter of the OAuthFlows, expects a OAuthFlow object type.

    Example:
        implicit: Optional[OAuthFlow] = OAuthFlow()
        password: Optional[OAuthFlow] = OAuthFlow()
        clientCredentials: Optional[OAuthFlow] = OAuthFlow()
        authorizationCode: Optional[OAuthFlow] = OAuthFlow()

        flows: OAuthFlows(
            implicit=implicit,
            password=password,
            clientCredentials=clientCredentials,
            authorizationCode=authorizationCode,
        )
    """

    def __init__(
        self,
        *,
        type_: Literal[
            "apiKey", "http", "mutualTLS", "oauth2", "openIdConnect"
        ] = SecuritySchemeType.oauth2.value,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        name: Optional[str] = None,
        flows: Union[OAuthFlows, Dict[str, Dict[str, Any]]] = OAuthFlows(),
        **kwargs: Any,
    ):
        extra: Dict[Any, Any] = {}
        extra["flows"] = flows
        extra.update(kwargs)
        super().__init__(
            type_=type_,
            description=description,
            name=name,
            scheme_name=scheme_name or self.__class__.__name__,
            **extra,
        )
