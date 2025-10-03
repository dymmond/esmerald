from typing import Union

import msgspec
from typing_extensions import Annotated

from ravyn import Ravyn, Gateway, post
from ravyn.core.datastructures.msgspec import Struct

Name = Annotated[str, msgspec.Meta(min_length=5)]
Email = Annotated[str, msgspec.Meta(min_length=5, max_length=100, pattern="[^@]+@[^@]+\\.[^@]+")]


class User(Struct):
    name: Name
    email: Union[Email, None] = None


@post()
def create(data: User) -> User:
    """
    Returns the same payload sent to the API.
    """
    return data


app = Ravyn(routes=[Gateway(handler=create)])
