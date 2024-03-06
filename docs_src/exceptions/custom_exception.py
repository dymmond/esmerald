from typing import Optional

from pydantic import BaseModel

from esmerald import HTTPException, JSONResponse, Request, post
from lilya import status


class PartialContentException(HTTPException):
    status_code = status.HTTP_206_PARTIAL_CONTENT
    detail = "Incomplete data."


async def validation_error_exception_handler(
    request: Request, exc: PartialContentException
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


class User(BaseModel):
    name: Optional[str]
    email: Optional[str]


@post(
    "/create",
    exception_handlers={PartialContentException: validation_error_exception_handler},
)
async def create_user(data: User):
    if not data.user:
        raise PartialContentException()
    else:
        ...
