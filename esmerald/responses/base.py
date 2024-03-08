import dataclasses
from dataclasses import is_dataclass
from typing import TYPE_CHECKING, Any, Dict, Generic, NoReturn, Optional, TypeVar, Union, cast

import msgspec
from lilya import status
from lilya.responses import (
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
from orjson import OPT_OMIT_MICROSECONDS, OPT_SERIALIZE_NUMPY, dumps
from pydantic import BaseModel
from typing_extensions import Annotated, Doc

from esmerald.enums import MediaType
from esmerald.exceptions import ImproperlyConfigured

PlainTextResponse = PlainText

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.backgound import BackgroundTask, BackgroundTasks
    from esmerald.types import ResponseCookies

T = TypeVar("T")


class Response(LilyaResponse, Generic[T]):
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
            Optional[Union["MediaType", str]],
            Doc(
                """
                The media type used in the response.
                """
            ),
        ] = MediaType.JSON,
        background: Annotated[
            Optional[Union["BackgroundTask", "BackgroundTasks"]],
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
            Optional["ResponseCookies"],
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

                Response(response_cookies=response_cookies)
                ```
                """
            ),
        ] = None,
    ) -> None:
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers or {},
            media_type=media_type,
            background=cast("BackgroundTask", background),
        )
        self.cookies = cookies or []

    @staticmethod
    def transform(value: Any) -> Dict[str, Any]:
        """
        The transformation of the data being returned.

        It supports Pydantic models, `dataclasses` and `msgspec.Struct`.
        """
        if isinstance(value, BaseModel):
            return value.model_dump()
        if is_dataclass(value):
            return dataclasses.asdict(value)
        if isinstance(value, msgspec.Struct):
            return msgspec.structs.asdict(value)
        raise TypeError("unsupported type")  # pragma: no cover

    def make_response(self, content: Any) -> Union[bytes, str]:
        try:
            if (
                content is None
                or content is NoReturn
                and (
                    self.status_code < 100
                    or self.status_code
                    in {status.HTTP_204_NO_CONTENT, status.HTTP_304_NOT_MODIFIED}
                )
            ):
                return b""
            if self.media_type == MediaType.JSON:
                return dumps(
                    content,
                    default=self.transform,
                    option=OPT_SERIALIZE_NUMPY | OPT_OMIT_MICROSECONDS,
                )
            return super().make_response(content)
        except (AttributeError, ValueError, TypeError) as e:  # pragma: no cover
            raise ImproperlyConfigured("Unable to serialize response content") from e
