from typing import Any, Dict, List, Union

from accounts.backends import (
    AccessToken,
    BackendAuthentication,
    RefreshAuthentication,
    RefreshToken,
    TokenAccess,
)
from accounts.middleware import AuthMiddleware
from accounts.models import User
from accounts.v1.schemas import LoginIn, UserIn, UserOut
from pydantic import BaseModel, EmailStr

from ravyn import Controller, JSONResponse, get, post, status
from ravyn.openapi.datastructures import OpenAPIResponse
from ravyn.openapi.security.http import Bearer


class UserIn(BaseModel):
    """
    Model responsible for the creation of a User.
    """

    first_name: str
    last_name: str
    email: str
    password: str
    username: str


class UserOut(BaseModel):
    """
    Representation of the list of users.
    """

    id: int
    first_name: str
    last_name: str
    email: str
    username: str
    is_staff: bool
    is_active: bool
    is_superuser: bool
    is_verified: bool


class LoginIn(BaseModel):
    """
    Details needed for a login of a user in the system.
    """

    email: EmailStr
    password: str


class ErrorDetail(BaseModel):
    """
    Used by the OpenAPI to describe the error
    exposing the details.
    """

    detail: str


class UserAPIView(Controller):
    tags: List[str] = ["User and Access"]
    security: List[Any] = [Bearer]

    @get(
        "/users",
        summary="Gets all the users",
        responses={201: OpenAPIResponse(model=[UserOut])},
        middleware=[AuthMiddleware],
    )
    async def get_all(self) -> List[UserOut]:
        return await User.query.all()

    @post(
        path="/create",
        summary="Creates a user in the system",
        responses={400: OpenAPIResponse(model=ErrorDetail)},
    )
    async def create_user(self, data: UserIn) -> None:
        """
        Creates a user in the system and returns the default 201
        status code.
        """
        user_data = data.model_dump()
        user_data.update({"is_verified": False})
        await User.query.create(**user_data)

    @post(
        path="/signin",
        summary="Login API and returns a JWT Token.",
        status_code=status.HTTP_200_OK,
        responses={
            200: OpenAPIResponse(model=TokenAccess),
            401: OpenAPIResponse(model=ErrorDetail),
        },
    )
    async def signin(self, data: LoginIn) -> JSONResponse:
        """
        Login a user and returns a JWT token, else raises ValueError
        """
        auth = BackendAuthentication(email=data.email, password=data.password)
        access_tokens: Dict[str, str] = await auth.authenticate()
        return JSONResponse(access_tokens)

    @post(
        path="/refresh-access",
        summary="Refreshes the access token",
        description="When a token expires, a new access token must be generated from the refresh token previously provided. The refresh token must be just that, a refresh and it should only return a new access token and nothing else",
        status_code=status.HTTP_200_OK,
        responses={
            200: OpenAPIResponse(model=AccessToken),
            401: OpenAPIResponse(model=ErrorDetail),
        },
    )
    async def refresh_token(self, payload: RefreshToken) -> AccessToken:
        authentication = RefreshAuthentication(token=payload)
        access_token: AccessToken = await authentication.refresh()
        return access_token
