from typing import List

from esmerald import get, patch, post, put
from esmerald.routing.apis.generics import ListAPIView


class UserAPI(ListAPIView):
    @get()
    async def get(self) -> List[str]:
        ...

    @post()
    async def post(self) -> List[str]:
        ...

    @put()
    async def put(self) -> List[str]:
        ...

    @patch()
    async def patch(self) -> List[str]:
        ...
