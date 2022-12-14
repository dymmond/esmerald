from esmerald import Esmerald, Gateway, Request, UJSONResponse, route


@route(methods=["GET"])
async def my_route(request: Request) -> UJSONResponse:
    return UJSONResponse({"message": "Welcome home!"})


@route(path="/another", methods=["GET", "POST"])
def another_route() -> str:
    return "Another welcome!"


@route(path="/", methods=["GET", "POST", "PUT", "PATCH"])
def last_route(name: str) -> str:
    return f"Another welcome, {name}!"


@route(path="/", methods=["DELETE"])
def delete(name: str) -> str:
    return f"Another welcome, {name}!"


app = Esmerald(
    routes=[
        Gateway(handler=my_route),
        Gateway(handler=another_route),
        Gateway(path="/last/{name:str}", handler=last_route),
        Gateway(path="/delete", handler=delete),
    ]
)
