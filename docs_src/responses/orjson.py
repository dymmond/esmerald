from esmerald import (
    APIView,
    Esmerald,
    Gateway,
    ORJSONResponse,
    Request,
    Response,
    get,
    post,
    status,
)


class World(APIView):
    @get(path="/{url}")
    async def home(request: Request, url: str) -> ORJSONResponse:
        return Response(f"URL: {url}")

    @post(path="/{url}", status_code=status.HTTP_201_CREATED)
    async def mars(request: Request, url: str) -> ORJSONResponse:
        ...


app = Esmerald(routes=[Gateway("/world", handler=World)])
