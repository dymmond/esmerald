from typing import Union

from ravyn import Ravyn, Gateway, post
from ravyn.core.datastructures.msgspec import Struct


class User(Struct):
    name: str
    email: Union[str, None] = None


@post()
def create(data: User) -> User:
    """
    Returns the same payload sent to the API.
    """
    return data


app = Ravyn(routes=[Gateway(handler=create)])
