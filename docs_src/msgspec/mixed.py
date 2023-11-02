from typing import Union

import msgspec
from pydantic import BaseModel, EmailStr
from typing_extensions import Annotated

from esmerald import Esmerald, Gateway, post
from esmerald.datastructures.msgspec import Struct

StreetAddress = Annotated[str, msgspec.Meta(min_length=5)]
PostCode = Annotated[str, msgspec.Meta(min_length=5)]


class Address(Struct):
    post_code: PostCode
    street_address: Union[StreetAddress, None] = None


class User(BaseModel):
    name: str
    email: Union[EmailStr, None] = None
    address: Address


@post()
def create(data: User) -> User:
    """
    Returns the same payload sent to the API.
    """
    return data


app = Esmerald(routes=[Gateway(handler=create)])
