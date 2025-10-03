from typing import Union

import msgspec

from ravyn import Ravyn, Gateway, post


class User(msgspec.Struct):
    name: str
    email: Union[str, None] = None


@post()
def create(data: User) -> User:
    """
    Returns the same payload sent to the API.
    """
    return data


app = Ravyn(routes=[Gateway(handler=create)])
