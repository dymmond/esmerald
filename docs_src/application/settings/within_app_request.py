from esmerald import Esmerald, Gateway, Request, get


@get()
async def app_name(request: Request) -> dict:
    settings = request.app.settings
    return {"app_name": settings.app_name}


app = Esmerald(routes=[Gateway(handler=app_name)])
