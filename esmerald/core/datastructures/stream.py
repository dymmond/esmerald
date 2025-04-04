from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    AsyncIterable,
    AsyncIterator,
    Callable,
    Dict,
    Generator,
    Iterable,
    Iterator,
    Type,
    Union,
)

from lilya.responses import StreamingResponse  # noqa
from typing_extensions import Annotated, Doc

from esmerald.core.datastructures.base import ResponseContainer  # noqa
from esmerald.utils.enums import MediaType

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.applications import Esmerald


class Stream(ResponseContainer[StreamingResponse]):
    iterator: Annotated[
        Union[
            Iterator[Union[str, bytes]],
            AsyncIterator[Union[str, bytes]],
            AsyncGenerator[Union[str, bytes], Any],
            Callable[[], AsyncGenerator[Union[str, bytes], Any]],
            Callable[[], Generator[Union[str, bytes], Any, Any]],
        ],
        Doc(
            """
            Any iterable function.
            """
        ),
    ]

    def to_response(
        self,
        headers: Dict[str, Any],
        media_type: Union["MediaType", str],
        status_code: int,
        app: Type["Esmerald"],
    ) -> StreamingResponse:  # pragma: no cover
        return StreamingResponse(
            background=self.background,
            content=(
                self.iterator
                if isinstance(self.iterator, (Iterable, AsyncIterable))
                else self.iterator()
            ),
            headers=headers,
            media_type=media_type,
            status_code=status_code,
        )
