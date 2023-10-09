from typing import List

from esmerald import get, patch, post, put
from esmerald.routing.apis.generics import CreateAPIView


class UserAPI(CreateAPIView):
    """
    ImproperlyConfigured will be raised as the handler `post()`
    name does not match the function name `post`.
    """

    @post()
    def get(self) -> str:
        ...
