from ravyn import delete, get, patch, post, put
from ravyn.routing.apis.generics import CreateAPIView, DeleteAPIView, ReadAPIView


class UserAPI(CreateAPIView, DeleteAPIView, ReadAPIView):
    """
    Combining them all.
    """

    @get()
    async def get(self) -> str: ...

    @post()
    async def post(self) -> str: ...

    @put()
    async def put(self) -> str: ...

    @patch()
    async def patch(self) -> str: ...

    @delete()
    async def delete(self) -> None: ...
