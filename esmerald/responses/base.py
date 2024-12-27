from __future__ import annotations

from functools import partial
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    NoReturn,
    Optional,
    Sequence,
    TypeVar,
    Union,
    cast,
)

import orjson
from lilya import status
from lilya.responses import (
    RESPONSE_TRANSFORM_KWARGS,
    Error as Error,
    FileResponse as FileResponse,  # noqa
    HTMLResponse as HTMLResponse,  # noqa
    JSONResponse as JSONResponse,  # noqa
    Ok as Ok,
    PlainText as PlainText,  # noqa
    RedirectResponse as RedirectResponse,  # noqa
    Response as LilyaResponse,  # noqa
    StreamingResponse as StreamingResponse,  # noqa
)
from typing_extensions import Annotated, Doc

from esmerald.encoders import Encoder
from esmerald.enums import MediaType
from esmerald.exceptions import ImproperlyConfigured

from .mixins import ORJSONTransformMixin

PlainTextResponse = PlainText

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.background import BackgroundTask, BackgroundTasks
    from esmerald.types import ResponseCookies

T = TypeVar("T")


class Response(ORJSONTransformMixin, LilyaResponse, Generic[T]):
    """
    Default `Response` object from Esmerald where it can be as the
    return annotation of a [handler](https://esmerald.dev/routing/handlers/).

    Esmerakd automatically will understand what time of response is going to be
    used and parse all the details automatically.

    **Example**

    ```python
    from pydantic import BaseModel

    from esmerald import Esmerald, Gateway, Response, get
    from esmerald.datastructures import Cookie


    @get(path="/me")
    async def home() -> Response:
        return Response(
            Item(id=1, sku="sku1238"),
            headers={"SKY-HEADER": "sku-xyz"},
            cookies=[Cookie(key="sku", value="a-value")],
        )


    Esmerald(routes=[Gateway(handler=home)])
    ```
    """

    def __init__(
        self,
        content: Annotated[
            Any,
            Doc(
                """
                Any content being sent to the response.
                """
            ),
        ],
        *,
        status_code: Annotated[
            int,
            Doc(
                """
                The response status code.
                """
            ),
        ] = status.HTTP_200_OK,
        media_type: Annotated[
            Optional[Union[MediaType, str]],
            Doc(
                """
                The media type used in the response.
                """
            ),
        ] = None,
        background: Annotated[
            Optional[Union[BackgroundTask, BackgroundTasks]],
            Doc(
                """
                Any instance of a [BackgroundTask or BackgroundTasks](https://esmerald.dev/background-tasks/).
                """
            ),
        ] = None,
        headers: Annotated[
            Optional[Dict[str, Any]],
            Doc(
                """
                Any additional headers being passed to the response.
                """
            ),
        ] = None,
        cookies: Annotated[
            Optional[ResponseCookies],
            Doc(
                """
                A sequence of `esmerald.datastructures.Cookie` objects.

                Read more about the [Cookies](https://esmerald.dev/extras/cookie-fields/?h=responsecook#cookie-from-response-cookies).

                **Example**

                ```python
                from esmerald import Response
                from esmerald.datastructures import Cookie

                response_cookies=[
                    Cookie(
                        key="csrf",
                        value="CIwNZNlR4XbisJF39I8yWnWX9wX4WFoz",
                        max_age=3000,
                        httponly=True,
                    )
                ]

                Response(cookies=response_cookies)
                ```
                """
            ),
        ] = None,
        encoders: Annotated[
            Union[Sequence[Encoder], None],
            Doc(
                """
                A sequence of `esmerald.encoders.Encoder` type of objects to be used
                by the response object directly.

                **Example**

                ```python
                from esmerald import Response
                from esmerald.encoders import PydanticEncoder, MsgSpecEncoder

                response_cookies=[
                    encoders=[PydanticEncoder, MsgSpecEncoder]
                ]

                Response(cookies=response_cookies)
                ```
                """
            ),
        ] = None,
    ) -> None:
        self.cookies = cookies or []
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers or {},
            media_type=media_type,
            background=cast("BackgroundTask", background),
            encoders=encoders,
        )

    def make_response(self, content: Any) -> bytes | memoryview | str:
        if (
            content is None
            or content is NoReturn
            and (
                self.status_code < 100
                or self.status_code in {status.HTTP_204_NO_CONTENT, status.HTTP_304_NOT_MODIFIED}
            )
        ):
            return b""
        transform_kwargs = RESPONSE_TRANSFORM_KWARGS.get()
        if transform_kwargs:
            transform_kwargs = transform_kwargs.copy()
        else:
            transform_kwargs = {}
        transform_kwargs.setdefault(
            "json_encode_fn",
            partial(
                orjson.dumps,
                option=orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_OMIT_MICROSECONDS,
            ),
        )
        try:
            # switch to a special mode for MediaType.JSON (default handlers)
            if self.media_type == MediaType.JSON:
                # keep it a serialized json object
                transform_kwargs.setdefault("post_transform_fn", None)
            # otherwise use default logic of lilya striping '"'
            with self.with_transform_kwargs(transform_kwargs):
                # if content is bytes it won't be transformed and
                # if None or NoReturn, return b"", this differs from the dedicated JSONResponses.
                return super().make_response(content)
        except (AttributeError, ValueError, TypeError) as e:  # pragma: no cover
            raise ImproperlyConfigured("Unable to serialize response content") from e
