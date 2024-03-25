from copy import copy
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Tuple, Union, cast

from lilya._internal._path import clean_path
from lilya.routing import compile_path
from lilya.types import Receive, Scope, Send
from typing_extensions import Annotated, Doc

if TYPE_CHECKING:  # pragma: no cover
    from openapi_schemas_pydantic.v3_1_0.security_scheme import SecurityScheme

    from esmerald.interceptors.types import Interceptor
    from esmerald.permissions.types import Permission
    from esmerald.routing.gateways import Gateway, WebSocketGateway
    from esmerald.routing.router import HTTPHandler, WebhookHandler, WebSocketHandler
    from esmerald.transformers.model import TransformerModel
    from esmerald.types import (
        Dependencies,
        ExceptionHandlerMap,
        Middleware,
        ResponseCookies,
        ResponseHeaders,
        ResponseType,
    )


class View:
    """
    `View` class object acts as the base of all the object
    oriented views used by `Esmerald`.

    The `View` contains all the available parameters that
    can be applied on a global level when subclassing it.

    **Example**

    ```python
    from esmerald.routing.views import View


    class CustomView(View):
        ...
    ```
    """

    __slots__ = (
        "dependencies",
        "exception_handlers",
        "interceptors",
        "permissions",
        "middleware",
        "parent",
        "path",
        "response_class",
        "response_cookies",
        "response_headers",
        "tags",
        "path_regex",
        "path_format",
        "param_convertors",
        "deprecated",
        "include_in_schema",
        "route_map",
        "operation_id",
        "methods",
        "interceptors",
        "security",
    )

    path: Annotated[
        str,
        Doc(
            """
            Relative path of the `Gateway`.
            The path can contain parameters in a dictionary like format.
            """
        ),
    ]
    dependencies: Annotated[
        Optional["Dependencies"],
        Doc(
            """
            A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
            """
        ),
    ]
    exception_handlers: Annotated[
        Optional["ExceptionHandlerMap"],
        Doc(
            """
            A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
            """
        ),
    ]
    permissions: Annotated[
        Optional[List["Permission"]],
        Doc(
            """
            A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
            """
        ),
    ]
    interceptors: Annotated[
        Optional[Sequence["Interceptor"]],
        Doc(
            """
            A list of [interceptors](https://esmerald.dev/interceptors/) to serve the application incoming requests (HTTP and Websockets).
            """
        ),
    ]
    middleware: Annotated[
        Optional[List["Middleware"]],
        Doc(
            """
            A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
            """
        ),
    ]
    parent: Annotated[
        Optional[Union["Gateway", "WebSocketGateway"]],
        Doc(
            """
            Used internally by Esmerald to recognise and build the [application levels](https://esmerald.dev/application/levels/).

            !!! Tip
                Unless you know what are you doing, it is advisable not to touch this.
            """
        ),
    ]
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
            Default response class to be used within the
            Esmerald application.

            Read more about the [Responses](https://esmerald.dev/responses/) and how
            to use them.

            **Example**

            ```python
            from esmerald import APIView, JSONResponse


            class MyView(APIView):
                response_class = JSONResponse
            ```
            """
        ),
    ]
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
            A sequence of `esmerald.datastructures.Cookie` objects.

            Read more about the [Cookies](https://esmerald.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

            **Example**

            ```python
            from esmerald import APIView
            from esmerald.datastructures import Cookie

            response_cookies=[
                Cookie(
                    key="csrf",
                    value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                    max_age=3000,
                    httponly=True,
                )
            ]

            class MyView(APIView):
                response_cookies = response_cookies
            ```
            """
        ),
    ]
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
            A mapping of `esmerald.datastructures.ResponseHeader` objects.

            Read more about the [ResponseHeader](https://esmerald.dev/extras/header-fields/#response-headers).

            **Example**

            ```python
            from esmerald import APIView
            from esmerald.datastructures import ResponseHeader

            response_headers={
                "authorize": ResponseHeader(value="granted")
            }

            class MyView(APIView):
                response_headers = response_headers
            ```
            """
        ),
    ]
    tags: Annotated[
        Optional[List[str]],
        Doc(
            """
            A list of strings tags to be applied to the *path operation*.

            It will be added to the generated OpenAPI documentation.

            **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means
            these tags on a Esmerald instance, means it will be added to every route even
            if those routes also contain tags.
            """
        ),
    ]
    include_in_schema: Annotated[
        Optional[bool],
        Doc(
            """
            Boolean flag indicating if it should be added to the OpenAPI docs.
            """
        ),
    ]
    security: Annotated[
        Optional[List["SecurityScheme"]],
        Doc(
            """
            Used by OpenAPI definition, the security must be compliant with the norms.
            Esmerald offers some out of the box solutions where this is implemented.

            The [Esmerald security](https://esmerald.dev/openapi/) is available to automatically used.

            The security can be applied also on a [level basis](https://esmerald.dev/application/levels/).

            For custom security objects, you **must** subclass
            `esmerald.openapi.security.base.HTTPBase` object.
            """
        ),
    ]
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
            Boolean flag for indicating the deprecation of the Include and all of its routes and to display it in the OpenAPI documentation..
            """
        ),
    ]

    def __init__(self, parent: Union["Gateway", "WebSocketGateway"]) -> None:
        for key in self.__slots__:
            if not hasattr(self, key):
                setattr(self, key, None)

        self.path = clean_path(self.path or "/")
        self.path_regex, self.path_format, self.param_convertors, _ = compile_path(self.path)
        self.parent = parent
        self.route_map: Dict[str, Tuple["HTTPHandler", "TransformerModel"]] = {}
        self.operation_id: Optional[str] = None
        self.methods: List[str] = []

    def get_filtered_handler(self) -> List[str]:
        """
        Filters out the names of the functions that are not part of the handler itself.
        """
        from esmerald.routing.router import HTTPHandler, WebhookHandler, WebSocketHandler

        filtered_handlers = [
            attr for attr in dir(self) if not attr.startswith("__") and not attr.endswith("__")
        ]
        route_handlers = []

        for handler_name in filtered_handlers:
            for base in self.__class__.__bases__:
                if handler_name not in dir(base) and isinstance(
                    getattr(self, handler_name),
                    (HTTPHandler, WebSocketHandler, WebhookHandler),
                ):
                    route_handlers.append(handler_name)
        return route_handlers

    def get_route_handlers(
        self,
    ) -> List[Union["HTTPHandler", "WebSocketHandler", "WebhookHandler"]]:
        """A getter for the apiview's route handlers that sets their parent.

        Returns:
            A list containing a copy of the route handlers defined inside the View.
        """
        from esmerald.routing.router import HTTPHandler, WebhookHandler, WebSocketHandler

        route_handlers: List[Union[HTTPHandler, WebSocketHandler, WebhookHandler]] = []
        filtered_handlers = self.get_filtered_handler()

        for handler in filtered_handlers:
            source_route_handler = cast(
                Union["HTTPHandler", "WebSocketHandler"], getattr(self, handler)
            )
            route_handler = copy(source_route_handler)
            route_handler.parent = self

            if self.include_in_schema is not None and not isinstance(
                route_handler, WebSocketHandler
            ):  # pragma: no cover
                route_handler.include_in_schema = self.include_in_schema

            if self.middleware:
                self.get_route_middleware(route_handler)

            if self.exception_handlers:
                route_handler.exception_handlers = self.get_exception_handlers(route_handler)  # type: ignore
            if self.tags or []:  # pragma: no cover
                for tag in reversed(self.tags):
                    route_handler.tags.insert(0, tag)
            route_handlers.append(route_handler)

        return route_handlers

    def get_route_middleware(
        self,
        handler: Annotated[
            Union["HTTPHandler", "WebSocketHandler", "WebhookHandler"],
            Doc(
                """
                The [handler](https://esmerald.dev/routing/handlers/) being checked against.
                """
            ),
        ],
    ) -> None:
        """
        Gets the list of extended middlewares for the handler starting from the last
        to the first by reversing the list
        """
        for middleware in reversed(self.middleware):
            handler.middleware.insert(0, middleware)

    def get_exception_handlers(
        self, handler: Union["HTTPHandler", "WebSocketHandler", "WebhookHandler"]
    ) -> "ExceptionHandlerMap":
        """
        Gets the dict of extended exception handlers for the handler starting from the last
        to the first by reversing the list
        """
        exception_handlers = {**self.exception_handlers, **handler.exception_handlers}
        return cast("ExceptionHandlerMap", exception_handlers)

    async def handle(
        self, scope: "Scope", receive: "Receive", send: "Send"
    ) -> None:  # pragma: no cover
        raise NotImplementedError(f"{self.__class__.__name__} object does not implement handle()")

    def create_signature_model(self, is_websocket: bool = False) -> None:  # pragma: no cover
        raise NotImplementedError(
            f"{self.__class__.__name__} object does not implement create_signature_model()"
        )
