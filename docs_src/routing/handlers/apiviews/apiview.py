from ravyn.permissions import DenyAll, IsAuthenticated
from ravyn.requests import Request
from ravyn.responses import JSONResponse
from ravyn.routing.controllers.views import APIView
from ravyn.routing.handlers import delete, get, post


class UserAPIView(APIView):
    path = "/users"
    permissions = [IsAuthenticated]

    @get(path="/")
    async def all_users(self, request: Request) -> JSONResponse:
        # logic to get all users here
        users = ...

        return JSONResponse({"users": users})

    @get(path="/deny", permissions=[DenyAll], description="API description")
    async def all_usersa(self, request: Request) -> JSONResponse: ...

    @get(path="/allow")
    async def all_usersb(self, request: Request) -> JSONResponse:
        users = ...
        return JSONResponse({"Total Users": users.count()})

    @post(path="/create")
    async def create_user(self, request: Request) -> None:
        # logic to create a user goes here
        ...

    @delete(path="/delete/{user_id}")
    async def delete_user(self, request: Request, user_id: str) -> None:
        # logic to delete a user goes here
        ...
