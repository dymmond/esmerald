from esmerald import Esmerald, Gateway, JSONResponse, Request, get


@get()
async def example(request: Request) -> JSONResponse:
    return JSONResponse({"message": "Welcome home!"})


@get(path="/another")
def another() -> str:
    return "Another welcome!"


@get(path="/")
def another_read(name: str) -> str:
    return f"Another welcome, {name}!"


app = Esmerald(
    routes=[
        Gateway(handler=example),
        # you can the handlers also directly (they are automatically converted to Gateways)
        another,
        Gateway(path="/last/{name:str}", handler=another_read),
    ]
)
