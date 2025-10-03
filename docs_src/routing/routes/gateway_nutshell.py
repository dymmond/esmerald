from ravyn import Ravyn, Gateway, Request, get


@get()
async def homepage(request: Request) -> str:
    return "Hello, home!"


app = Ravyn(routes=[Gateway(handler=homepage)])
