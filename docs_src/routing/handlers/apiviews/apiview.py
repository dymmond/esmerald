from esmerald.permissions import DenyAll, IsAuthenticated
from esmerald.requests import Request
from esmerald.responses import UJSONResponse
from esmerald.routing.handlers import delete, get, post
from esmerald.routing.views import APIView


class UserAPIView(APIView):
    path = "/users"
    permissions = [IsAuthenticated]

    @get(path="/")
    async def all_users(self, request: Request) -> UJSONResponse:
        # logic to get all users here
        users = ...

        return UJSONResponse({"users": users})

    @get(path="/deny", permissions=[DenyAll], description="API description")
    async def all_usersa(self, request: Request) -> UJSONResponse:
        ...

    @get(path="/allow")
    async def all_usersb(self, request: Request) -> UJSONResponse:
        users = ...
        return UJSONResponse({"Total Users": users.count()})

    @post(path="/create")
    async def create_user(self, request: Request) -> None:
        # logic to create a user goes here
        ...

    @delete(path="/delete/{user_id}")
    async def create_user(self, request: Request, user_id: str) -> None:
        # logic to delete a user goes here
        ...
