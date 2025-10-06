from ravyn import Ravyn, Gateway, JSONResponse, Request, get
from ravyn.exceptions import RavynAPIException, InternalServerError, NotAuthorized


async def http_ravyn_handler(_: Request, exc: RavynAPIException) -> JSONResponse:
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


async def http_internal_server_error_handler(_: Request, exc: InternalServerError) -> JSONResponse:
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


async def http_not_authorized_handler(_: Request, exc: NotAuthorized) -> JSONResponse:
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


@get(path="/home", exception_handlers={NotAuthorized: http_not_authorized_handler})
async def homepage() -> dict:
    return {"page": "ok"}


app = Ravyn(
    routes=[
        Gateway(
            handler=homepage,
            exception_handlers={InternalServerError: http_internal_server_error_handler},
        )
    ],
    exception_handlers={RavynAPIException: http_ravyn_handler},
)
