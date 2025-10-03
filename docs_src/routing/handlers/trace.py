from ravyn import Ravyn, Gateway, JSONResponse, Request, trace


@trace()
async def example(request: Request) -> JSONResponse:
    return JSONResponse({"message": "Welcome home!"})


@trace(path="/another")
def another() -> str:
    return "Another welcome!"


@trace(path="/")
def another_read(name: str) -> str:
    return f"Another welcome, {name}!"


app = Ravyn(
    routes=[
        Gateway(handler=example),
        Gateway(handler=another),
        Gateway(path="/last/{name:str}", handler=another_read),
    ]
)
