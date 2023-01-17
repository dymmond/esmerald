from http import HTTPStatus
from typing import Any, Dict, Optional, Type, Union

from pydantic import BaseModel, create_model
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.exceptions import WebSocketException

RequestErrorModel: Type[BaseModel] = create_model("Request")
WebSocketErrorModel: Type[BaseModel] = create_model("WebSocket")


class EsmeraldAPIException(Exception):
    def __init__(self, *args: Any, detail: str = ""):
        self.detail = detail
        super().__init__(*(str(arg) for arg in args if arg), self.detail)

    def __repr__(self) -> str:
        if self.detail:
            return f"{self.__class__.__name__} - {self.detail}"
        return self.__class__.__name__

    def __str__(self) -> str:
        return "".join(self.args).strip()


class HTTPException(StarletteHTTPException, EsmeraldAPIException):
    """
    Implementation of a unique exception allowing to override
    the details.
    """

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        *args: Any,
        detail: Optional[str] = None,
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None,
        **extra,
    ):
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

    def __repr__(self) -> str:
        return f"<{self.status_code}: {self.__class__.__name__} />"


class EsmeraldError(RuntimeError):
    """
    Generic exception.
    """

    ...


class ImproperlyConfigured(HTTPException, ValueError):
    ...


class ImproperlyMiddlewareConfigured(ImproperlyConfigured):
    ...


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


class MissingDependency(EsmeraldAPIException, ImportError):
    ...


class OpenAPIError(ValueError):
    ...


class WebSocketException(WebSocketException):
    ...


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
