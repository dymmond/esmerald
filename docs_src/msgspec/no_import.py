from typing import Union

import msgspec

from esmerald import Esmerald, Gateway, post


class User(msgspec.Struct):
    name: str
    email: Union[str, None] = None


@post()
def create(data: User) -> User:
    """
    Returns the same payload sent to the API.
    """
    return data


app = Esmerald(routes=[Gateway(handler=create)])
