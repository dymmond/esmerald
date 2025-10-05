from ravyn import APIView, Ravyn, Gateway, Request, get, post, status
from ravyn.core.datastructures.encoders import UJSON


class World(APIView):
    @get(path="/{url}")
    async def home(self, request: Request, url: str) -> UJSON:
        return UJSON(content=f"URL: {url}")

    @post(path="/{url}", status_code=status.HTTP_201_CREATED)
    async def mars(self, request: Request, url: str) -> UJSON: ...


app = Ravyn(routes=[Gateway("/world", handler=World)])
