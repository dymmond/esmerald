from typing import Any

from lilya.contrib.security.http import (
    HTTPAuthorizationCredentials as HTTPAuthorizationCredentials,  # noqa
    HTTPBase as LilyaHTTPBase,
    HTTPBasic as LilyaHTTPBasic,
    HTTPBasicCredentials as HTTPBasicCredentials,  # noqa
    HTTPBearer as LilyaHTTPBearer,
    HTTPDigest as LilyaHTTPDigest,
)
from typing_extensions import Annotated, Doc


class HTTPBase(LilyaHTTPBase):
    def __init__(
        self,
        *,
        scheme: str,
        scheme_name: str | None = None,
        description: str | None = None,
        auto_error: bool = True,
        **kwargs: Any,
    ):
        """
        Base class for HTTP security schemes.

        Args:
            scheme (str): The security scheme (e.g., "basic", "bearer").
            scheme_name (str, optional): The name of the security scheme.
            description (str, optional): Description of the security scheme.
            auto_error (bool, optional): Whether to automatically raise an error if authentication fails.
        """
        super().__init__(
            scheme=scheme,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
            **kwargs,
        )


class HTTPBasic(LilyaHTTPBasic):
    """
    HTTP Basic authentication.

    Use this class as a dependency to enforce HTTP Basic authentication.

    ## Example:

    ```python
    from typing import Any

    from ravyn import Gateway, Inject, Injects, get
    from ravyn.security.http import HTTPBasic, HTTPBasicCredentials
    from ravyn.testclient import create_client

    security = HTTPBasic()

    @app.get("/users/me", security=[security], dependencies={"credentials": Inject(security)}))
    def get_current_user(credentials: HTTPBasicCredentials = Injects()):
        return {"username": credentials.username, "password": credentials.password}
    ```
    """

    def __init__(
        self,
        *,
        scheme_name: Annotated[str | None, Doc("The name of the security scheme.")] = None,
        realm: Annotated[str | None, Doc("The HTTP Basic authentication realm.")] = None,
        description: Annotated[str | None, Doc("Description of the security scheme.")] = None,
        auto_error: Annotated[
            bool,
            Doc(
                "Whether to automatically raise an error if authentication fails. "
                "If set to False, the dependency result will be None when authentication is not provided."
            ),
        ] = True,
    ):
        super().__init__(
            scheme_name=scheme_name, realm=realm, description=description, auto_error=auto_error
        )


class HTTPBearer(LilyaHTTPBearer):
    """
    HTTP Bearer token authentication.

    Use this class as a dependency to enforce HTTP Bearer token authentication.

    ## Example

    ```python
    from typing import Any

    from ravyn import Inject, Injects, get
    from ravyn.security.http import HTTPAuthorizationCredentials, HTTPBearer

    security = HTTPBearer()

    @app.get("/users/me")
    def get_current_user(credentials: HTTPAuthorizationCredentials = Injects()) -> Any::
        return {"scheme": credentials.scheme, "credentials": credentials.credentials}
    ```
    """

    def __init__(
        self,
        *,
        bearerFormat: Annotated[str | None, Doc("The format of the Bearer token.")] = None,
        scheme_name: Annotated[str | None, Doc("The name of the security scheme.")] = None,
        description: Annotated[str | None, Doc("Description of the security scheme.")] = None,
        auto_error: Annotated[
            bool,
            Doc(
                "Whether to automatically raise an error if authentication fails. "
                "If set to False, the dependency result will be None when authentication is not provided."
            ),
        ] = True,
    ):
        super().__init__(
            bearerFormat=bearerFormat,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )


class HTTPDigest(LilyaHTTPDigest):
    """
    HTTP Digest authentication.

    Use this class as a dependency to enforce HTTP Digest authentication.

    ## Example:

    ```python
    from typing import Any

    from ravyn import Inject, Injects, get
    from ravyn.security.http import HTTPAuthorizationCredentials, HTTPDigest

    security = HTTPDigest()

    @get("/users/me", security=[security], dependencies={"credentials": Inject(security)})
    def get_current_user(credentials: HTTPAuthorizationCredentials = Injects()) -> Any:
        return {"scheme": credentials.scheme, "credentials": credentials.credentials}
    ```
    """

    def __init__(
        self,
        *,
        scheme_name: Annotated[str | None, Doc("The name of the security scheme.")] = None,
        description: Annotated[str | None, Doc("Description of the security scheme.")] = None,
        auto_error: Annotated[
            bool,
            Doc(
                "Whether to automatically raise an error if authentication fails. "
                "If set to False, the dependency result will be None when authentication is not provided."
            ),
        ] = True,
    ):
        super().__init__(scheme_name=scheme_name, description=description, auto_error=auto_error)
