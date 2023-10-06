from typing import List

from esmerald import Request, delete, get, post, put
from esmerald.openapi.datastructures import OpenAPIResponse

from .daos import UserDAO
from .schemas import Error, UserIn, UserOut


@get(
    "/users",
    tags=["User"],
    description="List of all the users in the system",
    summary="Lists all users",
    responses={
        200: OpenAPIResponse(model=[UserOut]),
        400: OpenAPIResponse(model=Error, description="Bad response"),
    },
)
async def users(request: Request) -> List[UserOut]:
    """
    Lists all the users in the system.
    """
    users = UserDAO()
    return await users.get_all()


@get(
    "/{id}",
    tags=["User"],
    summary="Get a user",
    description="Shows the information of a user",
    responses={
        200: OpenAPIResponse(model=UserOut),
        400: OpenAPIResponse(model=Error, description="Bad response"),
    },
)
async def user(id: int) -> UserOut:
    """
    Get the information about a user
    """
    user = UserDAO()
    return await user.get(obj_id=id)


@post(
    "/create",
    tags=["User"],
    summary="Create a user",
    description="Creates a user in the system",
    responses={400: OpenAPIResponse(model=Error, description="Bad response")},
)
async def create(data: UserIn) -> None:
    """
    Creates a user in the system.
    """
    user = UserDAO()
    await user.create(**data.model_dump())


@put(
    "/{id}",
    tags=["User"],
    summary="Updates a user",
    description="Updates a user in the system",
    responses={400: OpenAPIResponse(model=Error, description="Bad response")},
)
async def update(data: UserIn, id: int) -> None:
    """
    Updates a user in the system.
    """
    user = UserDAO()
    await user.update(id, **data.model_dump())


@delete(
    "/{id}",
    summary="Delete a user",
    tags=["User"],
    description="Deletes a user from the system by ID",
    responses={
        400: OpenAPIResponse(model=Error, description="Bad response"),
    },
)
async def delete_user(id: int) -> None:
    """
    Deletes a user.
    """
    user = UserDAO()
    await user.delete(obj_id=id)
