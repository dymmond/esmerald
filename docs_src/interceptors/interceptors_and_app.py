from ravyn import Ravyn, Gateway, JSONResponse, get

from .myapp.interceptors import RequestParamInterceptor


@get("/home")
async def home() -> JSONResponse:
    return JSONResponse({"message": "Welcome home"})


app = Ravyn(
    routes=[Gateway(handler=home)],
    interceptors=[RequestParamInterceptor],
)
