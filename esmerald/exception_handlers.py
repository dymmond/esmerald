from typing import Union

from orjson import loads
from pydantic import ValidationError
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import Response as StarletteResponse

from esmerald.enums import MediaType
from esmerald.exceptions import ExceptionErrorMap, HTTPException, ImproperlyConfigured
from esmerald.responses import JSONResponse, Response


async def http_exception_handler(
    request: Request, exc: Union[HTTPException, StarletteHTTPException]
) -> Union[JSONResponse, Response]:
    """
    Default exception handler for StarletteHTTPException and Esmerald HTTPException.
    """
    extra = getattr(exc, "extra", None)
    headers = getattr(exc, "headers", None)

    if exc.status_code in {204, 304}:
        return JSONResponse(None, status_code=exc.status_code, headers=headers)

    if headers and not extra:
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=headers)
    elif headers and extra:
        return JSONResponse(
            {"detail": exc.detail, "extra": extra},
            status_code=exc.status_code,
            headers=headers,
        )
    elif not headers and extra:
        return JSONResponse({"detail": exc.detail, "extra": extra}, status_code=exc.status_code)
    else:
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


async def validation_error_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    extra = getattr(exc, "extra", None)
    status_code = status.HTTP_400_BAD_REQUEST

    if extra:
        errors_extra = exc.extra.get("extra", {})
        return JSONResponse(
            {"detail": exc.detail, "errors": errors_extra},
            status_code=status_code,
        )
    else:
        return JSONResponse(
            {"detail": exc.detail},
            status_code=status_code,
        )


async def http_error_handler(_: Request, exc: ExceptionErrorMap) -> JSONResponse:
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


async def improperly_configured_exception_handler(
    request: Request, exc: ImproperlyConfigured
) -> StarletteResponse:
    """
    When an ImproperlyConfiguredException is raised.
    """
    status_code = (
        exc.status_code
        if isinstance(exc, StarletteHTTPException)
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    if not status_code:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    content = {"detail": exc.detail}
    if exc.extra:
        content.update({"extra": exc.extra})  # type: ignore[dict-item]
    headers = exc.headers if isinstance(exc, (HTTPException, StarletteHTTPException)) else None

    return Response(
        media_type=MediaType.JSON,
        content=content,
        status_code=status_code,
        headers=headers,
    )


async def pydantic_validation_error_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """
    This handler is to be used when a pydantic validation error is triggered during the logic
    of a code block and not the definition of a handler.

    This is different from validation_error_exception_handler
    """
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    return JSONResponse({"detail": loads(exc.json())}, status_code=status_code)


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """
    Simple handler that manages all the ValueError exceptions thrown to the user properly
    formatted.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    details = loads(exc.json()) if hasattr(exc, "json") else exc.args[0]
    return JSONResponse({"detail": details}, status_code=status_code)
