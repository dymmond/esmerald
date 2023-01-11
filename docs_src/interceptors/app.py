from esmerald import Esmerald, Gateway, JSONResponse, get

from .myapp.interceptors import LoggingInterceptor


@get("/home")
async def home() -> JSONResponse:
    return JSONResponse({"message": "Welcome home"})


app = Esmerald(routes=[Gateway(handler=home, interceptors=[LoggingInterceptor])])
