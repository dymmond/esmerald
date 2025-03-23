from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    List,
    Optional,
    Sequence,
    TypedDict,
    TypeVar,
    Union,
    Unpack,
)

import anyio
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


T = TypeVar("T", bound=Callable[..., Any])


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
    A decorator that registers a function as an event listener and/or automatically emits events.

    - **Send events** (`send` parameter): When the decorated function executes, it will automatically
      trigger the specified events.
    - **Listen to events** (`listen` parameter): The function will be registered as a listener for the
      specified events and will be executed when those events are emitted.

    This enables a simple event-driven architecture where functions can listen for and propagate events.

    Args:
        send (Optional[List[str]]): A list of event names to emit after the function executes.
        listen (Optional[List[str]]): A list of event names the function should listen for.

    Returns:
        Callable: The decorated function with event propagation behavior.

    Example:
        ```python
        @propagator(send=["user_created"])
        async def create_user():
            return "User created"

        @propagator(listen=["user_created"])
        async def notify_admin():
            print("Admin notified about new user")
        ```
    """

    def decorator(func: Callable) -> Callable:
        """
        Internal decorator function that wraps the original function, ensuring it is properly registered
        as an event listener and emits events when executed.

        Args:
            func (Callable): The function to be wrapped.

        Returns:
            Callable: The function wrapped with event listening and emitting capabilities.
        """

        async def register_if_needed() -> None:
            """
            Registers the function as a listener for specified events.

            This ensures that the function is properly registered in the event dispatcher
            when the application starts.
            """
            await EventDispatcher.register(func, listen)

        # Schedule the listener registration in the background to avoid blocking
        try:
            anyio.run(register_if_needed)  # Safe if no event loop is running
        except RuntimeError:  # If an event loop is already running
            anyio.from_thread.run(register_if_needed)  # Runs inside existing loop

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Executes the original function and propagates events if specified.

            - If the function is asynchronous, it is awaited.
            - If the function is synchronous, it runs safely in a separate thread.
            - After execution, if the `send` parameter is set, the corresponding events are emitted.

            Args:
                *args (Any): Positional arguments for the function.
                **kwargs (Any): Keyword arguments for the function.

            Returns:
                Any: The result of the wrapped function's execution.
            """
            if is_async_callable(func):
                result = await func(*args, **kwargs)
            else:
                result = await anyio.to_thread.run_sync(
                    func, *args, **kwargs
                )  # Run sync function safely

            if send:
                async with anyio.create_task_group() as tg:
                    for event in send:
                        tg.start_soon(EventDispatcher.emit, event, *args, **kwargs)

            return result

        return wrapper

    return decorator
