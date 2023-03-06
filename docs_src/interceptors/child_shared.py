from esmerald import ChildEsmerald, Esmerald, Gateway, Include, JSONResponse, get

from .myapp.interceptors import CookieInterceptor, RequestParamInterceptor


@get("/home")
async def home() -> JSONResponse:
    return JSONResponse({"message": "Welcome home"})


@get("/")
async def home_child() -> JSONResponse:
    return JSONResponse({"message": "Welcome home, child"})


child_esmerald = ChildEsmerald(
    routes=[Gateway(handler=home_child, interceptors=[CookieInterceptor, RequestParamInterceptor])]
)

app = Esmerald(
    routes=[Include("/child", app=child_esmerald), Gateway(handler=home)],
)
