from esmerald import Esmerald, Gateway, JSONResponse, Request, options


@options()
async def example(request: Request) -> JSONResponse:
    return JSONResponse({"message": "Welcome home!"})


@options(path="/another")
def another() -> str:
    return "Another welcome!"


@options(path="/")
def another_read(name: str) -> str:
    return f"Another welcome, {name}!"


app = Esmerald(
    routes=[
        Gateway(handler=example),
        Gateway(handler=another),
        Gateway(path="/last/{name:str}", handler=another_read),
    ]
)
