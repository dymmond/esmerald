from typing import List, Optional

from pydantic import BaseModel
from typing_extensions import Annotated, Doc


class CORSConfig(BaseModel):
    """
    An instance of [CORSConfig](https://esmerald.dev/configurations/cors/).

    This configuration is passed to the [CORSMiddleware](https://esmerald.dev/middleware/middleware/#corsmiddleware) and enables the middleware.

    **Example**

    ```python
    from esmerald import Esmerald
    from esmerald.config import CSRFConfig

    cors_config = CORSConfig(allow_origins=["*"])

    app = Esmerald(cors_config=cors_config)
    ```
    """

    allow_origins: Annotated[
        List[str],
        Doc(
            """
            A list of origins that are allowed.

            It is possible to allow all by passing '*' and also
            wildcards are are allowed.

            Example: `example.*` or `*.example.com`.

            This option sets the 'Access-Control-Allow-Origin' header.
            """
        ),
    ] = ["*"]
    allow_methods: Annotated[
        List[str],
        Doc(
            """
            List of allowed HTTP verbs/methods.

            This option sets the 'Access-Control-Allow-Methods' header.
            """
        ),
    ] = ["*"]
    allow_headers: Annotated[
        List[str],
        Doc(
            """
            List of allowed headers.

            This option sets the 'Access-Control-Allow-Headers' header.
            """
        ),
    ] = ["*"]
    allow_credentials: Annotated[
        bool,
        Doc(
            """
            Boolean flag indicating whether or not to set the 'Access-Control-Allow-Credentials' header.
            """
        ),
    ] = False
    allow_origin_regex: Annotated[
        Optional[str],
        Doc(
            """
            Regular expressio to match the origins against.
            """
        ),
    ] = None
    expose_headers: Annotated[
        List[str],
        Doc(
            """
            List of headers that are exposed.

            This option sets the 'Access-Control-Expose-Headers' header.
            """
        ),
    ] = []
    max_age: Annotated[
        int,
        Doc(
            """
            Response TTL caching in seconds.

            This option sets the 'Access-Control-Max-Age' header.
            """
        ),
    ] = 600
    allow_private_networks: Annotated[
        bool,
        Doc(
            """
            Flag indicating that CORS allows private networks.

            This option sets the 'Access-Control-Request-Private-Network' header.
            """
        ),
    ] = False
