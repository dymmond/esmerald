from typing import TYPE_CHECKING, Union

from lilya.context import Context as LilyaContext
from typing_extensions import Annotated, Doc

if TYPE_CHECKING:
    from esmerald import Request
    from esmerald.routing.router import HTTPHandler, WebSocketHandler


class Context(LilyaContext):
    """
    `Context` class is used for the handlers context of the
    scope of the call.

    When a `context` is passed through the handler,
    the context will be aware of the decoractor handler
    itself.

    You will probably not need the context or change it but it is here in
    case you decide to use it.

    !!! Tip
        The context only exists in the handlers and nothing else which you can also
        see it as `request context` sort of approach.

    **Example**

    ```python
    from esmerald import Esmerald, Context, get


    @get()
    async def home(context: Context) -> None:
        ...
    ```
    """

    def __init__(
        self,
        __handler__: Annotated[
            Union["HTTPHandler", "WebSocketHandler"],
            Doc(
                """
                The [handler](https://esmerald.dev/routing/handlers/) where the context will be. placed.

                To avoid any adulteration of the the original route handler, the context performs
                a shallow copy of the original handler itself.
                """
            ),
        ],
        __request__: Annotated[
            "Request",
            Doc(
                """
                A [Request](https://esmerald.dev/references/request/) class object.
                """
            ),
        ],
    ) -> None:
        super().__init__(__handler__, __request__)
