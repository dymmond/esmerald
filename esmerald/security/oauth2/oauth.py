from typing import Any, Dict, List, Optional, Union, cast

from lilya.requests import Request
from lilya.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from pydantic import BaseModel, field_validator
from typing_extensions import Annotated, Doc

from esmerald.exceptions import HTTPException
from esmerald.openapi.models import (
    OAuth2 as OAuth2Model,
    OAuthFlows as OAuthFlowsModel,
)
from esmerald.param_functions import Form
from esmerald.security.base import SecurityBase as SecurityBase
from esmerald.security.utils import get_authorization_scheme_param


class OAuth2PasswordRequestForm(BaseModel):
    """
    This is a dependency class to collect the `username` and `password` as form data
    for an OAuth2 password flow.

    The OAuth2 specification dictates that for a password flow the data should be
    collected using form data (instead of JSON) and that it should have the specific
    fields `username` and `password`.

    All the initialization parameters are extracted from the request.

    Read more about it in the
    [Esmerald docs for Simple OAuth2 with Password and Bearer](https://esmerald.dev/tutorial/security/simple-oauth2/).

    ## Example

    ```python
    from typing import Annotated

    from esmerald import Esmerald, Gateway, Inject, Injects, post
    from esmerald.security.oauth2 import OAuth2PasswordRequestForm


    @post("/login", dependencies={"form_data": Inject(OAuth2PasswordRequestForm)})
    def login(form_data: Annotated[OAuth2PasswordRequestForm, Injects()]) -> dict:
        data = {}
        data["scopes"] = []
        for scope in form_data.scopes:
            data["scopes"].append(scope)
        if form_data.client_id:
            data["client_id"] = form_data.client_id
        if form_data.client_secret:
            data["client_secret"] = form_data.client_secret
        return data


    app = Esmerald(
        routes=[
            Gateway(handler=login),
        ]
    )
    ```

    Note that for OAuth2 the scope `items:read` is a single scope in an opaque string.
    You could have custom internal logic to separate it by colon characters (`:`) or
    similar, and get the two parts `items` and `read`. Many applications do that to
    group and organize permissions, you could do it as well in your application, just
    know that that it is application specific, it's not part of the specification.
    """

    model_config = {"extra": "allow"}

    grant_type: Annotated[
        Union[str, None],
        Form(pattern="^password$"),
        Doc(
            """
            Specifies the OAuth2 grant type.

            Per the OAuth2 specification, this value is required and must be set
            to the fixed string "password" when using the password grant flow.
            However, this class allows flexibility and does not enforce this
            restriction. To enforce the "password" value strictly, consider using
            the `OAuth2PasswordRequestFormStrict` dependency.
            """
        ),
    ] = None
    username: Annotated[
        str,
        Form(),
        Doc(
            """
            The username of the user for OAuth2 authentication.

            According to the OAuth2 specification, this field must be named
            `username`, as it is used to identify the user during the
            authentication process.
            """
        ),
    ]
    password: Annotated[
        str,
        Form(),
        Doc(
            """
            The password of the user for OAuth2 authentication.

            Per the OAuth2 spec, this field must also use the name `password`.
            It is required for authentication to validate the provided username.
            """
        ),
    ]
    scope: Annotated[
        Union[str, List[str]],
        Form(),
        Doc(
            """
            A single string containing one or more scopes, space-separated.

            Each scope represents a permission requested by the application.
            Scopes help specify fine-grained access control, enabling the client
            to request only the permissions it needs. For example, the following
            string:

            ```python
            "items:read items:write users:read profile openid"
            ```

            represents multiple scopes:

            * `items:read`
            * `items:write`
            * `users:read`
            * `profile`
            * `openid`
            """
        ),
    ] = []
    client_id: Annotated[
        Union[str, None],
        Form(),
        Doc(
            """
            Optional client identifier used to identify the client application.

            If provided, `client_id` can be sent as part of the form data.
            Although the OAuth2 specification recommends sending both `client_id`
            and `client_secret` via HTTP Basic authentication headers, some APIs
            accept these values in the form fields for flexibility.
            """
        ),
    ] = None
    client_secret: Annotated[
        Union[str, None],
        Form(),
        Doc(
            """
            Optional client secret for authenticating the client application.

            If a `client_secret` is required (along with `client_id`), it can be
            included in the form data. However, the OAuth2 spec advises sending
            both `client_id` and `client_secret` using HTTP Basic authentication
            headers for security.
            """
        ),
    ] = None

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.scopes = self.scope

    @field_validator("scope", mode="before")
    @classmethod
    def validate_scope(cls, value: Union[str, List[str]]) -> Any:
        if isinstance(value, str) and len(value) == 0:
            return []
        if isinstance(value, str):
            return value.split(" ")
        return value

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Making sure the "scope" is not included in the model dump
        as the scopes should be the one being used by Esmerald.
        """
        if kwargs is None:
            kwargs = {}
        kwargs["exclude"] = {"scope"}
        return super().model_dump(**kwargs)


class OAuth2PasswordRequestFormStrict(OAuth2PasswordRequestForm):
    """
    This is a dependency class to collect the `username` and `password` as form data
    for an OAuth2 password flow.

    The OAuth2 specification dictates that for a password flow the data should be
    collected using form data (instead of JSON) and that it should have the specific
    fields `username` and `password`.

    All the initialization parameters are extracted from the request.

    The only difference between `OAuth2PasswordRequestFormStrict` and
    `OAuth2PasswordRequestForm` is that `OAuth2PasswordRequestFormStrict` requires the
    client to send the form field `grant_type` with the value `"password"`, which
    is required in the OAuth2 specification (it seems that for no particular reason),
    while for `OAuth2PasswordRequestForm` `grant_type` is optional.

    ## Example

    ```python
    from typing import Annotated

    from esmerald import Esmerald, Gateway, Inject, Injects, post
    from esmerald.security.oauth2 import OAuth2PasswordRequestForm


    @post("/login", dependencies={"form_data": Inject(OAuth2PasswordRequestForm)})
    def login(form_data: Annotated[OAuth2PasswordRequestForm, Injects()]) -> dict:
        data = {}
        data["scopes"] = []
        for scope in form_data.scopes:
            data["scopes"].append(scope)
        if form_data.client_id:
            data["client_id"] = form_data.client_id
        if form_data.client_secret:
            data["client_secret"] = form_data.client_secret
        return data


    app = Esmerald(
        routes=[
            Gateway(handler=login),
        ]
    )
    ```

    Note that for OAuth2 the scope `items:read` is a single scope in an opaque string.
    You could have custom internal logic to separate it by colon caracters (`:`) or
    similar, and get the two parts `items` and `read`. Many applications do that to
    group and organize permissions, you could do it as well in your application, just
    know that that it is application specific, it's not part of the specification.


    grant_type: the OAuth2 spec says it is required and MUST be the fixed string "password".
        This dependency is strict about it. If you want to be permissive, use instead the
        OAuth2PasswordRequestForm dependency class.
    username: username string. The OAuth2 spec requires the exact field name "username".
    password: password string. The OAuth2 spec requires the exact field name "password".
    scope: Optional string. Several scopes (each one a string) separated by spaces. E.g.
        "items:read items:write users:read profile openid"
    client_id: optional string. OAuth2 recommends sending the client_id and client_secret (if any)
        using HTTP Basic auth, as: client_id:client_secret
    client_secret: optional string. OAuth2 recommends sending the client_id and client_secret (if any)
        using HTTP Basic auth, as: client_id:client_secret
    """

    def __init__(
        self,
        grant_type: Annotated[
            str,
            Form(pattern="^password$"),
            Doc(
                """
                The OAuth2 spec says it is required and MUST be the fixed string
                "password". This dependency is strict about it. If you want to be
                permissive, use instead the `OAuth2PasswordRequestForm` dependency
                class.
                """
            ),
        ],
        username: Annotated[
            str,
            Form(),
            Doc(
                """
                `username` string. The OAuth2 spec requires the exact field name
                `username`.
                """
            ),
        ],
        password: Annotated[
            str,
            Form(),
            Doc(
                """
                `password` string. The OAuth2 spec requires the exact field name
                `password".
                """
            ),
        ],
        scope: Annotated[
            str,
            Form(),
            Doc(
                """
                A single string with actually several scopes separated by spaces. Each
                scope is also a string.

                For example, a single string with:

                ```python
                "items:read items:write users:read profile openid"
                ````

                would represent the scopes:

                * `items:read`
                * `items:write`
                * `users:read`
                * `profile`
                * `openid`
                """
            ),
        ] = "",
        client_id: Annotated[
            Union[str, None],
            Form(),
            Doc(
                """
                If there's a `client_id`, it can be sent as part of the form fields.
                But the OAuth2 specification recommends sending the `client_id` and
                `client_secret` (if any) using HTTP Basic auth.
                """
            ),
        ] = None,
        client_secret: Annotated[
            Union[str, None],
            Form(),
            Doc(
                """
                If there's a `client_password` (and a `client_id`), they can be sent
                as part of the form fields. But the OAuth2 specification recommends
                sending the `client_id` and `client_secret` (if any) using HTTP Basic
                auth.
                """
            ),
        ] = None,
    ) -> None:
        super().__init__(
            grant_type=grant_type,
            username=username,
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
        )


class OAuth2(SecurityBase):
    """
    This is the base class for OAuth2 authentication, an instance of it would be used
    as a dependency. All other OAuth2 classes inherit from it and customize it for
    each OAuth2 flow.

    You normally would not create a new class inheriting from it but use one of the
    existing subclasses, and maybe compose them if you want to support multiple flows.
    """

    def __init__(
        self,
        *,
        flows: Annotated[
            Union[OAuthFlowsModel, Dict[str, Dict[str, Any]]],
            Doc(
                """
                The dictionary containing the OAuth2 flows.
                """
            ),
        ] = OAuthFlowsModel(),
        scheme_name: Annotated[
            Optional[str],
            Doc(
                """
                The name of the Security scheme.

                It will be in the OpenAPI documentation.
                """
            ),
        ] = None,
        description: Annotated[
            Optional[str],
            Doc(
                """
                Security scheme description.

                It will be in the OpenAPI documentation.
                """
            ),
        ] = None,
        auto_error: Annotated[
            bool,
            Doc(
                """
                By default, if no HTTP Authorization header is provided, which is required for
                OAuth2 authentication, the request will automatically be canceled and
                an error will be sent to the client.

                If `auto_error` is set to `False`, when the HTTP Authorization header
                is not available, instead of erroring out, the dependency result will
                be `None`.

                This is useful when you want to have optional authentication.

                It is also useful when you want to have authentication that can be
                provided in one of multiple optional ways (for example, with OAuth2
                or in a cookie).
                """
            ),
        ] = True,
    ) -> None:
        model = OAuth2Model(
            flows=cast(OAuthFlowsModel, flows), scheme=scheme_name, description=description
        )
        super().__init__(**model.model_dump())
        self.scheme_name = scheme_name or self.__class__.__name__
        self.__auto_error__ = auto_error

    async def __call__(self, request: Request) -> Any:
        authorization = request.headers.get("Authorization")

        if authorization:
            return authorization

        if self.__auto_error__:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")

        return None


class OAuth2PasswordBearer(OAuth2):
    """
    This class is typically used as a dependency in path operations.

    Args:
        tokenUrl (str): The URL to obtain the OAuth2 token. This should be the path
                        operation that has `OAuth2PasswordRequestForm` as a dependency.
        scheme_name (Optional[str], optional): The security scheme name. This will appear
                                               in the OpenAPI documentation. Defaults to None.
        scopes (Optional[Dict[str, str]], optional): The OAuth2 scopes required by the
                                                     path operations using this dependency.
                                                     Defaults to None.
        description (Optional[str], optional): The security scheme description. This will
                                               appear in the OpenAPI documentation. Defaults to None.
        auto_error (bool, optional): If set to True (default), the request will automatically
                                     be canceled and an error sent to the client if no HTTP
                                     Authorization header is provided. If set to False, the
                                     dependency result will be None when the HTTP Authorization
                                     header is not available, allowing for optional authentication.

    Methods:
        __call__(request: Request) -> Optional[str]: Extracts and returns the bearer token
                                                     from the request's Authorization header.
                                                     Raises an HTTP 401 error if authentication
                                                     fails and `auto_error` is True.

    OAuth2 flow for authentication using a bearer token obtained with a password.
    An instance of it would be used as a dependency.
    """

    def __init__(
        self,
        tokenUrl: Annotated[
            str,
            Doc(
                """
                The endpoint URL used to obtain the OAuth2 token.

                This URL should point to the *path operation* that includes
                `OAuth2PasswordRequestForm` as a dependency, facilitating user
                authentication and token retrieval within the OAuth2 framework.
                """
            ),
        ],
        scheme_name: Annotated[
            Optional[str],
            Doc(
                """
                The name of the security scheme.

                This value will be displayed in the OpenAPI documentation,
                identifying the OAuth2 security scheme associated with this
                configuration.
                """
            ),
        ] = None,
        scopes: Annotated[
            Optional[Dict[str, str]],
            Doc(
                """
                A dictionary of OAuth2 scopes associated with this configuration.

                Scopes define specific permissions that the *path operations* require,
                enabling fine-grained access control. The dictionary should use
                scope names as keys and their descriptions as values, aiding in
                understanding each scope's purpose.
                """
            ),
        ] = None,
        description: Annotated[
            Optional[str],
            Doc(
                """
                A description of the security scheme.

                This description will be included in the OpenAPI documentation,
                providing users with an overview of the OAuth2 security scheme's
                purpose and any additional information relevant to this configuration.
                """
            ),
        ] = None,
        auto_error: Annotated[
            bool,
            Doc(
                """
                Flag to control automatic error response when authorization fails.

                If `True` (default), the application will automatically cancel the
                request and return an error response if the HTTP Authorization header
                is missing or invalid. Setting `auto_error` to `False` allows the
                request to proceed without authentication, returning `None` for the
                dependency result, which is useful in cases where authentication
                should be optional or supported through multiple methods (e.g.,
                OAuth2 or cookies).
                """
            ),
        ] = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password=cast(Any, {"tokenUrl": tokenUrl, "scopes": scopes}))
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if authorization and scheme.lower() == "bearer":
            return param

        if self.__auto_error__:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return None


class OAuth2AuthorizationCodeBearer(OAuth2):
    """
    Implements the OAuth2 authorization code flow for obtaining a bearer token.

    This class is used to handle authentication by exchanging an authorization
    code for an access token. An instance of `OAuth2AuthorizationCodeBearer` can
    be used as a dependency to secure endpoint access, ensuring users are
    authenticated via an OAuth2 authorization code flow.
    """

    def __init__(
        self,
        authorizationUrl: str,
        tokenUrl: Annotated[
            str,
            Doc(
                """
                The URL endpoint to exchange the authorization code for an OAuth2 access token.

                This URL should point to the token endpoint in the OAuth2 provider's
                API, enabling users to obtain a bearer token after the authorization
                code is provided.
                """
            ),
        ],
        refreshUrl: Annotated[
            Optional[str],
            Doc(
                """
                Optional URL endpoint for refreshing the OAuth2 access token.

                When provided, this URL allows users to renew an expired access token
                without re-authenticating, improving usability and security. This
                endpoint is part of the OAuth2 provider's API.
                """
            ),
        ] = None,
        scheme_name: Annotated[
            Optional[str],
            Doc(
                """
                The name of the OAuth2 security scheme.

                This name will be displayed in the OpenAPI documentation, identifying
                the authorization method used for API access.
                """
            ),
        ] = None,
        scopes: Annotated[
            Optional[Dict[str, str]],
            Doc(
                """
                Dictionary of OAuth2 scopes required for API access.

                Scopes represent permissions requested by the application for specific
                actions or data access. Each scope is represented by a key-value pair
                where the key is the scope identifier, and the value is a brief
                description of the scope's purpose.
                """
            ),
        ] = None,
        description: Annotated[
            Optional[str],
            Doc(
                """
                Description of the OAuth2 security scheme for documentation purposes.

                This text will appear in the OpenAPI documentation, providing context
                on the authentication method used by this scheme and any relevant
                details.
                """
            ),
        ] = None,
        auto_error: Annotated[
            bool,
            Doc(
                """
                Determines if the request should automatically error on authentication failure.

                If set to `True` (default), requests without a valid Authorization
                header will automatically return an error response. If `False`, the
                request can continue without authentication, returning `None` as the
                dependency result. This option is useful for optional authentication
                or for scenarios where multiple authentication methods are permitted
                (e.g., OAuth2 or session-based tokens).
                """
            ),
        ] = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            authorizationCode=cast(
                Any,
                {
                    "authorizationUrl": authorizationUrl,
                    "tokenUrl": tokenUrl,
                    "refreshUrl": refreshUrl,
                    "scopes": scopes,
                },
            )
        )
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        authorization = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)

        if authorization and scheme.lower() == "bearer":
            return param

        if self.__auto_error__:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return None
