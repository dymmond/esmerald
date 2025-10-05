from ravyn import Ravyn, Gateway, JSONResponse, Request, get
from ravyn.core.datastructures import State


@get()
async def user(request: Request) -> JSONResponse:
    return JSONResponse({"admin_email": request.app.state["ADMIN_EMAIL"]})


app = Ravyn(routes=[Gateway(handler=user)])
app.state = State({"ADMIN_EMAIL": "admin@example.com"})
