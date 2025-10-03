from ravyn import ChildRavyn, Ravyn, Gateway, Include, JSONResponse, get

from .myapp.interceptors import CookieInterceptor, RequestParamInterceptor


@get("/home")
async def home() -> JSONResponse:
    return JSONResponse({"message": "Welcome home"})


@get("/")
async def home_child() -> JSONResponse:
    return JSONResponse({"message": "Welcome home, child"})


child_ravyn = ChildRavyn(
    routes=[Gateway(handler=home_child, interceptors=[CookieInterceptor, RequestParamInterceptor])]
)

app = Ravyn(
    routes=[Include("/child", app=child_ravyn), Gateway(handler=home)],
)
