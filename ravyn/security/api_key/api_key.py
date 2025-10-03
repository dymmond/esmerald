from lilya.contrib.security.api_key import (
    APIKeyInCookie as LilyaAPIKeyInCookie,
    APIKeyInHeader as LilyaAPIKeyInHeader,
    APIKeyInQuery as LilyaAPIKeyInQuery,
)
from typing_extensions import Annotated, Doc


class APIKeyInQuery(LilyaAPIKeyInQuery):
    """
    API key authentication using a query parameter.

    Defines the query parameter name for the API key and integrates it into the OpenAPI documentation.
    Extracts the key value from the query parameter and provides it as the dependency result.

    ## Usage

    Create an instance and use it as a dependency in `Inject()`.

    The dependency result will be a string containing the key value after using the `Injects()`.

    ## Example

    ```python
    from ravyn import Ravyn,  Gateway, get, Inject, Injects
    from ravyn.security.api_key import APIKeyInQuery

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
            str | None,
            Doc("Name of the security scheme, shown in OpenAPI documentation."),
        ] = None,
        description: Annotated[
            str | None,
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
        super().__init__(
            name=name, auto_error=auto_error, scheme_name=scheme_name, description=description
        )


class APIKeyInHeader(LilyaAPIKeyInHeader):
    """
    API key authentication using a header parameter.

    Defines the header parameter name for the API key and integrates it into the OpenAPI documentation.
    Extracts the key value from the header parameter and provides it as the dependency result.

    ## Usage

    Create an instance and use it as a dependency in `Inject()`.

    The dependency result will be a string containing the key value after using the `Injects()`.

    ## Example

    ```python
    from ravyn import Ravyn,  Gateway, get, Inject, Injects
    from ravyn.security.api_key import APIKeyInHeader

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
            str | None,
            Doc("The name of the security scheme to be shown in the OpenAPI documentation."),
        ] = None,
        description: Annotated[
            str | None,
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
        super().__init__(
            name=name,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )


class APIKeyInCookie(LilyaAPIKeyInCookie):
    """
    API key authentication using a cookie parameter.

    Defines the cookie parameter name for the API key and integrates it into the OpenAPI documentation.
    Extracts the key value from the cookie parameter and provides it as the dependency result.

    ## Usage

    Create an instance and use it as a dependency in `Inject()`.

    The dependency result will be a string containing the key value after using the `Injects()`.

    ## Example

    ```python
    from ravyn import Ravyn,  Gateway, get, Inject, Injects
    from ravyn.security.api_key import APIKeyInCookie

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
            str | None,
            Doc("The name of the security scheme to be shown in the OpenAPI documentation."),
        ] = None,
        description: Annotated[
            str | None,
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
        super().__init__(
            name=name,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )
