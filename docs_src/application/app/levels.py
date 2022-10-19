from esmerald import Esmerald, Gateway, Include, Request, get


@get("/me")
async def me(request: Request) -> str:
    return "Hello, world!"


app = Esmerald(routes=[Include("/", routes=[Gateway(handler=me)])])
