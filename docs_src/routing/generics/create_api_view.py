from ravyn import patch, post, put
from ravyn.routing.controllers.generics import CreateAPIController


class UserAPI(CreateAPIController):
    """
    CreateAPIController only allows the `post`, `put` and `patch`
    to be used by default.
    """

    @post()
    async def post(self) -> str: ...

    @put()
    async def put(self) -> str: ...

    @patch()
    async def patch(self) -> str: ...
