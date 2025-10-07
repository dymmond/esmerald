import warnings
from typing import Any

from ravyn.routing.controllers._metaclasses import ListAPIMeta, SimpleAPIMeta
from ravyn.routing.controllers._mixins import MethodMixin
from ravyn.routing.controllers.base import BaseController, View


class SimpleAPIView(View, MethodMixin, metaclass=SimpleAPIMeta):
    """The Ravyn SimpleAPIView class.

    This class has the same available parameters as the parent,
    `View`.

    **Example**

    ```python
    from ravyn import SimpleAPIView, delete, get, patch, post, put


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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "SimpleAPIView is deprecated and will be removed in the release 0.4.0. "
            "Please use SimpleAPIController instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class SimpleAPIController(BaseController, MethodMixin, metaclass=SimpleAPIMeta):
    """The Ravyn SimpleAPIController class.

    This class has the same available parameters as the parent,
    `View`.

    **Example**

    ```python
    from ravyn import SimpleAPIController, delete, get, patch, post, put


    class UserAPI(SimpleAPIController):
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

    ...


class ListView(View, MethodMixin, metaclass=ListAPIMeta):
    """
    Base API for views returning lists.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "ListView is deprecated and will be removed in the release 0.4.0. "
            "Please use ListAPIController instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class ListController(BaseController, MethodMixin, metaclass=ListAPIMeta):
    """
    Base API for controllers returning lists.
    """

    ...


class APIView(View):
    """The Ravyn APIView class.

    The parameters available are the ones provided by the parent,
    `View` class.

    **Example**

    ```python
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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "APIView is deprecated and will be removed in the release 0.4.0. "
            "Please use APIController instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class Controller(BaseController):
    """The Ravyn Controller class.

    **This is a drop-in replacement for the `APIView` class.**

    The parameters available are the ones provided by the parent,
    `View` class.

    **Example**

    ```python
    from ravyn.permissions import DenyAll, IsAuthenticated
    from ravyn.requests import Request
    from ravyn.responses import JSONResponse
    from ravyn.routing.controllers.views import Controller
    from ravyn.routing.handlers import delete, get, post


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
