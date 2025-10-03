from typing import Union

from ravyn import Ravyn, Gateway, post
from ravyn.core.datastructures.msgspec import Struct
from ravyn.openapi.datastructures import OpenAPIResponse


class ErrorDetail(Struct):
    detail: str
    code: int


class BadRequest(Struct):
    detail: str
    field: str
    code: int


class User(Struct):
    name: str
    email: Union[str, None] = None


@post(
    summary="Creates a user in the system",
    responses={
        400: OpenAPIResponse(model=ErrorDetail),
        401: OpenAPIResponse(model=BadRequest),
    },
)
def create(data: User) -> User:
    """
    Returns the same payload sent to the API.
    """
    return data


app = Ravyn(routes=[Gateway(handler=create)])
