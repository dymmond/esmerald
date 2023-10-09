from typing import List

from esmerald import get, patch, post, put
from esmerald.routing.apis.generics import CreateAPIView


class UserAPI(CreateAPIView):
    """
    CreateAPIView only allows the `post`, `put` and `patch`
    to be used by default.
    """

    extra_allowed: List[str] = ["read_item"]

    @post()
    async def post(self) -> str:
        ...

    @put()
    async def put(self) -> str:
        ...

    @patch()
    async def patch(self) -> str:
        ...

    @get()
    async def read_item(self) -> str:
        ...
