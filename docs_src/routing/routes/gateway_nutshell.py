from esmerald import Esmerald, Gateway, Request, get


@get()
async def homepage(request: Request) -> str:
    return "Hello, home!"


app = Esmerald(routes=[Gateway(handler=homepage)])
