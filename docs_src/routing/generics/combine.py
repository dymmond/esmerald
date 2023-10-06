from esmerald import delete, get, patch, post, put
from esmerald.routing.apis.generics import CreateAPIView, DeleteAPIView, ReadAPIView


class UserAPI(CreateAPIView, DeleteAPIView, ReadAPIView):
    """
    Combining them all.
    """

    @get()
    def get(self) -> str:
        ...

    @post()
    def post(self) -> str:
        ...

    @put()
    def put(self) -> str:
        ...

    @patch()
    def patch(self) -> str:
        ...

    @delete()
    def delete(self) -> None:
        ...
