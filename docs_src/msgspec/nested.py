from typing import Union

import msgspec
from typing_extensions import Annotated

from esmerald import Esmerald, Gateway, post
from esmerald.core.datastructures.msgspec import Struct

Name = Annotated[str, msgspec.Meta(min_length=5)]
Email = Annotated[str, msgspec.Meta(min_length=5, max_length=100, pattern="[^@]+@[^@]+\\.[^@]+")]
PostCode = Annotated[str, msgspec.Meta(min_length=5)]


class Address(Struct):
    post_code: PostCode
    street_address: Union[str, None] = None


class User(Struct):
    name: Name
    email: Union[Email, None] = None
    address: Address


@post()
def create(data: User) -> User:
    """
    Returns the same payload sent to the API.
    """
    return data


app = Esmerald(routes=[Gateway(handler=create)])
