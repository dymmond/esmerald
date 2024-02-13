from typing import List

from esmerald import get, patch, post, put
from esmerald.routing.apis.generics import ListAPIView


class UserAPI(ListAPIView):
    extra_allowed: List[str] = ["read_item"]

    @post()
    async def post(self) -> List[str]: ...

    @put()
    async def put(self) -> List[str]: ...

    @patch()
    async def patch(self) -> List[str]: ...

    @get()
    async def read_item(self) -> List[str]: ...
