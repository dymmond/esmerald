from esmerald import Esmerald, Gateway, Request, UJSONResponse, get
from esmerald.datastructures import State


@get()
async def user(request: Request) -> UJSONResponse:
    return UJSONResponse({"admin_email": request.app.state["ADMIN_EMAIL"]})


app = Esmerald(routes=[Gateway(handler=user)])
app.state = State({"ADMIN_EMAIL": "admin@example.com"})
