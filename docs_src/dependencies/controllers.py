from typing import List

from ravyn import get
from ravyn.openapi.datastructures import OpenAPIResponse


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
async def users(user_dao: UserDAO) -> List[UserOut]:
    """
    Lists all the users in the system.
    """
    return await user_dao.get_all()
