from esmerald import (
    APIView,
    Esmerald,
    Gateway,
    Request,
    Response,
    UJSONResponse,
    get,
    post,
    status,
)


class World(APIView):
    @get(path="/{url}")
    async def home(request: Request, url: str) -> UJSONResponse:
        return Response(f"URL: {url}")

    @post(path="/{url}", status_code=status.HTTP_201_CREATED)
    async def mars(request: Request, url: str) -> UJSONResponse:
        ...


app = Esmerald(routes=[Gateway("/world", handler=World)])
