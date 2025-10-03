from ravyn import Ravyn, Gateway, JSONResponse, Request, get


@get()
async def user(request: Request) -> JSONResponse:
    return JSONResponse({"app_name": request.app.settings.app_name})


app = Ravyn(routes=[Gateway(handler=user)])
