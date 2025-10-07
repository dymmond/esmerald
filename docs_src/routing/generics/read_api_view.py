from ravyn import get
from ravyn.routing.controllers.generics import ReadAPIView


class UserAPI(ReadAPIView):
    """
    ReadAPIView only allows the `get` to be used by default.
    """

    @get()
    async def get(self) -> str: ...
