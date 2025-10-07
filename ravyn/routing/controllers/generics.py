import warnings
from typing import Any, ClassVar

from typing_extensions import Annotated, Doc

from ravyn.routing.controllers.views import (
    ListController,
    ListView,
    SimpleAPIController,
    SimpleAPIView,
)


class GenericMixin:
    __is_generic__: ClassVar[bool] = True


class CreateAPIView(GenericMixin, SimpleAPIView):
    """
    This class has the same available parameters as the parent,
    `View` but subclassing the `SimpleAPIView`.

    ```python
    from ravyn.routing.controllers.generics import CreateAPIView
    ```

    **Example**

    ```python
    from ravyn import patch, post, put
    from ravyn.routing.controllers.generics import CreateAPIView


    class UserAPI(CreateAPIView):
        '''
        CreateAPIView only allows the `post`, `put` and `patch`
        to be used by default.
        '''

        @post()
        async def post(self) -> str:
            ...

        @put()
        async def put(self) -> str:
            ...

        @patch()
        async def patch(self) -> str:
        ...
    ```
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "CreateAPIView is deprecated and will be removed in the release 0.4.0. "
            "Please use CreateAPIController instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)

    http_allowed_methods: Annotated[
        list[str],
        Doc(
            """
            Allowed methods for the given base class.
            """
        ),
    ] = ["post", "put", "patch"]


class CreateAPIController(GenericMixin, SimpleAPIController):
    """
    This class has the same available parameters as the parent,
    `View` but subclassing the `SimpleAPIController`.

    ```python
    from ravyn.routing.controllers.generics import CreateAPIController
    ```

    **Example**

    ```python
    from ravyn import patch, post, put
    from ravyn.routing.controllers.generics import CreateAPIController


    class UserAPI(CreateAPIController):
        '''
        CreateAPIController only allows the `post`, `put` and `patch`
        to be used by default.
        '''

        @post()
        async def post(self) -> str:
            ...

        @put()
        async def put(self) -> str:
            ...

        @patch()
        async def patch(self) -> str:
        ...
    ```
    """

    http_allowed_methods: Annotated[
        list[str],
        Doc(
            """
            Allowed methods for the given base class.
            """
        ),
    ] = ["post", "put", "patch"]


class DeleteAPIView(GenericMixin, SimpleAPIView):
    """
    This class has the same available parameters as the parent,
    `View` but subclassing the `SimpleAPIView`.

    ```python
    from ravyn.routing.controllers.generics import CreateAPIView
    ```

    **Example**

    ```python
    from ravyn import delete
    from ravyn.routing.controllers.generics import DeleteAPIView


    class UserAPI(DeleteAPIView):
        '''
        DeleteAPIView only allows the `delete` to be used by default.
        '''

        @delete()
        async def delete(self) -> None:
            ...
    ```
    """

    http_allowed_methods: Annotated[
        list[str],
        Doc(
            """
            Allowed methods for the given base class.
            """
        ),
    ] = ["delete"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "DeleteAPIView is deprecated and will be removed in the release 0.4.0. "
            "Please use DeleteAPIController instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class DeleteAPIController(GenericMixin, SimpleAPIController):
    """
    This class has the same available parameters as the parent,
    `View` but subclassing the `SimpleAPIController`.

    ```python
    from ravyn.routing.controllers.generics import DeleteAPIController
    ```

    **Example**

    ```python
    from ravyn import delete
    from ravyn.routing.controllers.generics import DeleteAPIController


    class UserAPI(DeleteAPIController):
        '''
        DeleteAPIController only allows the `delete` to be used by default.
        '''

        @delete()
        async def delete(self) -> None:
            ...
    ```
    """

    http_allowed_methods: Annotated[
        list[str],
        Doc(
            """
            Allowed methods for the given base class.
            """
        ),
    ] = ["delete"]


class ReadAPIView(GenericMixin, SimpleAPIView):
    """
    This class has the same available parameters as the parent,
    `View` but subclassing the `SimpleAPIView`.

    ```python
    from ravyn.routing.controllers.generics import ReadAPIView
    ```

    **Example**

    ```python
    from ravyn import get
    from ravyn.routing.controllers.generics import ReadAPIView


    class UserAPI(ReadAPIView):
        '''
        ReadAPIView only allows the `get` to be used by default..
        '''

        @get()
        async def get(self) -> None:
            ...
    ```
    """

    http_allowed_methods: Annotated[
        list[str],
        Doc(
            """
            Allowed methods for the given base class.
            """
        ),
    ] = ["get"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "ReadAPIView is deprecated and will be removed in the release 0.4.0. "
            "Please use ReadAPIController instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class ReadAPIController(GenericMixin, SimpleAPIController):
    """
    This class has the same available parameters as the parent,
    `View` but subclassing the `SimpleAPIController`.

    ```python
    from ravyn.routing.controllers.generics import ReadAPIController
    ```

    **Example**

    ```python
    from ravyn import get
    from ravyn.routing.controllers.generics import ReadAPIController


    class UserAPI(ReadAPIController):
        '''
        ReadAPIController only allows the `get` to be used by default..
        '''

        @get()
        async def get(self) -> None:
            ...
    ```
    """

    http_allowed_methods: Annotated[
        list[str],
        Doc(
            """
            Allowed methods for the given base class.
            """
        ),
    ] = ["get"]


class ListAPIView(GenericMixin, ListView):
    """
    Only allows the return to be lists.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        warnings.warn(
            "ListAPIView is deprecated and will be removed in the release 0.4.0. "
            "Please use ListAPIController instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


class ListAPIController(GenericMixin, ListController):
    """
    Only allows the return to be lists.
    """

    ...
