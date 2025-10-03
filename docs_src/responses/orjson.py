from ravyn import APIView, Ravyn, Gateway, Request, get, post, status
from ravyn.core.datastructures.encoders import OrJSON


class World(APIView):
    @get(path="/{url}")
    async def home(self, request: Request, url: str) -> OrJSON:
        return OrJSON(content=f"URL: {url}")

    @post(path="/{url}", status_code=status.HTTP_201_CREATED)
    async def mars(self, request: Request, url: str) -> OrJSON: ...


app = Ravyn(routes=[Gateway("/world", handler=World)])
