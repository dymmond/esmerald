from esmerald import JSONResponse, Request, get


@get(tags=["home"])
async def home(request: Request) -> JSONResponse:
    """
    Esmerald request has a `user` property that also
    comes from its origins (Lilya).

    When building an authentication middleware, it
    is recommended to inherit from the `BaseAuthMiddleware`.

    See more info here: https://esmerald.dymmond.com/middleware/middleware/?h=baseauthmiddleware#baseauthmiddleware
    """
    return JSONResponse({"message": f"hello {request.user.email}"})
