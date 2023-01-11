from esmerald import Esmerald, Gateway, JSONResponse, get


@get("/home")
async def home() -> JSONResponse:
    return JSONResponse({"message": "Welcome home"})


app = Esmerald(routes=[Gateway(handler=home)])
