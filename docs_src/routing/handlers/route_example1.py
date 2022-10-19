from esmerald import Esmerald, Gateway, Request, UJSONResponse, route


@route(methods=["GET", "POST", "PUT"])
async def multiple_methods_function(request: Request) -> UJSONResponse:
    method = request.method.upper()

    if method == "GET":
        return UJSONResponse({"message": "I'm a GET!"})
    elif method == "PUT":
        return UJSONResponse({"message": "I'm a PUT!"})
    return UJSONResponse({"message": "I'm a POST!"})


app = Esmerald(
    routes=[
        Gateway(handler=multiple_methods_function),
    ]
)
