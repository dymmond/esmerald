from esmerald import Esmerald, Gateway, JSONResponse, Request, get
from esmerald.core.datastructures import State


@get()
async def user(request: Request) -> JSONResponse:
    return JSONResponse({"admin_email": request.app.state["ADMIN_EMAIL"]})


app = Esmerald(routes=[Gateway(handler=user)])
app.state = State({"ADMIN_EMAIL": "admin@example.com"})
