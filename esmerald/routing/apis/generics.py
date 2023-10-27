from typing import ClassVar, List

from typing_extensions import Annotated, Doc

from esmerald.routing.apis.views import ListView, SimpleAPIView


class GenericMixin:
    __is_generic__: ClassVar[bool] = True


class CreateAPIView(GenericMixin, SimpleAPIView):
    """
    This class has the same available parameters as the parent,
    `View` but subclassing the `SimpleAPIView`.

    ```python
    from esmerald.routing.apis.generics import CreateAPIView
    ```

    **Example**

    ```python
    from esmerald import patch, post, put
    from esmerald.routing.apis.generics import CreateAPIView


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

    http_allowed_methods: Annotated[
        List[str],
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
    from esmerald.routing.apis.generics import CreateAPIView
    ```

    **Example**

    ```python
    from esmerald import delete
    from esmerald.routing.apis.generics import DeleteAPIView


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
        List[str],
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
    from esmerald.routing.apis.generics import ReadAPIView
    ```

    **Example**

    ```python
    from esmerald import get
    from esmerald.routing.apis.generics import ReadAPIView


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
        List[str],
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

    ...
