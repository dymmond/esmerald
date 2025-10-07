from ravyn import delete, get, patch, post, put
from ravyn.routing.controllers.generics import (
    CreateAPIController,
    DeleteAPIController,
    ReadAPIController,
)


class UserAPI(CreateAPIController, DeleteAPIController, ReadAPIController):
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
