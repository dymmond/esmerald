from ravyn import Ravyn, Gateway, Include, Request, get


@get("/me")
async def me(request: Request) -> str:
    return "Hello, world!"


app = Ravyn(routes=[Include("/", routes=[Gateway(handler=me)])])
