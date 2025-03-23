from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Sequence, TypedDict, Union, Unpack

from lilya._internal._path import clean_path  # noqa
from lilya.compat import is_async_callable
from typing_extensions import Annotated, Doc

from esmerald import Controller
from esmerald.core.events.base import EventDispatcher

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.interceptors.types import Interceptor
    from esmerald.openapi.schemas.v3_1_0.security_scheme import SecurityScheme
    from esmerald.permissions.types import Permission
    from esmerald.types import (
        Dependencies,
        ExceptionHandlerMap,
        Middleware,
        ResponseCookies,
        ResponseHeaders,
        ResponseType,
    )


class ControllerOptions(TypedDict, total=False):
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
    before_request: Annotated[
        Union[Sequence[Callable[[], Any]], None],
        Doc(
            """
            A `list` of events that are trigger after the application
            processes the request.

            Read more about the [events](https://lilya.dev/lifespan/).

            **Example**

            ```python
            from edgy import Database, Registry

            from esmerald import Esmerald, Request, Gateway, get

            database = Database("postgresql+asyncpg://user:password@host:port/database")
            registry = Registry(database=database)

            async def create_user(request: Request):
                # Logic to create the user
                data = await request.json()
                ...


            app = Esmerald(
                routes=[Gateway("/create", handler=create_user)],
                after_request=[database.disconnect],
            )
            ```
            """
        ),
    ]
    after_request: Annotated[
        Union[Sequence[Callable[[], Any]], None],
        Doc(
            """
            A `list` of events that are trigger after the application
            processes the request.

            Read more about the [events](https://lilya.dev/lifespan/).

            **Example**

            ```python
            from edgy import Database, Registry

            from esmerald import Esmerald, Request, Gateway, get

            database = Database("postgresql+asyncpg://user:password@host:port/database")
            registry = Registry(database=database)


            async def create_user(request: Request):
                # Logic to create the user
                data = await request.json()
                ...


            app = Esmerald(
                routes=[Gateway("/create", handler=create_user)],
                after_request=[database.disconnect],
            )
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


def controller(**kwargs: Unpack[ControllerOptions]) -> Callable[[type], type]:
    """Decorator to transform a class into an Esmerald Controller."""

    def wrapper(cls: Any) -> type:
        # Dynamically create a new class that extends Controller and the original class
        base_path = kwargs.get("path", "/")

        kwargs["path"] = clean_path(base_path)
        new_class = type(
            cls.__name__,  # Keep the original class name
            (Controller, cls),  # Ensure it inherits from Controller
            {**cls.__dict__, **kwargs},  # Merge original attributes with kwargs
        )
        return new_class

    return wrapper


def propagator(send: Optional[List[str]] = None, listen: Optional[List[str]] = None) -> Callable:
    """
    Decorator to register event listeners and automatically trigger them when an event is sent.

    This decorator allows a function to:
    - **Send events** (`send` parameter): When the function executes, it will automatically
      trigger the specified events.
    - **Listen to events** (`listen` parameter): The function will be registered as a listener
      for the specified events, meaning it will be called whenever those events are emitted.

    **Example**:

    ```python
    @propagator(send=["user_created"])
    async def create_user():
        return "User created"

    @propagator(listen=["user_created"])
    async def notify_admin():
        print("Admin notified about new user")
    ```

    Parameters:
        send : Optional[List[str]]
            A list of event names that should be emitted when the function is executed.
        listen : Optional[List[str]]
            A list of event names that the function should listen to.

    Callable
        The wrapped function with event propagation behavior.
    """

    def decorator(func: Callable) -> Callable:
        """
        Inner decorator function that wraps the original function to handle event propagation.

        - Registers the function as an event listener if it listens to any events.
        - Wraps the function to emit specified events upon execution.
        """

        # Register function as a listener if it listens to events
        EventDispatcher.register(func, listen)

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Wrapper function that:
            - Calls the original function (sync or async).
            - Emits events defined in `send` after execution.
            """
            result = (
                await func(*args, **kwargs) if is_async_callable(func) else func(*args, **kwargs)
            )

            # Automatically emit the events when function is executed
            if send:
                for event in send:
                    await EventDispatcher.emit(event, *args, **kwargs)

            return result

        return wrapper

    return decorator
