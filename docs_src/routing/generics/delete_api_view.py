from ravyn import delete
from ravyn.routing.apis.generics import DeleteAPIView


class UserAPI(DeleteAPIView):
    """
    DeleteAPIView only allows the `delete` to be used by default.
    """

    @delete()
    async def delete(self) -> None: ...
