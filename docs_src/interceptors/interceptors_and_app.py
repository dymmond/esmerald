from esmerald import Esmerald, Gateway, JSONResponse, get

from .myapp.interceptors import RequestParamInterceptor


@get("/home")
async def home() -> JSONResponse:
    return JSONResponse({"message": "Welcome home"})


app = Esmerald(
    routes=[Gateway(handler=home)],
    interceptors=[RequestParamInterceptor],
)
