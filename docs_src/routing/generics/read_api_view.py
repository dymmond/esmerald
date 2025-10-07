from ravyn import get
from ravyn.routing.controllers.generics import ReadAPIController


class UserAPI(ReadAPIController):
    """
    ReadAPIController only allows the `get` to be used by default.
    """

    @get()
    async def get(self) -> str: ...
