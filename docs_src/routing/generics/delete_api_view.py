from esmerald import delete
from esmerald.routing.apis.generics import DeleteAPIView


class UserAPI(DeleteAPIView):
    """
    DeleteAPIView only allows the `delete` to be used by default.
    """

    @delete()
    def delete(self) -> None:
        ...
