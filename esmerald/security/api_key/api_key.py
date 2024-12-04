from typing import Union, cast

from lilya.exceptions import HTTPException
from lilya.status import HTTP_403_FORBIDDEN
from pydantic import BaseModel
from typing_extensions import Annotated, Doc

from esmerald.openapi.models import APIKey, APIKeyIn
from esmerald.requests import Request
from esmerald.security.base import SecurityBase


class APIKeyBase(SecurityBase):
    __model__: Union[BaseModel, None] = None


class APIKeyInQuery(APIKeyBase):
    """
    API key authentication using a query parameter.

    Defines the query parameter name for the API key and integrates it into the OpenAPI documentation.
    Extracts the key value from the query parameter and provides it as the dependency result.

    ## Usage

    Create an instance and use it as a dependency in `Inject()`.

    The dependency result will be a string containing the key value after using the `Injects()`.

    ## Example

    ```python
    from esmerald import Esmerald,  Gateway, get, Inject, Injects
    from esmerald.security.api_key import APIKeyInQuery

    query_scheme = APIKeyInQuery(name="api_key")

    @get("/items/", dependencies={"api_key": Inject(query_scheme)})
    async def read_items(api_key: str = Injects()) -> dict[str, str]:
        return {"api_key": api_key}
    ```
    """

    def __init__(
        self,
        *,
        name: Annotated[str, Doc("Name of the query parameter.")],
        scheme_name: Annotated[
            Union[str, None],
            Doc("Name of the security scheme, shown in OpenAPI documentation."),
        ] = None,
        description: Annotated[
            Union[str, None],
            Doc("Description of the security scheme, shown in OpenAPI documentation."),
        ] = None,
        auto_error: Annotated[
            bool,
            Doc(
                "If True, raises an error if the query parameter is missing. "
                "If False, returns None when the query parameter is missing."
            ),
        ] = True,
    ):
        model: APIKey = APIKey(
            **{"in": APIKeyIn.query.value},  # type: ignore[arg-type]
            name=name,
            description=description,
        )
        super().__init__(**model.model_dump())
        self.__model__ = model
        self.scheme_name = scheme_name or self.__class__.__name__
        self.__auto_error__ = auto_error

    async def __call__(self, request: Request) -> Union[str, None]:
        api_key = request.query_params.get(self.__model__.name)
        if api_key:
            return cast(str, api_key)
        if self.__auto_error__:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")
        return None


class APIKeyInHeader(APIKeyBase):
    """
    API key authentication using a header parameter.

    Defines the header parameter name for the API key and integrates it into the OpenAPI documentation.
    Extracts the key value from the header parameter and provides it as the dependency result.

    ## Usage

    Create an instance and use it as a dependency in `Inject()`.

    The dependency result will be a string containing the key value after using the `Injects()`.

    ## Example

    ```python
    from esmerald import Esmerald,  Gateway, get, Inject, Injects
    from esmerald.security.api_key import APIKeyInHeader

    header_scheme = APIKeyInHeader(name="x-key")

    @get("/items/", dependencies={"api_key": Inject(header_scheme)})
    async def read_items(api_key: str = Injects()) -> dict[str, str]:
        return {"api_key": api_key}
    ```
    """

    def __init__(
        self,
        *,
        name: Annotated[str, Doc("The name of the header parameter.")],
        scheme_name: Annotated[
            Union[str, None],
            Doc("The name of the security scheme to be shown in the OpenAPI documentation."),
        ] = None,
        description: Annotated[
            Union[str, None],
            Doc("A description of the security scheme to be shown in the OpenAPI documentation."),
        ] = None,
        auto_error: Annotated[
            bool,
            Doc(
                "If True, an error is raised if the header is missing. "
                "If False, None is returned when the header is missing."
            ),
        ] = True,
    ):
        model: APIKey = APIKey(
            **{"in": APIKeyIn.header.value},  # type: ignore[arg-type]
            name=name,
            description=description,
        )
        super().__init__(**model.model_dump())
        self.__model__ = model
        self.scheme_name = scheme_name or self.__class__.__name__
        self.__auto_error__ = auto_error

    async def __call__(self, request: Request) -> Union[str, None]:
        api_key = request.headers.get(self.__model__.name)
        if api_key:
            return cast(str, api_key)
        if self.__auto_error__:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")
        return None


class APIKeyInCookie(APIKeyBase):
    """
    API key authentication using a cookie parameter.

    Defines the cookie parameter name for the API key and integrates it into the OpenAPI documentation.
    Extracts the key value from the cookie parameter and provides it as the dependency result.

    ## Usage

    Create an instance and use it as a dependency in `Inject()`.

    The dependency result will be a string containing the key value after using the `Injects()`.

    ## Example

    ```python
    from esmerald import Esmerald,  Gateway, get, Inject, Injects
    from esmerald.security.api_key import APIKeyInCookie

    cookie_scheme = APIKeyInCookie(name="session")

    @get("/items/", dependencies={"api_key": Inject(cookie_scheme)})
    async def read_items(api_key: str = Injects()) -> dict[str, str]:
        return {"api_key": api_key}
    ```
    """

    def __init__(
        self,
        *,
        name: Annotated[str, Doc("The name of the cookie parameter.")],
        scheme_name: Annotated[
            Union[str, None],
            Doc("The name of the security scheme to be shown in the OpenAPI documentation."),
        ] = None,
        description: Annotated[
            Union[str, None],
            Doc("A description of the security scheme to be shown in the OpenAPI documentation."),
        ] = None,
        auto_error: Annotated[
            bool,
            Doc(
                "If True, an error is raised if the cookie is missing. "
                "If False, None is returned when the cookie is missing."
            ),
        ] = True,
    ):
        model: APIKey = APIKey(
            **{"in": APIKeyIn.cookie.value},  # type: ignore[arg-type]
            name=name,
            description=description,
        )
        super().__init__(**model.model_dump())
        self.__model__ = model
        self.scheme_name = scheme_name or self.__class__.__name__
        self.__auto_error__ = auto_error

    async def __call__(self, request: Request) -> Union[str, None]:
        api_key = request.cookies.get(self.__model__.name)
        if api_key:
            return api_key
        if self.__auto_error__:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")
        return None
