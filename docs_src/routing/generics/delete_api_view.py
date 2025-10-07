from ravyn import delete
from ravyn.routing.controllers.generics import DeleteAPIController


class UserAPI(DeleteAPIController):
    """
    DeleteAPIController only allows the `delete` to be used by default.
    """

    @delete()
    async def delete(self) -> None: ...
