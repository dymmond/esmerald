from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional, Type, Union

from esmerald.enums import HttpMethod, MediaType
from esmerald.exceptions import HTTPException, ImproperlyConfigured
from esmerald.openapi.datastructures import ResponseSpecification
from esmerald.permissions.types import Permission
from esmerald.routing.router import HTTPHandler, WebSocketHandler
from esmerald.types import (
    BackgroundTaskType,
    Dependencies,
    ExceptionHandler,
    ExceptionHandlers,
    HTTPMethod,
    Middleware,
    ResponseCookies,
    ResponseHeaders,
    ResponseType,
)
from esmerald.utils.constants import AVAILABLE_METHODS
from starlette import status

if TYPE_CHECKING:
    from esmerald.exceptions import HTTPException
    from openapi_schemas_pydantic.v3_1_0 import SecurityRequirement


class get(HTTPHandler):
    def __init__(
        self,
        path: Optional[str] = None,
        *,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        status_code: Optional[int] = status.HTTP_200_OK,
        content_encoding: Optional[str] = None,
        content_media_type: Optional[str] = None,
        include_in_schema: bool = True,
        background: Optional["BackgroundTaskType"] = None,
        dependencies: Optional["Dependencies"] = None,
        exception_handlers: Optional[ExceptionHandlers] = None,
        permissions: Optional[List[Permission]] = None,
        middleware: Optional[List[Middleware]] = None,
        media_type: Union[MediaType, str] = MediaType.JSON,
        response_class: Optional[ResponseType] = None,
        response_cookies: Optional[ResponseCookies] = None,
        response_headers: Optional[ResponseHeaders] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
        deprecated: Optional[bool] = None,
        security: Optional[List["SecurityRequirement"]] = None,
        operation_id: Optional[str] = None,
        raise_exceptions: Optional[List[Type["HTTPException"]]] = None,
        response_description: Optional[str] = "Successful response",
        responses: Optional[Dict[int, ResponseSpecification]] = None,
    ) -> None:
        super().__init__(
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
            raise_exceptions=raise_exceptions,
            response_description=response_description,
            responses=responses,
        )


class post(HTTPHandler):
    def __init__(
        self,
        path: Optional[str] = None,
        *,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        status_code: Optional[int] = status.HTTP_201_CREATED,
        content_encoding: Optional[str] = None,
        content_media_type: Optional[str] = None,
        include_in_schema: bool = True,
        background: Optional["BackgroundTaskType"] = None,
        dependencies: Optional["Dependencies"] = None,
        exception_handlers: Optional[ExceptionHandlers] = None,
        permissions: Optional[List[Permission]] = None,
        middleware: Optional[List[Middleware]] = None,
        media_type: Union[MediaType, str] = MediaType.JSON,
        response_class: Optional[ResponseType] = None,
        response_cookies: Optional[ResponseCookies] = None,
        response_headers: Optional[ResponseHeaders] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
        deprecated: Optional[bool] = None,
        security: Optional[List["SecurityRequirement"]] = None,
        operation_id: Optional[str] = None,
        raise_exceptions: Optional[List[Type["HTTPException"]]] = None,
        response_description: Optional[str] = "Successful response",
        responses: Optional[Dict[int, ResponseSpecification]] = None,
    ) -> None:
        super().__init__(
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
            raise_exceptions=raise_exceptions,
            response_description=response_description,
            responses=responses,
        )


class put(HTTPHandler):
    def __init__(
        self,
        path: Optional[str] = None,
        *,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        status_code: Optional[int] = status.HTTP_200_OK,
        content_encoding: Optional[str] = None,
        content_media_type: Optional[str] = None,
        include_in_schema: bool = True,
        background: Optional["BackgroundTaskType"] = None,
        dependencies: Optional["Dependencies"] = None,
        exception_handlers: Optional[ExceptionHandlers] = None,
        permissions: Optional[List[Permission]] = None,
        middleware: Optional[List[Middleware]] = None,
        media_type: Union[MediaType, str] = MediaType.JSON,
        response_class: Optional[ResponseType] = None,
        response_cookies: Optional[ResponseCookies] = None,
        response_headers: Optional[ResponseHeaders] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
        deprecated: Optional[bool] = None,
        security: Optional[List["SecurityRequirement"]] = None,
        operation_id: Optional[str] = None,
        raise_exceptions: Optional[List[Type["HTTPException"]]] = None,
        response_description: Optional[str] = "Successful response",
        responses: Optional[Dict[int, ResponseSpecification]] = None,
    ) -> None:
        super().__init__(
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
            raise_exceptions=raise_exceptions,
            response_description=response_description,
            responses=responses,
        )


