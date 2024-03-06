from pydantic.error_wrappers import ValidationError

from esmerald import (
    HTTPException,
    ImproperlyConfigured,
    JSONResponse,
    Request,
    Response,
    ValidationErrorException,
)
from esmerald.applications import Esmerald
from esmerald.enums import MediaType
from lilya import status
from lilya.exceptions import HTTPException as StarletteHTTPException
from lilya.responses import Response as LilyaResponse


async def improperly_configured_exception_handler(
    request: Request, exc: ImproperlyConfigured
) -> LilyaResponse:
    status_code = (
        exc.status_code
        if isinstance(exc, StarletteHTTPException)
        else status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    if not status_code:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    content = {"detail": exc.detail}
    if exc.extra:
        content.update({"extra": exc.extra})
    headers = exc.headers if isinstance(exc, (HTTPException, StarletteHTTPException)) else None

    return Response(
        media_type=MediaType.JSON,
        content=content,
        status_code=status_code,
        headers=headers,
    )


async def validation_error_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    extra = getattr(exc, "extra", None)
    if extra:
        return JSONResponse(
            {"detail": exc.detail, "errors": exc.extra.get("extra", {})},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    else:
        return JSONResponse(
            {"detail": exc.detail},
            status_code=status.HTTP_400_BAD_REQUEST,
        )


app = Esmerald(
    routes=[...],
    exception_handlers={
        ImproperlyConfigured: improperly_configured_exception_handler,
        ValidationErrorException: validation_error_exception_handler,
    },
)
