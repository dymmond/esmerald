from lilya.contrib.security.open_id import OpenIdConnect as LilyaOpenIdConnect
from typing_extensions import Annotated, Doc


class OpenIdConnect(LilyaOpenIdConnect):
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
            str | None,
            Doc(
                """
                The name of the security scheme.
                """
            ),
        ] = None,
        description: Annotated[
            str | None,
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
        super().__init__(
            openIdConnectUrl=openIdConnectUrl,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )
