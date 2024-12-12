from typing import List

from esmerald import Request, get
from esmerald.openapi.datastructures import OpenAPIResponse
from esmerald.security.api_key import APIKeyInCookie, APIKeyInHeader, APIKeyInQuery
from esmerald.security.http import HTTPBearer, HTTPBasic, HTTPDigest
from esmerald.security.oauth2 import OAuth2
from esmerald.security.open_id import OpenIdConnect
from esmerald.security.http import HTTPBasic

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
        HTTPBasic(),
        HTTPBearer(),
        HTTPDigest(),
        APIKeyInHeader(name="X_TOKEN_API"),
        APIKeyInCookie(name="X_QUERY_API"),
        APIKeyInQuery(name="X_COOKIE_API"),
        OpenIdConnect(openIdConnectUrl="/openid"),
        OAuth2(
            flows={
                "password": {
                    "tokenUrl": "token",
                    "scopes": {"read:users": "Read the users", "write:users": "Create users"},
                }
            },
            description="OAuth2 security scheme",
        ),
    ],
)
async def users(request: Request) -> List[UserOut]:
    """
    Lists all the users in the system.
    """
    users = UserDAO()
    return await users.get_all()
