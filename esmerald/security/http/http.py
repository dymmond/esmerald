import binascii
from base64 import b64decode
from typing import Any, Optional, Union

from lilya.requests import Request
from lilya.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from pydantic import BaseModel
from typing_extensions import Annotated, Doc

from esmerald.exceptions import HTTPException
from esmerald.openapi.models import HTTPBase as HTTPBaseModel, HTTPBearer as HTTPBearerModel
from esmerald.security.base import HttpSecurityBase
from esmerald.security.utils import get_authorization_scheme_param


class HTTPBasicCredentials(BaseModel):
    """
    Represents HTTP Basic credentials.

    Attributes:
        username (str): The username.
        password (str): The password.
    """

    username: Annotated[str, Doc("The username for HTTP Basic authentication.")]
    password: Annotated[str, Doc("The password for HTTP Basic authentication.")]


class HTTPAuthorizationCredentials(BaseModel):
    """
    Represents HTTP authorization credentials.

    Attributes:
        scheme (str): The authorization scheme (e.g., "Bearer").
        credentials (str): The authorization credentials (e.g., token).
    """

    scheme: Annotated[str, Doc("The authorization scheme extracted from the header.")]
    credentials: Annotated[str, Doc("The authorization credentials extracted from the header.")]


class HTTPBase(HttpSecurityBase):
    def __init__(
        self,
        *,
        scheme: str,
        scheme_name: Union[str, None] = None,
        description: Union[str, None] = None,
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
        model = HTTPBaseModel(scheme=scheme, description=description)
        model_dump = {**model.model_dump(), **kwargs}
        super().__init__(**model_dump)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.__auto_error__ = auto_error

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        authorization = request.headers.get("Authorization")
        if not authorization:
            if self.__auto_error__:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")
            return None

        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (scheme and credentials):
            if self.__auto_error__:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Invalid authentication credentials"
                )
            return None

        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


class HTTPBasic(HTTPBase):
    """
    HTTP Basic authentication.

    Use this class as a dependency to enforce HTTP Basic authentication.

    ## Example:

    ```python
    from typing import Any

    from esmerald import Gateway, Inject, Injects, get
    from esmerald.security.http import HTTPBasic, HTTPBasicCredentials
    from esmerald.testclient import create_client

    security = HTTPBasic()

    @app.get("/users/me", security=[security], dependencies={"credentials": Inject(security)}))
    def get_current_user(credentials: HTTPBasicCredentials = Injects()):
        return {"username": credentials.username, "password": credentials.password}
    ```
    """

    def __init__(
        self,
        *,
        scheme_name: Annotated[Union[str, None], Doc("The name of the security scheme.")] = None,
        realm: Annotated[Union[str, None], Doc("The HTTP Basic authentication realm.")] = None,
        description: Annotated[
            Union[str, None], Doc("Description of the security scheme.")
        ] = None,
        auto_error: Annotated[
            bool,
            Doc(
                "Whether to automatically raise an error if authentication fails. "
                "If set to False, the dependency result will be None when authentication is not provided."
            ),
        ] = True,
    ):
        model = HTTPBaseModel(scheme="basic", description=description)
        super().__init__(**model.model_dump())
        self.scheme_name = scheme_name or self.__class__.__name__
        self.realm = realm
        self.__auto_error__ = auto_error

    async def __call__(self, request: Request) -> Optional[HTTPBasicCredentials]:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        unauthorized_headers = {
            "WWW-Authenticate": f'Basic realm="{self.realm}"' if self.realm else "Basic"
        }

        if not authorization or scheme.lower() != "basic":
            if self.__auto_error__:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers=unauthorized_headers,
                )
            return None

        try:
            data = b64decode(param).decode("ascii")
            username, separator, password = data.partition(":")
            if not separator:
                raise ValueError("Invalid credentials format")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers=unauthorized_headers,
            ) from None

        return HTTPBasicCredentials(username=username, password=password)


class HTTPBearer(HTTPBase):
    """
    HTTP Bearer token authentication.

    Use this class as a dependency to enforce HTTP Bearer token authentication.

    ## Example

    ```python
    from typing import Any

    from esmerald import Inject, Injects, get
    from esmerald.security.http import HTTPAuthorizationCredentials, HTTPBearer

    security = HTTPBearer()

    @app.get("/users/me")
    def get_current_user(credentials: HTTPAuthorizationCredentials = Injects()) -> Any::
        return {"scheme": credentials.scheme, "credentials": credentials.credentials}
    ```
    """

    def __init__(
        self,
        *,
        bearerFormat: Annotated[Union[str, None], Doc("The format of the Bearer token.")] = None,
        scheme_name: Annotated[Union[str, None], Doc("The name of the security scheme.")] = None,
        description: Annotated[
            Union[str, None], Doc("Description of the security scheme.")
        ] = None,
        auto_error: Annotated[
            bool,
            Doc(
                "Whether to automatically raise an error if authentication fails. "
                "If set to False, the dependency result will be None when authentication is not provided."
            ),
        ] = True,
    ):
        model = HTTPBearerModel(bearerFormat=bearerFormat, description=description)
        super().__init__(**model.model_dump())
        self.scheme_name = scheme_name or self.__class__.__name__
        self.__auto_error__ = auto_error

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        authorization = request.headers.get("Authorization")
        if not authorization:
            if self.__auto_error__:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")
            return None

        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (scheme and credentials) or scheme.lower() != "bearer":
            if self.__auto_error__:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN,
                    detail="Invalid authentication credentials",
                )
            return None

        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


class HTTPDigest(HTTPBase):
    """
    HTTP Digest authentication.

    Use this class as a dependency to enforce HTTP Digest authentication.

    ## Example:

    ```python
    from typing import Any

    from esmerald import Inject, Injects, get
    from esmerald.security.http import HTTPAuthorizationCredentials, HTTPDigest

    security = HTTPDigest()

    @get("/users/me", security=[security], dependencies={"credentials": Inject(security)})
    def get_current_user(credentials: HTTPAuthorizationCredentials = Injects()) -> Any:
        return {"scheme": credentials.scheme, "credentials": credentials.credentials}
    ```
    """

    def __init__(
        self,
        *,
        scheme_name: Annotated[Union[str, None], Doc("The name of the security scheme.")] = None,
        description: Annotated[
            Union[str, None], Doc("Description of the security scheme.")
        ] = None,
        auto_error: Annotated[
            bool,
            Doc(
                "Whether to automatically raise an error if authentication fails. "
                "If set to False, the dependency result will be None when authentication is not provided."
            ),
        ] = True,
    ):
        model = HTTPBaseModel(scheme="digest", description=description)
        super().__init__(**model.model_dump())
        self.scheme_name = scheme_name or self.__class__.__name__
        self.__auto_error__ = auto_error

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            if self.__auto_error__:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")
            else:
                return None
        if scheme.lower() != "digest":
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Invalid authentication credentials",
            )
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)
