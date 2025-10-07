from ravyn import post
from ravyn.routing.controllers.generics import CreateAPIView


class UserAPI(CreateAPIView):
    """
    ImproperlyConfigured will be raised as the handler `post()`
    name does not match the function name `post`.
    """

    @post()
    async def get(self) -> str: ...
