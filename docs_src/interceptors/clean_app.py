from ravyn import Ravyn, Gateway, JSONResponse, get


@get("/home")
async def home() -> JSONResponse:
    return JSONResponse({"message": "Welcome home"})


app = Ravyn(routes=[Gateway(handler=home)])
