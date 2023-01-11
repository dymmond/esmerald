from esmerald import Esmerald, Gateway, JSONResponse, get

from .myapp.interceptors import CookieInterceptor, RequestParamInterceptor


@get("/home")
async def home() -> JSONResponse:
    return JSONResponse({"message": "Welcome home"})


app = Esmerald(
    routes=[Gateway(handler=home, interceptors=[CookieInterceptor])],
    interceptors=[RequestParamInterceptor],
)
