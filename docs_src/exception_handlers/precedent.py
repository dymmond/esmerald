from pydantic.error_wrappers import ValidationError

from esmerald import (
    Esmerald,
    Gateway,
    Include,
    JSONResponse,
    Request,
    ValidationErrorException,
    get,
)
from lilya import status


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


async def validation_error_gateway(request: Request, exc: ValidationError) -> JSONResponse:
    extra = getattr(exc, "extra", None)
    status_code = status.HTTP_400_BAD_REQUEST

    if extra:
        return JSONResponse(
            {"detail": exc.detail, "errors": exc.extra.get("extra", {})},
            status_code=status_code,
        )
    else:
        return JSONResponse(
            {"detail": exc.detail},
            status_code=status_code,
        )


@get("/me")
async def me(request: Request) -> str:
    return "Hello, world!"


app = Esmerald(
    routes=[
        Include(
            "/",
            routes=[
                Gateway(
                    handler=me,
                    exception_handlers={
                        ValidationErrorException: validation_error_gateway,
                    },
                )
            ],
        )
    ],
    exception_handlers={
        ValidationErrorException: validation_error_exception_handler,
    },
)
