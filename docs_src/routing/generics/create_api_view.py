from esmerald import patch, post, put
from esmerald.routing.apis.generics import CreateAPIView


class UserAPI(CreateAPIView):
    """
    CreateAPIView only allows the `post`, `put` and `patch`
    to be used by default.
    """

    @post()
    def post(self) -> str:
        ...

    @put()
    def put(self) -> str:
        ...

    @patch()
    def patch(self) -> str:
        ...
