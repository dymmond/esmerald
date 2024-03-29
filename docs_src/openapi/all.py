from typing import List

from esmerald import Request, get
from esmerald.openapi.datastructures import OpenAPIResponse
from esmerald.openapi.security.api_key import APIKeyInCookie, APIKeyInHeader, APIKeyInQuery
from esmerald.openapi.security.http import Basic, Bearer, Digest
from esmerald.openapi.security.oauth2 import OAuth2
from esmerald.openapi.security.openid_connect import OpenIdConnect

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
        Basic,
        Bearer,
        Digest,
        APIKeyInHeader(name="X_TOKEN_API"),
        APIKeyInCookie(name="X_QUERY_API"),
        APIKeyInQuery(name="X_COOKIE_API"),
        OpenIdConnect(openIdConnectUrl=...),
    ],
)
async def users(request: Request) -> List[UserOut]:
    """
    Lists all the users in the system.
    """
    users = UserDAO()
    return await users.get_all()
