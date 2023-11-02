from typing import Union

from esmerald import Esmerald, Gateway, post
from esmerald.datastructures.msgspec import Struct


class User(Struct):
    name: str
    email: Union[str, None] = None


@post()
def create(data: User) -> User:
    """
    Returns the same payload sent to the API.
    """
    return data


app = Esmerald(routes=[Gateway(handler=create)])
