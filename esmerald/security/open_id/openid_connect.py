from typing import Any, Optional

from lilya.exceptions import HTTPException
from lilya.requests import Request
from lilya.status import HTTP_403_FORBIDDEN
from typing_extensions import Annotated, Doc

from esmerald.openapi.models import OpenIdConnect as OpenIdConnectModel
from esmerald.security.base import SecurityBase as SecurityBase


class OpenIdConnect(SecurityBase):
    def __init__(
        self,
        *,
        openIdConnectUrl: Annotated[
            str,
            Doc(
                """
                The OpenID Connect URL.
                """
            ),
        ],
        scheme_name: Annotated[
            Optional[str],
            Doc(
                """
                The name of the security scheme.
                """
            ),
        ] = None,
        description: Annotated[
            Optional[str],
            Doc(
                """
                A description of the security scheme.
                """
            ),
        ] = None,
        auto_error: Annotated[
            bool,
            Doc(
                """
                Determines the behavior when the HTTP Authorization header is missing.

                If set to `True` (default), the request will be automatically canceled and an error will be sent to the client if the header is not provided.

                If set to `False`, the dependency result will be `None` when the header is not available, allowing for optional authentication or multiple authentication methods (e.g., OpenID Connect or a cookie).
                """
            ),
        ] = True,
    ):
        model = OpenIdConnectModel(
            openIdConnectUrl=openIdConnectUrl, description=description, scheme=scheme_name
        )
        model_dump = model.model_dump()
        super().__init__(**model_dump)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.__auto_error__ = auto_error

    async def __call__(self, request: Request) -> Any:
        authorization = request.headers.get("Authorization")

        if authorization:
            return authorization

        if self.__auto_error__:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")

        return None
