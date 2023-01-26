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

from starlette.responses import StreamingResponse  # noqa

from esmerald.datastructures.base import ResponseContainer  # noqa

if TYPE_CHECKING:
    from esmerald.applications import Esmerald
    from esmerald.enums import MediaType


class Stream(ResponseContainer[StreamingResponse]):

    iterator: Union[
        Iterator[Union[str, bytes]],
        Generator[Union[str, bytes], Any, Any],
        AsyncIterator[Union[str, bytes]],
        AsyncGenerator[Union[str, bytes], Any],
        Type[Iterator[Union[str, bytes]]],
        Type[AsyncIterator[Union[str, bytes]]],
        Callable[[], AsyncGenerator[Union[str, bytes], Any]],
        Callable[[], Generator[Union[str, bytes], Any, Any]],
    ]

    def to_response(
        self,
        headers: Dict[str, Any],
        media_type: Union["MediaType", str],
        status_code: int,
        app: Type["Esmerald"],
    ) -> StreamingResponse:

        return StreamingResponse(
            background=self.background,
            content=self.iterator
            if isinstance(self.iterator, (Iterable, AsyncIterable))
            else self.iterator(),
            headers=headers,
            media_type=media_type,
            status_code=status_code,
        )
