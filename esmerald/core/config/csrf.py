from typing import Optional, Set

from pydantic import BaseModel
from typing_extensions import Annotated, Doc, Literal

from esmerald.types import HTTPMethod


class CSRFConfig(BaseModel):
    """
    An instance of [CRSFConfig](https://esmerald.dev/configurations/csrf/).

    This configuration is passed to the [CSRFMiddleware](https://esmerald.dev/middleware/middleware/#csrfmiddleware) and enables the middleware.

    !!! Tip
        You can creatye your own `CRSFMiddleware` version and pass your own
        configurations. You don't need to use the built-in version although it
        is recommended to do it so.

    **Example**

    ```python
    from esmerald import Esmerald
    from esmerald.config import CSRFConfig

    csrf_config = CSRFConfig(secret="your-long-unique-secret")

    app = Esmerald(csrf_config=csrf_config)
    ```
    """

    secret: Annotated[
        str,
        Doc(
            """
            The string used for the encryption/decryption and used to create an HMAC to sign
            the CSRF token.

            !!! Tip
                It is advised to use the same secret as the one in the settings to make it consistent.
            """
        ),
    ]
    cookie_name: Annotated[
        str,
        Doc(
            """
            The name of the CSRF cookie.
            """
        ),
    ] = "csrftoken"
    cookie_path: Annotated[
        str,
        Doc(
            """
            Name path of the CSRF cookie.
            """
        ),
    ] = "/"
    header_name: Annotated[
        str,
        Doc(
            """
            The header expected that will be expected in each request.
            """
        ),
    ] = "X-CSRFToken"
    secure: Annotated[
        bool,
        Doc(
            """
            Boolean flag when enabled sets `Secure` on the cookie.
            """
        ),
    ] = False
    httponly: Annotated[
        bool,
        Doc(
            """
            Boolean flag when enabled sets the cookie to be `httpsOnly`.
            """
        ),
    ] = False
    samesite: Annotated[
        Literal["lax", "strict", "none"],
        Doc(
            """
            The value to set in the `SameSite` attribute of the cookie.
            """
        ),
    ] = "lax"
    domain: Annotated[
        Optional[str],
        Doc(
            """
            Specifies which hosts can receive the cookie.
            """
        ),
    ] = None
    safe_methods: Annotated[
        Set[HTTPMethod],
        Doc(
            """
            A set of allowed safe methods that can set the cookie.
            """
        ),
    ] = {"GET", "HEAD"}
