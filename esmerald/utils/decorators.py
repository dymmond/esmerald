from functools import update_wrapper, wraps
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
)

import anyio
from lilya._internal._path import clean_path  # noqa
from lilya.compat import is_async_callable
from typing_extensions import Annotated, Doc, Unpack

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

        # Preserve the original class metadata
        update_wrapper(new_class, cls, updated=())
        return new_class

    return wrapper


def observable(send: Optional[List[str]] = None, listen: Optional[List[str]] = None) -> Callable:
    """
    A decorator that enables a function to participate in an event-driven system.

    - If `send` is provided, the function will emit the specified events after execution.
    - If `listen` is provided, the function will be registered as a listener for those events
      and executed when they are emitted.

    This allows seamless event propagation and reaction, making functions behave like observables.

    Args:
        send (Optional[List[str]]): A list of event names to emit after the function executes.
        listen (Optional[List[str]]): A list of event names the function should listen for.

    Returns:
        Callable: The decorated function with event-driven behavior.
    """

    def decorator(func: Callable) -> Callable:
        """Wraps the function to handle event subscription and emission."""

        async def register() -> None:
            """Registers the function as a listener if `listen` events are specified."""
            if listen:
                for event in listen:
                    await EventDispatcher.subscribe(event, func)

        try:
            anyio.run(register)  # Ensures safe execution if no event loop is running
        except RuntimeError:
            anyio.from_thread.run(register)  # Runs in an existing event loop if active

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Executes the function and emits events if specified.

            - If the function is asynchronous, it is awaited.
            - If the function is synchronous, it is executed in a separate thread.
            - After execution, events defined in `send` are emitted.

            Args:
                *args (Any): Positional arguments for the function.
                **kwargs (Any): Keyword arguments for the function.

            Returns:
                Any: The result of the function execution.
            """
            if is_async_callable(func):
                result = await func(*args, **kwargs)
            else:
                result = await anyio.to_thread.run_sync(func, *args, **kwargs)

            # Emit events after execution
            if send:
                async with anyio.create_task_group() as tg:
                    for event in send:
                        tg.start_soon(
                            lambda e=event, a=args, k=kwargs: EventDispatcher.emit(e, *a, **k)
                        )

            return result

        return wrapper

    return decorator
