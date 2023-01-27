from esmerald import Esmerald, Gateway, JSONResponse, Request, route


@route(methods=["GET", "POST", "PUT"])
async def multiple_methods_function(request: Request) -> JSONResponse:
    method = request.method.upper()

    if method == "GET":
        return JSONResponse({"message": "I'm a GET!"})
    elif method == "PUT":
        return JSONResponse({"message": "I'm a PUT!"})
    return JSONResponse({"message": "I'm a POST!"})


app = Esmerald(
    routes=[
        Gateway(handler=multiple_methods_function),
    ]
)
