from esmerald.routing.apis._metaclasses import ListAPIMeta, SimpleAPIMeta
from esmerald.routing.apis._mixins import MethodMixin
from esmerald.routing.apis.base import View


class SimpleAPIView(View, MethodMixin, metaclass=SimpleAPIMeta):
    """The Esmerald SimpleAPIView class.

    This class has the same available parameters as the parent,
    `View`.

    **Example**

    ```python
    from esmerald import SimpleAPIView, delete, get, patch, post, put


    class UserAPI(SimpleAPIView):
        @get()
        async def get(self) -> str:
            ...

        @post()
        async def post(self) -> str:
            ...

        @put()
        async def put(self) -> str:
            ...

        @patch()
        async def patch(self) -> str:
            ...

        @delete()
        async def delete(self) -> None:
            ...
    ```
    """


class ListView(View, MethodMixin, metaclass=ListAPIMeta):
    """
    Base API for views returning lists.
    """

    ...


class APIView(View):
    """The Esmerald APIView class.

    The parameters available are the ones provided by the parent,
    `View` class.

    **Example**

    ```python
    from esmerald.permissions import DenyAll, IsAuthenticated
    from esmerald.requests import Request
    from esmerald.responses import JSONResponse
    from esmerald.routing.apis.views import APIView
    from esmerald.routing.handlers import delete, get, post


    class UserAPIView(APIView):
        path = "/users"
        permissions = [IsAuthenticated]

        @get(path="/")
        async def all_users(self, request: Request) -> JSONResponse:
            # logic to get all users here
            users = ...

            return JSONResponse({"users": users})

        @get(path="/deny", permissions=[DenyAll], description="API description")
        async def all_usersa(self, request: Request) -> JSONResponse:
            ...

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
    ```
    """

    ...


class Controller(APIView):
    """The Esmerald Controller class.

    **This is a drop-in replacement for the `APIView` class.**

    The parameters available are the ones provided by the parent,
    `View` class.

    **Example**

    ```python
    from esmerald.permissions import DenyAll, IsAuthenticated
    from esmerald.requests import Request
    from esmerald.responses import JSONResponse
    from esmerald.routing.apis.views import Controller
    from esmerald.routing.handlers import delete, get, post


    class UserController(Controller):
        path = "/users"
        permissions = [IsAuthenticated]

        @get(path="/")
        async def all_users(self, request: Request) -> JSONResponse:
            # logic to get all users here
            users = ...

            return JSONResponse({"users": users})

        @get(path="/deny", permissions=[DenyAll], description="API description")
        async def all_usersa(self, request: Request) -> JSONResponse:
            ...

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
    ```
    """

    ...
