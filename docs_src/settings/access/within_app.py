from ravyn import Ravyn, Gateway, Request, get


@get()
async def app_name(request: Request) -> dict:
    settings = request.app.settings
    return {"app_name": settings.app_name}


app = Ravyn(routes=[Gateway(handler=app_name)])
