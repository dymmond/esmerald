from typing import List, Union

from pydantic import BaseModel

from esmerald import Esmerald, Gateway, post
from esmerald.core.datastructures.msgspec import Struct
from esmerald.openapi.datastructures import OpenAPIResponse


class ErrorDetail(Struct):
    detail: str
    code: int


class Error(BaseModel):
    errors: List[ErrorDetail]


class User(Struct):
    name: str
    email: Union[str, None] = None


@post(
    summary="Creates a user in the system",
    responses={
        400: OpenAPIResponse(model=Error),
    },
)
def create(data: User) -> User:
    """
    Returns the same payload sent to the API.
    """
    return data


app = Esmerald(routes=[Gateway(handler=create)])
