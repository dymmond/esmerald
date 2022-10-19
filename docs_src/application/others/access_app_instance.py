from esmerald import Esmerald, Gateway, Request, UJSONResponse, get


@get()
async def user(request: Request) -> UJSONResponse:
    return UJSONResponse({"app_name": request.app.settings.app_name})


app = Esmerald(routes=[Gateway(handler=user)])
