from http import HTTPStatus
from typing import Any, Dict, Optional, Type, Union

from lilya import status
from lilya.exceptions import (
    EnvironmentError as EnvironmentError,
    HTTPException as LilyaHTTPException,
    ImproperlyConfigured as ImproperlyConfigured,
    LilyaException as LilyaException,
    MethodNotAllowed as MethodNotAllowed,
    NotAuthorized as NotAuthorized,
    NotFound as NotFound,
    PermissionDenied as PermissionDenied,
    TemplateNotFound as TemplateNotFound,
    WebSocketException as LilyaWebSocketException,
)
from pydantic import BaseModel, create_model
from typing_extensions import Annotated, Doc

RequestErrorModel: Type[BaseModel] = create_model("Request")
WebSocketErrorModel: Type[BaseModel] = create_model("WebSocket")


class EsmeraldAPIException(LilyaException): ...


class HTTPException(LilyaHTTPException, EsmeraldAPIException):
    """
    Base of all `Esmerald` execeptions.

    !!! Tip
        For an implementation of a custom exception that you need
        to be thrown by Esmerald, it is advised to subclass `HTTPException`.
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        *args: Annotated[
            Any,
            Doc(
                """
                The args passed to the exception.
                """
            ),
        ],
        detail: Annotated[
            Optional[str],
            Doc(
                """
                A string text with the details of the error being thrown.
                """
            ),
        ] = None,
        status_code: Annotated[
            Optional[int],
            Doc(
                """
                An integer with the status code to be raised.
                """
            ),
        ] = None,
        headers: Annotated[
            Optional[Dict[str, Any]],
            Doc(
                """
                Any python dictionary containing headers.
                """
            ),
        ] = None,
        **extra: Annotated[
            Any,
            Doc(
                """
                Any extra information used by the exception.
                """
            ),
        ],
    ) -> None:
        detail = detail or getattr(self, "detail", None)
        status_code = status_code or getattr(self, "status_code", None)
        if not detail:
            detail = args[0] if args else HTTPStatus(status_code or self.status_code).phrase
            args = args[1:]
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.detail = detail
        self.headers = headers
        self.args = (f"{self.status_code}: {self.detail}", *args)
        self.extra = extra

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{self.status_code}: {self.__class__.__name__} />"


class ImproperlyMiddlewareConfigured(ImproperlyConfigured): ...


class NotAuthenticated(HTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Authentication credentials were not provided."


class ValidationErrorException(HTTPException, ValueError):
    status_code = status.HTTP_400_BAD_REQUEST


class InternalServerError(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class ServiceUnavailable(HTTPException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class MissingDependency(EsmeraldAPIException, ImportError): ...


class OpenAPIException(ImproperlyConfigured): ...


class WebSocketException(LilyaWebSocketException): ...


class AuthenticationError(HTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED


class BroadcastError(ImproperlyConfigured): ...


ExceptionErrorMap = Union[
    HTTPException,
    NotAuthenticated,
    PermissionDenied,
    NotAuthorized,
    NotFound,
    MethodNotAllowed,
    InternalServerError,
    ServiceUnavailable,
]
