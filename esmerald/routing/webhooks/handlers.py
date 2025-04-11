from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Union, cast

from lilya import status
from typing_extensions import Annotated, Doc

from esmerald.exceptions import ImproperlyConfigured
from esmerald.openapi.datastructures import OpenAPIResponse
from esmerald.permissions.types import Permission
from esmerald.routing.router import WebhookHandler
from esmerald.types import (
    BackgroundTaskType,
    Dependencies,
    ExceptionHandlerMap,
    Middleware,
    ResponseCookies,
    ResponseHeaders,
    ResponseType,
)
from esmerald.utils.constants import AVAILABLE_METHODS
from esmerald.utils.enums import HttpMethod, MediaType

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.openapi.schemas.v3_1_0 import SecurityScheme


SUCCESSFUL_RESPONSE = "Successful response"


def whget(
    path: Annotated[
        Optional[str],
        Doc(
            """
                Relative path of the `handler`.
                The path can contain parameters in a dictionary like format
                and if the path is not provided, it will default to `/`.

                **Example**

                ```python
                @get()
                ```

                **Example with parameters**

                ```python
                @get(path="/{age: int}")
                ```
                """
        ),
    ] = None,
    *,
    summary: Annotated[
        Optional[str],
        Doc(
            """
                The summary of the handler. This short summary is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Example**

                ```python
                from esmerald import get


                @get(summary="Black Window joining Pretenders")
                async def get_joiners() -> None:
                    ...
                ```
                """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
                The description of the Esmerald application/API. This description is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Example**

                ```python
                from esmerald import get


                @get(description=...)
                async def get_joiners() -> None:
                    ...
                """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
                An integer indicating the status code of the handler.

                This can be achieved by passing directly the value or
                by using the `esmerald.status` or even the `lilya.status`.
                """
        ),
    ] = status.HTTP_200_OK,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content encoding of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content media type of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
                Boolean flag indicating if it should be added to the OpenAPI docs.
                """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
                An instance of an `esmerald.background.BackgroundTask` or `esmerald.background.BackgroundTasks` to be passed onto the handler.

                Read more about [Background tasks](https://esmerald.dev/background-tasks/) to
                understand what can be done.
                """
        ),
    ] = None,
    dependencies: Annotated[
        Optional["Dependencies"],
        Doc(
            """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
        ),
    ] = None,
    exception_handlers: Annotated[
        Optional["ExceptionHandlerMap"],
        Doc(
            """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
        ),
    ] = None,
    middleware: Annotated[
        Optional[List["Middleware"]],
        Doc(
            """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
        ),
    ] = None,
    permissions: Annotated[
        Optional[List["Permission"]],
        Doc(
            """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
        ),
    ] = None,
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
                The default `media-type` used by the handler.
                """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
                Response class to be used within the
                handler application.

                Read more about the [Responses](https://esmerald.dev/responses/) and how
                to use them.

                **Example**

                ```python
                from esmerald import get, JSONResponse

                @get(response_class=JSONResponse)
                ```
                """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
                A sequence of `esmerald.datastructures.Cookie` objects.

                Read more about the [Cookies](https://esmerald.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

                **Example**

                ```python
                from esmerald import get
                from esmerald.datastructures import Cookie

                response_cookies=[
                    Cookie(
                        key="csrf",
                        value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                        max_age=3000,
                        httponly=True,
                    )
                ]

                @get(response_cookies=response_cookies)
                ```
                """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
                A mapping of `esmerald.datastructures.ResponseHeader` objects.

                Read more about the [ResponseHeader](https://esmerald.dev/extras/header-fields/#response-headers).

                **Example**

                ```python
                from esmerald import get
                from esmerald.datastructures import ResponseHeader

                response_headers={
                    "authorize": ResponseHeader(value="granted")
                }

                @get(response_headers=response_headers)
                ```
                """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
                A list of strings tags to be applied to the *path operation*.

                It will be added to the generated OpenAPI documentation.

                **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means
                these tags on a Esmerald instance, means it will be added to every route even
                if those routes also contain tags.

                **Example**

                ```python
                from esmerald import get

                @get(tags=["application"])
                ```
                """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
                Boolean flag indicating if the handler
                should be deprecated in the OpenAPI documentation.

                **Example**

                ```python
                from esmerald import get

                @get(deprecated=True)
                ```
                """
        ),
    ] = None,
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

                **Example**

                ```python
                from esmerald import get
                from esmerald.openapi.security.http import Bearer

                @get(security=[Bearer()])
                ```
                """
        ),
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
                The unique identifier of the `handler`. This acts as a unique ID
                for the OpenAPI documentation.

                !!! Tip
                    Usually you don't need this as Esmerald handles it automatically
                    but it is here if you want to add your own.
                """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
                A description of the response. This is used for OpenAPI documentation
                purposes only and accepts all the docstrings including `markdown` format.
                """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[Dict[int, OpenAPIResponse]],
        Doc(
            """
                Additional responses that are handled by the handler and need to be described
                in the OpenAPI documentation.

                The `responses` is a dictionary like object where the first parameter is an
                `integer` and the second is an instance of an [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object.


                Read more about [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object and how to use it.


                **Example**

                ```python
                from esmerald import get
                from esmerald.openapi.datastructures import OpenAPIResponse
                from pydantic import BaseModel

                class Power(BaseModel):
                    name: str
                    description: str


                class Error(BaseModel):
                    detail: str


                @get(path='/read', responses={
                        200: OpenAPIResponse(model=Power, description=...)
                        400: OpenAPIResponse(model=Error, description=...)
                    }
                )
                async def create() -> Union[None, ItemOut]:
                    ...
                ```
                """
        ),
    ] = None,
) -> WebhookHandler:
    """
    Handler responsible for the HTTP method `get` and
    all of its operatations.

    **Example**

    ```python
    from esmerald import get


    @get()
    async def get() -> str:
        return "Hello, World!"
    ```
    """

    def wrapper(func: Any) -> WebhookHandler:
        handler = WebhookHandler(
            path=path,
            methods=[HttpMethod.GET],
            summary=summary,
            description=description,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
        )
        handler.fn = func
        handler.handler = func
        handler.__type__ = HttpMethod.GET.value
        handler.validate_handler()
        return handler

    return cast(WebhookHandler, wrapper)


def whhead(
    path: Annotated[
        Optional[str],
        Doc(
            """
                Relative path of the `handler`.
                The path can contain parameters in a dictionary like format
                and if the path is not provided, it will default to `/`.
                """
        ),
    ] = None,
    *,
    summary: Annotated[
        Optional[str],
        Doc(
            """
                The summary of the handler. This short summary is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.
                """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
                The description of the Esmerald application/API. This description is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.
                """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
                An integer indicating the status code of the handler.

                This can be achieved by passing directly the value or
                by using the `esmerald.status` or even the `lilya.status`.
                """
        ),
    ] = status.HTTP_200_OK,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content encoding of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content media type of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
                Boolean flag indicating if it should be added to the OpenAPI docs.
                """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
                An instance of an `esmerald.background.BackgroundTask` or `esmerald.background.BackgroundTasks` to be passed onto the handler.

                Read more about [Background tasks](https://esmerald.dev/background-tasks/) to
                understand what can be done.
                """
        ),
    ] = None,
    dependencies: Annotated[
        Optional["Dependencies"],
        Doc(
            """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
        ),
    ] = None,
    exception_handlers: Annotated[
        Optional["ExceptionHandlerMap"],
        Doc(
            """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
        ),
    ] = None,
    middleware: Annotated[
        Optional[List["Middleware"]],
        Doc(
            """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
        ),
    ] = None,
    permissions: Annotated[
        Optional[List["Permission"]],
        Doc(
            """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
        ),
    ] = None,
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
                The default `media-type` used by the handler.
                """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
                Response class to be used within the
                handler application.

                Read more about the [Responses](https://esmerald.dev/responses/) and how
                to use them.
                """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
                A sequence of `esmerald.datastructures.Cookie` objects.

                Read more about the [Cookies](https://esmerald.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).
                """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
                A mapping of `esmerald.datastructures.ResponseHeader` objects.

                Read more about the [ResponseHeader](https://esmerald.dev/extras/header-fields/#response-headers).
                """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
                A list of strings tags to be applied to the *path operation*.

                It will be added to the generated OpenAPI documentation.

                **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means
                these tags on a Esmerald instance, means it will be added to every route even
                if those routes also contain tags.
                """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
                Boolean flag indicating if the handler
                should be deprecated in the OpenAPI documentation.
                """
        ),
    ] = None,
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
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
                The unique identifier of the `handler`. This acts as a unique ID
                for the OpenAPI documentation.

                !!! Tip
                    Usually you don't need this as Esmerald handles it automatically
                    but it is here if you want to add your own.
                """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
                A description of the response. This is used for OpenAPI documentation
                purposes only and accepts all the docstrings including `markdown` format.
                """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[Dict[int, OpenAPIResponse]],
        Doc(
            """
                Additional responses that are handled by the handler and need to be described
                in the OpenAPI documentation.

                The `responses` is a dictionary like object where the first parameter is an
                `integer` and the second is an instance of an [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object.


                Read more about [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object and how to use it.
                """
        ),
    ] = None,
) -> WebhookHandler:
    """
    Handler responsible for the HTTP method `head` and
    all of its operatations.
    """

    def wrapper(func: Any) -> WebhookHandler:
        handler = WebhookHandler(
            path=path,
            methods=[HttpMethod.HEAD],
            summary=summary,
            description=description,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
        )
        handler.fn = func
        handler.handler = func
        handler.__type__ = HttpMethod.HEAD.value
        handler.validate_handler()
        return handler

    return cast(WebhookHandler, wrapper)


def whpost(
    path: Annotated[
        Optional[str],
        Doc(
            """
                Relative path of the `handler`.
                The path can contain parameters in a dictionary like format
                and if the path is not provided, it will default to `/`.

                **Example**

                ```python
                @post()
                ```

                **Example with parameters**

                ```python
                @post(path="/{age: int}")
                ```
                """
        ),
    ] = None,
    *,
    summary: Annotated[
        Optional[str],
        Doc(
            """
                The summary of the handler. This short summary is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Example**

                ```python
                from esmerald import post
                from pydantic import BaseModel


                class Pretender(BaseModel):
                    name: str


                @post(summary="Black Window joining Pretenders")
                async def create_joiners(data: Pretender) -> None:
                    ...
                ```
                """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
                The description of the Esmerald application/API. This description is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Example**

                ```python
                from esmerald import post


                @post(description=...)
                async def create_joiners() -> None:
                    ...
                """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
                An integer indicating the status code of the handler.

                This can be achieved by passing directly the value or
                by using the `esmerald.status` or even the `lilya.status`.
                """
        ),
    ] = status.HTTP_201_CREATED,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content encoding of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content media type of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
                Boolean flag indicating if it should be added to the OpenAPI docs.
                """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
                An instance of an `esmerald.background.BackgroundTask` or `esmerald.background.BackgroundTasks` to be passed onto the handler.

                Read more about [Background tasks](https://esmerald.dev/background-tasks/) to
                understand what can be done.
                """
        ),
    ] = None,
    dependencies: Annotated[
        Optional["Dependencies"],
        Doc(
            """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
        ),
    ] = None,
    exception_handlers: Annotated[
        Optional["ExceptionHandlerMap"],
        Doc(
            """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
        ),
    ] = None,
    middleware: Annotated[
        Optional[List["Middleware"]],
        Doc(
            """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
        ),
    ] = None,
    permissions: Annotated[
        Optional[List["Permission"]],
        Doc(
            """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
        ),
    ] = None,
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
                The default `media-type` used by the handler.
                """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
                Response class to be used within the
                handler application.

                Read more about the [Responses](https://esmerald.dev/responses/) and how
                to use them.

                **Example**

                ```python
                from esmerald import post, JSONResponse

                @post(response_class=JSONResponse)
                ```
                """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
                A sequence of `esmerald.datastructures.Cookie` objects.

                Read more about the [Cookies](https://esmerald.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

                **Example**

                ```python
                from esmerald import post
                from esmerald.datastructures import Cookie

                response_cookies=[
                    Cookie(
                        key="csrf",
                        value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                        max_age=3000,
                        httponly=True,
                    )
                ]

                @post(response_cookies=response_cookies)
                ```
                """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
                A mapping of `esmerald.datastructures.ResponseHeader` objects.

                Read more about the [ResponseHeader](https://esmerald.dev/extras/header-fields/#response-headers).

                **Example**

                ```python
                from esmerald import post
                from esmerald.datastructures import ResponseHeader

                response_headers={
                    "authorize": ResponseHeader(value="granted")
                }

                @post(response_headers=response_headers)
                ```
                """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
                A list of strings tags to be applied to the *path operation*.

                It will be added to the generated OpenAPI documentation.

                **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means
                these tags on a Esmerald instance, means it will be added to every route even
                if those routes also contain tags.

                **Example**

                ```python
                from esmerald import post

                @post(tags=["application"])
                ```
                """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
                Boolean flag indicating if the handler
                should be deprecated in the OpenAPI documentation.

                **Example**

                ```python
                from esmerald import post

                @post(deprecated=True)
                ```
                """
        ),
    ] = None,
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

                **Example**

                ```python
                from esmerald import post
                from esmerald.openapi.security.http import Bearer

                @post(security=[Bearer()])
                ```
                """
        ),
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
                The unique identifier of the `handler`. This acts as a unique ID
                for the OpenAPI documentation.

                !!! Tip
                    Usually you don't need this as Esmerald handles it automatically
                    but it is here if you want to add your own.
                """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
                A description of the response. This is used for OpenAPI documentation
                purposes only and accepts all the docstrings including `markdown` format.
                """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[Dict[int, OpenAPIResponse]],
        Doc(
            """
                Additional responses that are handled by the handler and need to be described
                in the OpenAPI documentation.

                The `responses` is a dictionary like object where the first parameter is an
                `integer` and the second is an instance of an [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object.


                Read more about [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object and how to use it.


                **Example**

                ```python
                from esmerald import post
                from esmerald.openapi.datastructures import OpenAPIResponse
                from pydantic import BaseModel

                class Power(BaseModel):
                    name: str
                    description: str


                class Error(BaseModel):
                    detail: str


                @post(path='/read', responses={
                        200: OpenAPIResponse(model=Power, description=...)
                        400: OpenAPIResponse(model=Error, description=...)
                    }
                )
                async def create() -> Union[None, ItemOut]:
                    ...
                ```
                """
        ),
    ] = None,
) -> WebhookHandler:
    """
    Handler responsible for the HTTP method `post` and
    all of its operatations.

    **Example**

    ```python
    from esmerald import post


    @post()
    async def create() -> None:
        ...
    ```
    """

    def wrapper(func: Any) -> WebhookHandler:
        handler = WebhookHandler(
            path=path,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            summary=summary,
            description=description,
            methods=[HttpMethod.POST],
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
        )
        handler.fn = func
        handler.handler = func
        handler.__type__ = HttpMethod.POST.value
        handler.validate_handler()
        return handler

    return cast(WebhookHandler, wrapper)


def whput(
    path: Annotated[
        Optional[str],
        Doc(
            """
                Relative path of the `handler`.
                The path can contain parameters in a dictionary like format
                and if the path is not provided, it will default to `/`.

                **Example**

                ```python
                @put()
                ```

                **Example with parameters**

                ```python
                @put(path="/{age: int}")
                ```
                """
        ),
    ] = None,
    *,
    summary: Annotated[
        Optional[str],
        Doc(
            """
                The summary of the handler. This short summary is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Example**

                ```python
                from esmerald import put


                @put(summary="Black Window joining Pretenders")
                async def update_joiners() -> None:
                    ...
                ```
                """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
                The description of the Esmerald application/API. This description is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Example**

                ```python
                from esmerald import put


                @put(description=...)
                async def update_joiners() -> None:
                    ...
                """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
                An integer indicating the status code of the handler.

                This can be achieved by passing directly the value or
                by using the `esmerald.status` or even the `lilya.status`.
                """
        ),
    ] = status.HTTP_200_OK,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content encoding of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content media type of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
                Boolean flag indicating if it should be added to the OpenAPI docs.
                """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
                An instance of an `esmerald.background.BackgroundTask` or `esmerald.background.BackgroundTasks` to be passed onto the handler.

                Read more about [Background tasks](https://esmerald.dev/background-tasks/) to
                understand what can be done.
                """
        ),
    ] = None,
    dependencies: Annotated[
        Optional["Dependencies"],
        Doc(
            """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
        ),
    ] = None,
    exception_handlers: Annotated[
        Optional["ExceptionHandlerMap"],
        Doc(
            """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
        ),
    ] = None,
    middleware: Annotated[
        Optional[List["Middleware"]],
        Doc(
            """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
        ),
    ] = None,
    permissions: Annotated[
        Optional[List["Permission"]],
        Doc(
            """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
        ),
    ] = None,
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
                The default `media-type` used by the handler.
                """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
                Response class to be used within the
                handler application.

                Read more about the [Responses](https://esmerald.dev/responses/) and how
                to use them.

                **Example**

                ```python
                from esmerald import put, JSONResponse

                @put(response_class=JSONResponse)
                ```
                """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
                A sequence of `esmerald.datastructures.Cookie` objects.

                Read more about the [Cookies](https://esmerald.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

                **Example**

                ```python
                from esmerald import put
                from esmerald.datastructures import Cookie

                response_cookies=[
                    Cookie(
                        key="csrf",
                        value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                        max_age=3000,
                        httponly=True,
                    )
                ]

                @put(response_cookies=response_cookies)
                ```
                """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
                A mapping of `esmerald.datastructures.ResponseHeader` objects.

                Read more about the [ResponseHeader](https://esmerald.dev/extras/header-fields/#response-headers).

                **Example**

                ```python
                from esmerald import put
                from esmerald.datastructures import ResponseHeader

                response_headers={
                    "authorize": ResponseHeader(value="granted")
                }

                @put(response_headers=response_headers)
                ```
                """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
                A list of strings tags to be applied to the *path operation*.

                It will be added to the generated OpenAPI documentation.

                **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means
                these tags on a Esmerald instance, means it will be added to every route even
                if those routes also contain tags.

                **Example**

                ```python
                from esmerald import put

                @put(tags=["application"])
                ```
                """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
                Boolean flag indicating if the handler
                should be deprecated in the OpenAPI documentation.

                **Example**

                ```python
                from esmerald import put

                @put(deprecated=True)
                ```
                """
        ),
    ] = None,
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

                **Example**

                ```python
                from esmerald import put
                from esmerald.openapi.security.http import Bearer

                @put(security=[Bearer()])
                ```
                """
        ),
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
                The unique identifier of the `handler`. This acts as a unique ID
                for the OpenAPI documentation.

                !!! Tip
                    Usually you don't need this as Esmerald handles it automatically
                    but it is here if you want to add your own.
                """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
                A description of the response. This is used for OpenAPI documentation
                purposes only and accepts all the docstrings including `markdown` format.
                """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[Dict[int, OpenAPIResponse]],
        Doc(
            """
                Additional responses that are handled by the handler and need to be described
                in the OpenAPI documentation.

                The `responses` is a dictionary like object where the first parameter is an
                `integer` and the second is an instance of an [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object.


                Read more about [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object and how to use it.


                **Example**

                ```python
                from esmerald import put
                from esmerald.openapi.datastructures import OpenAPIResponse
                from pydantic import BaseModel

                class Power(BaseModel):
                    name: str
                    description: str


                class Error(BaseModel):
                    detail: str


                @put(path='/read', responses={
                        200: OpenAPIResponse(model=Power, description=...)
                        400: OpenAPIResponse(model=Error, description=...)
                    }
                )
                async def create() -> Union[None, ItemOut]:
                    ...
                ```
                """
        ),
    ] = None,
) -> WebhookHandler:
    """
    Handler responsible for the HTTP method `put` and
    all of its operatations.

    **Example**

    ```python
    from esmerald import put


    @put()
    async def update() -> str:
        return "updated!"
    ```
    """

    def wrapper(func: Any) -> WebhookHandler:
        handler = WebhookHandler(
            path=path,
            methods=[HttpMethod.PUT],
            summary=summary,
            description=description,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
        )
        handler.fn = func
        handler.handler = func
        handler.__type__ = HttpMethod.PUT.value
        handler.validate_handler()
        return handler

    return cast(WebhookHandler, wrapper)


def whpatch(
    path: Annotated[
        Optional[str],
        Doc(
            """
                Relative path of the `handler`.
                The path can contain parameters in a dictionary like format
                and if the path is not provided, it will default to `/`.

                **Example**

                ```python
                @patch()
                ```

                **Example with parameters**

                ```python
                @patch(path="/{age: int}")
                ```
                """
        ),
    ] = None,
    *,
    summary: Annotated[
        Optional[str],
        Doc(
            """
                The summary of the handler. This short summary is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Example**

                ```python
                from esmerald import patch


                @patch(summary="Black Window joining Pretenders")
                async def update_partial_joiners() -> None:
                    ...
                ```
                """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
                The description of the Esmerald application/API. This description is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Example**

                ```python
                from esmerald import patch


                @patch(description=...)
                async def update_partial_joiners() -> None:
                    ...
                """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
                An integer indicating the status code of the handler.

                This can be achieved by passing directly the value or
                by using the `esmerald.status` or even the `lilya.status`.
                """
        ),
    ] = status.HTTP_200_OK,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content encoding of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content media type of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
                Boolean flag indicating if it should be added to the OpenAPI docs.
                """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
                An instance of an `esmerald.background.BackgroundTask` or `esmerald.background.BackgroundTasks` to be passed onto the handler.

                Read more about [Background tasks](https://esmerald.dev/background-tasks/) to
                understand what can be done.
                """
        ),
    ] = None,
    dependencies: Annotated[
        Optional["Dependencies"],
        Doc(
            """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
        ),
    ] = None,
    exception_handlers: Annotated[
        Optional["ExceptionHandlerMap"],
        Doc(
            """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
        ),
    ] = None,
    middleware: Annotated[
        Optional[List["Middleware"]],
        Doc(
            """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
        ),
    ] = None,
    permissions: Annotated[
        Optional[List["Permission"]],
        Doc(
            """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
        ),
    ] = None,
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
                The default `media-type` used by the handler.
                """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
                Response class to be used within the
                handler application.

                Read more about the [Responses](https://esmerald.dev/responses/) and how
                to use them.

                **Example**

                ```python
                from esmerald import patch, JSONResponse

                @patch(response_class=JSONResponse)
                ```
                """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
                A sequence of `esmerald.datastructures.Cookie` objects.

                Read more about the [Cookies](https://esmerald.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

                **Example**

                ```python
                from esmerald import patch
                from esmerald.datastructures import Cookie

                response_cookies=[
                    Cookie(
                        key="csrf",
                        value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                        max_age=3000,
                        httponly=True,
                    )
                ]

                @patch(response_cookies=response_cookies)
                ```
                """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
                A mapping of `esmerald.datastructures.ResponseHeader` objects.

                Read more about the [ResponseHeader](https://esmerald.dev/extras/header-fields/#response-headers).

                **Example**

                ```python
                from esmerald import patch
                from esmerald.datastructures import ResponseHeader

                response_headers={
                    "authorize": ResponseHeader(value="granted")
                }

                @patch(response_headers=response_headers)
                ```
                """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
                A list of strings tags to be applied to the *path operation*.

                It will be added to the generated OpenAPI documentation.

                **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means
                these tags on a Esmerald instance, means it will be added to every route even
                if those routes also contain tags.

                **Example**

                ```python
                from esmerald import patch

                @patch(tags=["application"])
                ```
                """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
                Boolean flag indicating if the handler
                should be deprecated in the OpenAPI documentation.

                **Example**

                ```python
                from esmerald import patch

                @patch(deprecated=True)
                ```
                """
        ),
    ] = None,
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

                **Example**

                ```python
                from esmerald import patch
                from esmerald.openapi.security.http import Bearer

                @patch(security=[Bearer()])
                ```
                """
        ),
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
                The unique identifier of the `handler`. This acts as a unique ID
                for the OpenAPI documentation.

                !!! Tip
                    Usually you don't need this as Esmerald handles it automatically
                    but it is here if you want to add your own.
                """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
                A description of the response. This is used for OpenAPI documentation
                purposes only and accepts all the docstrings including `markdown` format.
                """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[Dict[int, OpenAPIResponse]],
        Doc(
            """
                Additional responses that are handled by the handler and need to be described
                in the OpenAPI documentation.

                The `responses` is a dictionary like object where the first parameter is an
                `integer` and the second is an instance of an [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object.


                Read more about [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object and how to use it.


                **Example**

                ```python
                from esmerald import patch
                from esmerald.openapi.datastructures import OpenAPIResponse
                from pydantic import BaseModel

                class Power(BaseModel):
                    name: str
                    description: str


                class Error(BaseModel):
                    detail: str


                @patch(path='/read', responses={
                        200: OpenAPIResponse(model=Power, description=...)
                        400: OpenAPIResponse(model=Error, description=...)
                    }
                )
                async def update() -> Union[None, ItemOut]:
                    ...
                ```
                """
        ),
    ] = None,
) -> WebhookHandler:
    """
    Handler responsible for the HTTP method `path` and
    all of its operatations.

    **Example**

    ```python
    from esmerald import patch


    @patch()
    async def update_partial() -> str:
        return "done!"
    ```
    """

    def wrapper(func: Any) -> WebhookHandler:
        handler = WebhookHandler(
            path=path,
            methods=[HttpMethod.PATCH],
            summary=summary,
            description=description,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
        )
        handler.fn = func
        handler.handler = func
        handler.__type__ = HttpMethod.PATCH.value
        handler.validate_handler()
        return handler

    return cast(WebhookHandler, wrapper)


def whdelete(
    path: Annotated[
        Optional[str],
        Doc(
            """
                Relative path of the `handler`.
                The path can contain parameters in a dictionary like format
                and if the path is not provided, it will default to `/`.

                **Example**

                ```python
                @delete()
                ```

                **Example with parameters**

                ```python
                @delete(path="/{age: int}")
                ```
                """
        ),
    ] = None,
    *,
    summary: Annotated[
        Optional[str],
        Doc(
            """
                The summary of the handler. This short summary is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Example**

                ```python
                from esmerald import delete


                @delete(summary="Black Window joining Pretenders")
                async def delete_joiners() -> None:
                    ...
                ```
                """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
                The description of the Esmerald application/API. This description is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Example**

                ```python
                from esmerald import delete


                @delete(description=...)
                async def delete_joiners() -> None:
                    ...
                """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
                An integer indicating the status code of the handler.

                This can be achieved by passing directly the value or
                by using the `esmerald.status` or even the `lilya.status`.
                """
        ),
    ] = status.HTTP_204_NO_CONTENT,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content encoding of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content media type of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
                Boolean flag indicating if it should be added to the OpenAPI docs.
                """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
                An instance of an `esmerald.background.BackgroundTask` or `esmerald.background.BackgroundTasks` to be passed onto the handler.

                Read more about [Background tasks](https://esmerald.dev/background-tasks/) to
                understand what can be done.
                """
        ),
    ] = None,
    dependencies: Annotated[
        Optional["Dependencies"],
        Doc(
            """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
        ),
    ] = None,
    exception_handlers: Annotated[
        Optional["ExceptionHandlerMap"],
        Doc(
            """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
        ),
    ] = None,
    middleware: Annotated[
        Optional[List["Middleware"]],
        Doc(
            """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
        ),
    ] = None,
    permissions: Annotated[
        Optional[List["Permission"]],
        Doc(
            """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
        ),
    ] = None,
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
                The default `media-type` used by the handler.
                """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
                Response class to be used within the
                handler application.

                Read more about the [Responses](https://esmerald.dev/responses/) and how
                to use them.

                **Example**

                ```python
                from esmerald import delete, JSONResponse

                @delete(response_class=JSONResponse)
                ```
                """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
                A sequence of `esmerald.datastructures.Cookie` objects.

                Read more about the [Cookies](https://esmerald.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

                **Example**

                ```python
                from esmerald import delete
                from esmerald.datastructures import Cookie

                response_cookies=[
                    Cookie(
                        key="csrf",
                        value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                        max_age=3000,
                        httponly=True,
                    )
                ]

                @delete(response_cookies=response_cookies)
                ```
                """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
                A mapping of `esmerald.datastructures.ResponseHeader` objects.

                Read more about the [ResponseHeader](https://esmerald.dev/extras/header-fields/#response-headers).

                **Example**

                ```python
                from esmerald import delete
                from esmerald.datastructures import ResponseHeader

                response_headers={
                    "authorize": ResponseHeader(value="granted")
                }

                @delete(response_headers=response_headers)
                ```
                """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
                A list of strings tags to be applied to the *path operation*.

                It will be added to the generated OpenAPI documentation.

                **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means
                these tags on a Esmerald instance, means it will be added to every route even
                if those routes also contain tags.

                **Example**

                ```python
                from esmerald import delete

                @delete(tags=["application"])
                ```
                """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
                Boolean flag indicating if the handler
                should be deprecated in the OpenAPI documentation.

                **Example**

                ```python
                from esmerald import delete

                @delete(deprecated=True)
                ```
                """
        ),
    ] = None,
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

                **Example**

                ```python
                from esmerald import delete
                from esmerald.openapi.security.http import Bearer

                @delete(security=[Bearer()])
                ```
                """
        ),
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
                The unique identifier of the `handler`. This acts as a unique ID
                for the OpenAPI documentation.

                !!! Tip
                    Usually you don't need this as Esmerald handles it automatically
                    but it is here if you want to add your own.
                """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
                A description of the response. This is used for OpenAPI documentation
                purposes only and accepts all the docstrings including `markdown` format.
                """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[Dict[int, OpenAPIResponse]],
        Doc(
            """
                Additional responses that are handled by the handler and need to be described
                in the OpenAPI documentation.

                The `responses` is a dictionary like object where the first parameter is an
                `integer` and the second is an instance of an [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object.


                Read more about [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object and how to use it.


                **Example**

                ```python
                from esmerald import delete
                from esmerald.openapi.datastructures import OpenAPIResponse
                from pydantic import BaseModel

                class Power(BaseModel):
                    name: str
                    description: str


                class Error(BaseModel):
                    detail: str


                @delete(path='/read', responses={
                        400: OpenAPIResponse(model=Error, description=...)
                        401: OpenAPIResponse(model=Power, description=...)
                    }
                )
                async def remove() -> Union[None, ItemOut]:
                    ...
                ```
                """
        ),
    ] = None,
) -> WebhookHandler:
    """
    Handler responsible for the HTTP method `delete` and
    all of its operatations.

    **Example**

    ```python
    from esmerald import delete


    @delete()
    async def remove() -> None:
        ...
    ```
    """

    def wrapper(func: Any) -> WebhookHandler:
        handler = WebhookHandler(
            path=path,
            methods=[HttpMethod.DELETE],
            summary=summary,
            description=description,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
        )
        handler.fn = func
        handler.handler = func
        handler.__type__ = HttpMethod.DELETE.value
        handler.validate_handler()
        return handler

    return cast(WebhookHandler, wrapper)


def whoptions(
    path: Annotated[
        Optional[str],
        Doc(
            """
                Relative path of the `handler`.
                The path can contain parameters in a dictionary like format
                and if the path is not provided, it will default to `/`.
                """
        ),
    ] = None,
    *,
    summary: Annotated[
        Optional[str],
        Doc(
            """
                The summary of the handler. This short summary is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.
                """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
                The description of the Esmerald application/API. This description is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.
                """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
                An integer indicating the status code of the handler.

                This can be achieved by passing directly the value or
                by using the `esmerald.status` or even the `lilya.status`.
                """
        ),
    ] = status.HTTP_200_OK,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content encoding of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content media type of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
                Boolean flag indicating if it should be added to the OpenAPI docs.
                """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
                An instance of an `esmerald.background.BackgroundTask` or `esmerald.background.BackgroundTasks` to be passed onto the handler.

                Read more about [Background tasks](https://esmerald.dev/background-tasks/) to
                understand what can be done.
                """
        ),
    ] = None,
    dependencies: Annotated[
        Optional["Dependencies"],
        Doc(
            """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
        ),
    ] = None,
    exception_handlers: Annotated[
        Optional["ExceptionHandlerMap"],
        Doc(
            """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
        ),
    ] = None,
    middleware: Annotated[
        Optional[List["Middleware"]],
        Doc(
            """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
        ),
    ] = None,
    permissions: Annotated[
        Optional[List["Permission"]],
        Doc(
            """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
        ),
    ] = None,
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
                The default `media-type` used by the handler.
                """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
                Response class to be used within the
                handler application.

                Read more about the [Responses](https://esmerald.dev/responses/) and how
                to use them.
                """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
                A sequence of `esmerald.datastructures.Cookie` objects.

                Read more about the [Cookies](https://esmerald.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).
                """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
                A mapping of `esmerald.datastructures.ResponseHeader` objects.

                Read more about the [ResponseHeader](https://esmerald.dev/extras/header-fields/#response-headers).
                """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
                A list of strings tags to be applied to the *path operation*.

                It will be added to the generated OpenAPI documentation.

                **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means
                these tags on a Esmerald instance, means it will be added to every route even
                if those routes also contain tags.
                """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
                Boolean flag indicating if the handler
                should be deprecated in the OpenAPI documentation.
                """
        ),
    ] = None,
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
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
                The unique identifier of the `handler`. This acts as a unique ID
                for the OpenAPI documentation.

                !!! Tip
                    Usually you don't need this as Esmerald handles it automatically
                    but it is here if you want to add your own.
                """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
                A description of the response. This is used for OpenAPI documentation
                purposes only and accepts all the docstrings including `markdown` format.
                """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[Dict[int, OpenAPIResponse]],
        Doc(
            """
                Additional responses that are handled by the handler and need to be described
                in the OpenAPI documentation.

                The `responses` is a dictionary like object where the first parameter is an
                `integer` and the second is an instance of an [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object.


                Read more about [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object and how to use it.
                """
        ),
    ] = None,
) -> WebhookHandler:
    """
    Handler responsible for the HTTP method `options` and
    all of its operatations.
    """

    def wrapper(func: Any) -> WebhookHandler:
        handler = WebhookHandler(
            path=path,
            methods=[HttpMethod.OPTIONS],
            summary=summary,
            description=description,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
        )
        handler.fn = func
        handler.handler = func
        handler.__type__ = HttpMethod.OPTIONS.value
        handler.validate_handler()
        return handler

    return cast(WebhookHandler, wrapper)


def whtrace(
    path: Annotated[
        Optional[str],
        Doc(
            """
                Relative path of the `handler`.
                The path can contain parameters in a dictionary like format
                and if the path is not provided, it will default to `/`.
                """
        ),
    ] = None,
    *,
    summary: Annotated[
        Optional[str],
        Doc(
            """
                The summary of the handler. This short summary is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.
                """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
                The description of the Esmerald application/API. This description is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.
                """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
                An integer indicating the status code of the handler.

                This can be achieved by passing directly the value or
                by using the `esmerald.status` or even the `lilya.status`.
                """
        ),
    ] = status.HTTP_200_OK,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content encoding of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content media type of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
                Boolean flag indicating if it should be added to the OpenAPI docs.
                """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
                An instance of an `esmerald.background.BackgroundTask` or `esmerald.background.BackgroundTasks` to be passed onto the handler.

                Read more about [Background tasks](https://esmerald.dev/background-tasks/) to
                understand what can be done.
                """
        ),
    ] = None,
    dependencies: Annotated[
        Optional["Dependencies"],
        Doc(
            """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
        ),
    ] = None,
    exception_handlers: Annotated[
        Optional["ExceptionHandlerMap"],
        Doc(
            """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
        ),
    ] = None,
    middleware: Annotated[
        Optional[List["Middleware"]],
        Doc(
            """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
        ),
    ] = None,
    permissions: Annotated[
        Optional[List["Permission"]],
        Doc(
            """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
        ),
    ] = None,
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
                The default `media-type` used by the handler.
                """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
                Response class to be used within the
                handler application.

                Read more about the [Responses](https://esmerald.dev/responses/) and how
                to use them.
                """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
                A sequence of `esmerald.datastructures.Cookie` objects.

                Read more about the [Cookies](https://esmerald.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).
                """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
                A mapping of `esmerald.datastructures.ResponseHeader` objects.

                Read more about the [ResponseHeader](https://esmerald.dev/extras/header-fields/#response-headers).
                """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
                A list of strings tags to be applied to the *path operation*.

                It will be added to the generated OpenAPI documentation.

                **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means
                these tags on a Esmerald instance, means it will be added to every route even
                if those routes also contain tags.
                """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
                Boolean flag indicating if the handler
                should be deprecated in the OpenAPI documentation.
                """
        ),
    ] = None,
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
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
                The unique identifier of the `handler`. This acts as a unique ID
                for the OpenAPI documentation.

                !!! Tip
                    Usually you don't need this as Esmerald handles it automatically
                    but it is here if you want to add your own.
                """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
                A description of the response. This is used for OpenAPI documentation
                purposes only and accepts all the docstrings including `markdown` format.
                """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[Dict[int, OpenAPIResponse]],
        Doc(
            """
                Additional responses that are handled by the handler and need to be described
                in the OpenAPI documentation.

                The `responses` is a dictionary like object where the first parameter is an
                `integer` and the second is an instance of an [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object.


                Read more about [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object and how to use it.
                """
        ),
    ] = None,
) -> WebhookHandler:
    """
    Handler responsible for the HTTP method `trace` and
    all of its operatations.
    ```
    """

    def wrapper(func: Any) -> WebhookHandler:
        handler = WebhookHandler(
            path=path,
            methods=[HttpMethod.TRACE],
            summary=summary,
            description=description,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
        )
        handler.fn = func
        handler.handler = func
        handler.__type__ = HttpMethod.TRACE.value
        handler.validate_handler()
        return handler

    return cast(WebhookHandler, wrapper)


def whroute(
    path: Annotated[
        Optional[str],
        Doc(
            """
                Relative path of the `handler`.
                The path can contain parameters in a dictionary like format
                and if the path is not provided, it will default to `/`.

                **Example**

                ```python
                @route()
                ```

                **Example with parameters**

                ```python
                @route(path="/{age: int}")
                ```
                """
        ),
    ] = None,
    *,
    methods: Annotated[
        List[str],
        Doc(
            """
                List of strings of methods allowed by the handler.

                **Example**

                ```python
                from esmerald import route


                @route(methods=["GET", "POST", "PUT", "DELETE"])
                async def handle_stuff() -> None:
                    ...
                ```
                """
        ),
    ] = None,
    summary: Annotated[
        Optional[str],
        Doc(
            """
                The summary of the handler. This short summary is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Example**

                ```python
                from esmerald import route


                @route(summary="Black Window joining Pretenders")
                async def operate() -> None:
                    ...
                ```
                """
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        Doc(
            """
                The description of the Esmerald application/API. This description is displayed when the [OpenAPI](https://esmerald.dev/openapi/) documentation is used.

                **Example**

                ```python
                from esmerald import route


                @route(description=...)
                async def operate_joiners() -> None:
                    ...
                """
        ),
    ] = None,
    status_code: Annotated[
        Optional[int],
        Doc(
            """
                An integer indicating the status code of the handler.

                This can be achieved by passing directly the value or
                by using the `esmerald.status` or even the `lilya.status`.
                """
        ),
    ] = status.HTTP_200_OK,
    content_encoding: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content encoding of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    content_media_type: Annotated[
        Optional[str],
        Doc(
            """
                The string indicating the content media type of the handler.

                This is used for the generation of the [OpenAPI](https://esmerald.dev/openapi/)
                documentation.
                """
        ),
    ] = None,
    include_in_schema: Annotated[
        bool,
        Doc(
            """
                Boolean flag indicating if it should be added to the OpenAPI docs.
                """
        ),
    ] = True,
    background: Annotated[
        Optional["BackgroundTaskType"],
        Doc(
            """
                An instance of an `esmerald.background.BackgroundTask` or `esmerald.background.BackgroundTasks` to be passed onto the handler.

                Read more about [Background tasks](https://esmerald.dev/background-tasks/) to
                understand what can be done.
                """
        ),
    ] = None,
    dependencies: Annotated[
        Optional["Dependencies"],
        Doc(
            """
                A dictionary of string and [Inject](https://esmerald.dev/dependencies/) instances enable application level dependency injection.
                """
        ),
    ] = None,
    exception_handlers: Annotated[
        Optional["ExceptionHandlerMap"],
        Doc(
            """
                A dictionary of [exception types](https://esmerald.dev/exceptions/) (or custom exceptions) and the handler functions on an application top level. Exception handler callables should be of the form of `handler(request, exc) -> response` and may be be either standard functions, or async functions.
                """
        ),
    ] = None,
    middleware: Annotated[
        Optional[List["Middleware"]],
        Doc(
            """
                A list of middleware to run for every request. The middlewares of an Include will be checked from top-down or [Lilya Middleware](https://www.lilya.dev/middleware/) as they are both converted internally. Read more about [Python Protocols](https://peps.python.org/pep-0544/).
                """
        ),
    ] = None,
    permissions: Annotated[
        Optional[List["Permission"]],
        Doc(
            """
                A list of [permissions](https://esmerald.dev/permissions/) to serve the application incoming requests (HTTP and Websockets).
                """
        ),
    ] = None,
    media_type: Annotated[
        Union[MediaType, str],
        Doc(
            """
                The default `media-type` used by the handler.
                """
        ),
    ] = MediaType.JSON,
    response_class: Annotated[
        Optional["ResponseType"],
        Doc(
            """
                Response class to be used within the
                handler application.

                Read more about the [Responses](https://esmerald.dev/responses/) and how
                to use them.

                **Example**

                ```python
                from esmerald import route, JSONResponse

                @route(response_class=JSONResponse)
                ```
                """
        ),
    ] = None,
    response_cookies: Annotated[
        Optional["ResponseCookies"],
        Doc(
            """
                A sequence of `esmerald.datastructures.Cookie` objects.

                Read more about the [Cookies](https://esmerald.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

                **Example**

                ```python
                from esmerald import route
                from esmerald.datastructures import Cookie

                response_cookies=[
                    Cookie(
                        key="csrf",
                        value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                        max_age=3000,
                        httponly=True,
                    )
                ]

                @route(response_cookies=response_cookies)
                ```
                """
        ),
    ] = None,
    response_headers: Annotated[
        Optional["ResponseHeaders"],
        Doc(
            """
                A mapping of `esmerald.datastructures.ResponseHeader` objects.

                Read more about the [ResponseHeader](https://esmerald.dev/extras/header-fields/#response-headers).

                **Example**

                ```python
                from esmerald import route
                from esmerald.datastructures import ResponseHeader

                response_headers={
                    "authorize": ResponseHeader(value="granted")
                }

                @route(response_headers=response_headers)
                ```
                """
        ),
    ] = None,
    tags: Annotated[
        Optional[Sequence[str]],
        Doc(
            """
                A list of strings tags to be applied to the *path operation*.

                It will be added to the generated OpenAPI documentation.

                **Note** almost everything in Esmerald can be done in [levels](https://esmerald.dev/application/levels/), which means
                these tags on a Esmerald instance, means it will be added to every route even
                if those routes also contain tags.

                **Example**

                ```python
                from esmerald import route

                @route(tags=["application"])
                ```
                """
        ),
    ] = None,
    deprecated: Annotated[
        Optional[bool],
        Doc(
            """
                Boolean flag indicating if the handler
                should be deprecated in the OpenAPI documentation.

                **Example**

                ```python
                from esmerald import route

                @route(deprecated=True)
                ```
                """
        ),
    ] = None,
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

                **Example**

                ```python
                from esmerald import route
                from esmerald.openapi.security.http import Bearer

                @route(security=[Bearer()])
                ```
                """
        ),
    ] = None,
    operation_id: Annotated[
        Optional[str],
        Doc(
            """
                The unique identifier of the `handler`. This acts as a unique ID
                for the OpenAPI documentation.

                !!! Tip
                    Usually you don't need this as Esmerald handles it automatically
                    but it is here if you want to add your own.
                """
        ),
    ] = None,
    response_description: Annotated[
        Optional[str],
        Doc(
            """
                A description of the response. This is used for OpenAPI documentation
                purposes only and accepts all the docstrings including `markdown` format.
                """
        ),
    ] = SUCCESSFUL_RESPONSE,
    responses: Annotated[
        Optional[Dict[int, OpenAPIResponse]],
        Doc(
            """
                Additional responses that are handled by the handler and need to be described
                in the OpenAPI documentation.

                The `responses` is a dictionary like object where the first parameter is an
                `integer` and the second is an instance of an [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object.


                Read more about [OpenAPIResponse](https://esmerald.dev/responses/#openapi-responses) object and how to use it.


                **Example**

                ```python
                from esmerald import route
                from esmerald.openapi.datastructures import OpenAPIResponse
                from pydantic import BaseModel

                class Power(BaseModel):
                    name: str
                    description: str


                class Error(BaseModel):
                    detail: str


                @route(path='/read', responses={
                        200: OpenAPIResponse(model=Power, description=...)
                        400: OpenAPIResponse(model=Error, description=...)
                    }
                )
                async def operate() -> Union[None, ItemOut]:
                    ...
                ```
                """
        ),
    ] = None,
) -> WebhookHandler:
    """
    Handler responsible for allowing multiple HTTP verbs in one go
    all of its operatations.

    **Example**

    ```python
    from esmerald import route


    @route(methods=["GET", "POST", "DELETE"])
    async def operate() -> str:
        return "Hello, World!"
    ```
    """
    if not methods or not isinstance(methods, list):
        raise ImproperlyConfigured(
            "http handler demands `methods` to be declared. "
            "An example would be: @route(methods=['GET', 'PUT'])."
        )

    for method in methods:
        if method.upper() not in AVAILABLE_METHODS:
            raise ImproperlyConfigured(
                f"Invalid method {method}. " "An example would be: @route(methods=['GET', 'PUT'])."
            )

    methods = [method.upper() for method in methods]
    if not status_code:  # pragma: no cover
        status_code = status.HTTP_200_OK

    def wrapper(func: Any) -> WebhookHandler:
        handler = WebhookHandler(
            path=path,
            methods=methods,
            summary=summary,
            description=description,
            status_code=status_code,
            content_encoding=content_encoding,
            content_media_type=content_media_type,
            include_in_schema=include_in_schema,
            background=background,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
            media_type=media_type,
            response_class=response_class,
            response_cookies=response_cookies,
            response_headers=response_headers,
            tags=tags,
            deprecated=deprecated,
            security=security,
            operation_id=operation_id,
            response_description=response_description,
            responses=responses,
        )

        handler.fn = func
        handler.handler = func
        handler.__type__ = HttpMethod.OPTIONS.value
        handler.validate_handler()
        return handler

    return cast(WebhookHandler, wrapper)
