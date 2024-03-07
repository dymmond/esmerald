from http import HTTPStatus
from typing import Any, Dict, Optional, Type, Union

from lilya import status
from lilya.exceptions import (
    HTTPException as LilyaHTTPException,
    ImproperlyConfigured as ImproperlyConfigured,
    WebSocketException as LilyaWebSocketException,
)
from pydantic import BaseModel, create_model
from typing_extensions import Annotated, Doc

RequestErrorModel: Type[BaseModel] = create_model("Request")
WebSocketErrorModel: Type[BaseModel] = create_model("WebSocket")


class EsmeraldAPIException(Exception):
    def __init__(self, *args: Any, detail: str = ""):
        self.detail = detail
        super().__init__(*(str(arg) for arg in args if arg), self.detail)

    def __repr__(self) -> str:  # pragma: no cover
        if self.detail:
            return f"{self.__class__.__name__} - {self.detail}"
        return self.__class__.__name__

    def __str__(self) -> str:
        return "".join(self.args).strip()


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


class EsmeraldError(RuntimeError):
    """
    Generic exception.
    """

    ...


class ImproperlyMiddlewareConfigured(ImproperlyConfigured): ...


class NotAuthenticated(HTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Authentication credentials were not provided."


class PermissionDenied(HTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "You do not have permission to perform this action."


class ValidationErrorException(HTTPException, ValueError):
    status_code = status.HTTP_400_BAD_REQUEST


class NotAuthorized(HTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "You do not have authorization to perform this action."


class NotFound(HTTPException, ValueError):
    detail = "The resource cannot be found."
    status_code = status.HTTP_404_NOT_FOUND


class MethodNotAllowed(HTTPException):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED


class InternalServerError(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class ServiceUnavailable(HTTPException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class TemplateNotFound(InternalServerError):
    def __init__(self, *args: Any, template_name: str):
        """Template could not be found."""
        super().__init__(*args, detail=f"Template {template_name} not found.")


class MissingDependency(EsmeraldAPIException, ImportError): ...


class OpenAPIException(ImproperlyConfigured): ...


class WebSocketException(LilyaWebSocketException): ...


class AuthenticationError(HTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED


class EnvironmentError(EsmeraldAPIException): ...


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
