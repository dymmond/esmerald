from ravyn import JSONResponse, get


@get()
async def home() -> JSONResponse:
    return JSONResponse({"message": "Welcome home!"})