class patch(HTTPHandler):
    def __init__(
        self,
        path: Optional[str] = None,
        *,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        status_code: Optional[int] = status.HTTP_200_OK,
        content_encoding: Optional[str] = None,
        content_media_type: Optional[str] = None,
        include_in_schema: bool = True,
        background: Optional["BackgroundTaskType"] = None,
        dependencies: Optional["Dependencies"] = None,
        exception_handlers: Optional[ExceptionHandlers] = None,
        permissions: Optional[List[Permission]] = None,
        middleware: Optional[List[Middleware]] = None,
        media_type: Union[MediaType, str] = MediaType.JSON,
        response_class: Optional[ResponseType] = None,
        response_cookies: Optional[ResponseCookies] = None,
        response_headers: Optional[ResponseHeaders] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
        deprecated: Optional[bool] = None,
        security: Optional[List["SecurityRequirement"]] = None,
        operation_id: Optional[str] = None,
        raise_exceptions: Optional[List[Type["HTTPException"]]] = None,
        response_description: Optional[str] = "Successful response",
        responses: Optional[Dict[int, ResponseSpecification]] = None,
    ) -> None:
        super().__init__(
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
            raise_exceptions=raise_exceptions,
            response_description=response_description,
            responses=responses,
        )


class delete(HTTPHandler):
    def __init__(
        self,
        path: Optional[str] = None,
        *,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        status_code: Optional[int] = status.HTTP_204_NO_CONTENT,
        content_encoding: Optional[str] = None,
        content_media_type: Optional[str] = None,
        include_in_schema: bool = True,
        background: Optional["BackgroundTaskType"] = None,
        dependencies: Optional["Dependencies"] = None,
        exception_handlers: Optional[ExceptionHandlers] = None,
        permissions: Optional[List[Permission]] = None,
        middleware: Optional[List[Middleware]] = None,
        media_type: Union[MediaType, str] = MediaType.JSON,
        response_class: Optional[ResponseType] = None,
        response_cookies: Optional[ResponseCookies] = None,
        response_headers: Optional[ResponseHeaders] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
        deprecated: Optional[bool] = None,
        security: Optional[List["SecurityRequirement"]] = None,
        operation_id: Optional[str] = None,
        raise_exceptions: Optional[List[Type["HTTPException"]]] = None,
        response_description: Optional[str] = "Successful response",
        responses: Optional[Dict[int, ResponseSpecification]] = None,
    ) -> None:
        super().__init__(
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
            raise_exceptions=raise_exceptions,
            response_description=response_description,
            responses=responses,
        )


class route(HTTPHandler):
    def __init__(
        self,
        path: Optional[str] = None,
        *,
        methods: List["HTTPMethod"] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        status_code: Optional[int] = status.HTTP_200_OK,
        content_encoding: Optional[str] = None,
        content_media_type: Optional[str] = None,
        include_in_schema: bool = True,
        background: Optional["BackgroundTaskType"] = None,
        dependencies: Optional["Dependencies"] = None,
        exception_handlers: Optional[ExceptionHandlers] = None,
        permissions: Optional[List[Permission]] = None,
        middleware: Optional[List[Middleware]] = None,
        media_type: Union[MediaType, str] = MediaType.JSON,
        response_class: Optional[ResponseType] = None,
        response_cookies: Optional[ResponseCookies] = None,
        response_headers: Optional[ResponseHeaders] = None,
        tags: Optional[List[Union[str, Enum]]] = None,
        deprecated: Optional[bool] = None,
        security: Optional[List["SecurityRequirement"]] = None,
        operation_id: Optional[str] = None,
        raise_exceptions: Optional[List[Type["HTTPException"]]] = None,
        response_description: Optional[str] = "Successful response",
        responses: Optional[Dict[int, ResponseSpecification]] = None,
    ) -> None:
        if not methods or not isinstance(methods, list):
            raise ImproperlyConfigured(
                "http handler demands `methods` to be declared. "
                "An example would be: @route(methods=['GET', 'PUT'])."
            )

        for method in methods:
            if method.upper() not in AVAILABLE_METHODS:
                raise ImproperlyConfigured(
                    f"Invalid method {method}. "
                    "An example would be: @route(methods=['GET', 'PUT'])."
                )

        methods = [method.upper() for method in methods]
        if not status_code:
            status_code = status.HTTP_200_OK

        super().__init__(
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
            raise_exceptions=raise_exceptions,
            response_description=response_description,
            responses=responses,
        )


class websocket(WebSocketHandler):
    def __init__(
        self,
        path: Union[Optional[str], Optional[List[str]]] = None,
        *,
        dependencies: Optional["Dependencies"] = None,
        exception_handlers: Optional[Dict[Union[int, Type[Exception]], "ExceptionHandler"]] = None,
        permissions: Optional[List["Permission"]] = None,
        middleware: Optional[List["Middleware"]] = None,
    ):
        super().__init__(
            path=path,
            dependencies=dependencies,
            exception_handlers=exception_handlers,
            permissions=permissions,
            middleware=middleware,
        )
