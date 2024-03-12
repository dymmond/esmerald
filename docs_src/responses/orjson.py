from esmerald import APIView, Esmerald, Gateway, Request, get, post, status
from esmerald.datastructures.encoders import OrJSON


class World(APIView):
    @get(path="/{url}")
    async def home(self, request: Request, url: str) -> OrJSON:
        return OrJSON(content=f"URL: {url}")

    @post(path="/{url}", status_code=status.HTTP_201_CREATED)
    async def mars(self, request: Request, url: str) -> OrJSON: ...


app = Esmerald(routes=[Gateway("/world", handler=World)])
