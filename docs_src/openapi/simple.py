from typing import List

from esmerald import Request, get
from esmerald.openapi.datastructures import OpenAPIResponse
from esmerald.security.api_key import APIKeyInCookie, APIKeyInHeader, APIKeyInQuery

from .daos import UserDAO
from .schemas import Error, UserOut


@get(
    "/users",
    tags=["User"],
    description="List of all the users in the system",
    summary="Lists all users",
    responses={
        200: OpenAPIResponse(model=[UserOut]),
        400: OpenAPIResponse(model=Error, description="Bad response"),
    },
    security=[
        APIKeyInHeader(name="X_TOKEN_API"),
        APIKeyInCookie(name="X_COOKIE_API"),
        APIKeyInQuery(name="X_QUERY_API"),
    ],
)
async def users(request: Request) -> List[UserOut]:
    """
    Lists all the users in the system.
    """
    users = UserDAO()
    return await users.get_all()
