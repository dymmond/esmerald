import os
from abc import ABC, abstractmethod
from copy import copy
from http.cookies import SimpleCookie
from typing import AsyncIterable  # noqa
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    AsyncIterator,
    Callable,
    Dict,
    Generator,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)

from pydantic import BaseConfig, BaseModel, FilePath, validator  # noqa
from pydantic.generics import GenericModel  # noqa
from starlette.datastructures import URL as URL  # noqa: F401
from starlette.datastructures import Address as Address  # noqa: F401
from starlette.datastructures import FormData as FormData  # noqa: F401
from starlette.datastructures import Headers as Headers  # noqa: F401
from starlette.datastructures import MutableHeaders as MutableHeaders  # noqa
from starlette.datastructures import QueryParams as QueryParams  # noqa: F401
from starlette.datastructures import State as StarletteStateClass  # noqa: F401
from starlette.datastructures import UploadFile as UploadFile  # noqa
from starlette.datastructures import URLPath as URLPath  # noqa: F401
from starlette.responses import StreamingResponse  # noqa
from starlette.responses import FileResponse, RedirectResponse  # noqa
from starlette.responses import Response as StarletteResponse  # noqa
from typing_extensions import Literal, ParamSpec

from esmerald.backgound import BackgroundTask, BackgroundTasks  # noqa
from esmerald.exceptions import TemplateNotFound  # noqa
from esmerald.responses import JSONResponse  # noqa
from esmerald.responses import ORJSONResponse  # noqa
from esmerald.responses import TemplateResponse  # noqa
from esmerald.responses import UJSONResponse  # noqa; noqa

P = ParamSpec("P")
R = TypeVar("R", bound=StarletteResponse)

if TYPE_CHECKING:
    from esmerald.applications import Esmerald
    from esmerald.enums import MediaType


class Secret:
    def __init__(self, value: str):
        self._value = value

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}('**********')"

    def __str__(self) -> str:
        return self._value

    def __bool__(self) -> bool:
        return bool(self._value)

    def __len__(self) -> int:
        return len(self._value)


class State(StarletteStateClass):

    state: Dict[str, Any]

    def __copy__(self) -> "State":
        return self.__class__(copy(self._state))

    def __len__(self):
        return len(self._state)

    def __getattr__(self, key: str) -> Any:
        try:
            return self._state[key]
        except KeyError as e:
            raise AttributeError(f"State has no key '{key}'") from e

    def __getitem__(self, key: str) -> Any:
        return self._state[key]

    def copy(self) -> "State":
        return copy(self)


class Cookie(BaseModel):
    key: str
    value: Optional[str] = None
    max_age: Optional[int] = None
    expires: Optional[int] = None
    path: str = "/"
    domain: Optional[str] = None
    secure: Optional[bool] = None
    httponly: Optional[bool] = None
    samesite: Literal["lax", "strict", "none"] = "lax"
    description: Optional[str] = None

    def to_header(self, **kwargs: Any) -> str:
        simple_cookie: SimpleCookie = SimpleCookie()
        simple_cookie[self.key] = self.value or ""
        if self.max_age:
            simple_cookie[self.key]["max-age"] = self.max_age
        cookie_dict = self.dict()
        for key in ["expires", "path", "domain", "secure", "httponly", "samesite"]:
            if cookie_dict[key] is not None:
                simple_cookie[self.key][key] = cookie_dict[key]
        return simple_cookie.output(**kwargs).strip()


class ResponseContainer(GenericModel, ABC, Generic[R]):
    class Config(BaseConfig):
        arbitrary_types_allowed = True

    background: Optional[Union[BackgroundTask, BackgroundTasks]] = None
    headers: Dict[str, Any] = {}
    cookies: List[Cookie] = []

    @abstractmethod
    def to_response(
        self,
        headers: Dict[str, Any],
        media_type: Union["MediaType", str],
        status_code: int,
        app: "Esmerald",
    ) -> R:  # pragma: no cover
        raise NotImplementedError("not implemented")


class File(ResponseContainer[FileResponse]):
    path: FilePath
    filename: str
    stat_result: Optional[os.stat_result] = None

    @validator("stat_result", always=True)
    def validate_status_code(  # pylint: disable=no-self-argument
        cls, value: Optional[os.stat_result], values: Dict[str, Any]
    ) -> os.stat_result:
        """Set the stat_result value for the given filepath."""
        return value or os.stat(cast("str", values.get("path")))

    def to_response(
        self,
        headers: Dict[str, Any],
        media_type: Union["MediaType", str],
        status_code: int,
        app: "Esmerald",
    ) -> FileResponse:
        return FileResponse(
            background=self.background,
            filename=self.filename,
            headers=headers,
            media_type=media_type,
            path=self.path,
            stat_result=self.stat_result,
            status_code=status_code,
        )


class Redirect(ResponseContainer[RedirectResponse]):
    path: str

    def to_response(
        self,
        headers: Dict[str, Any],
        media_type: Union["MediaType", str],
        status_code: int,
        app: "Esmerald",
    ) -> RedirectResponse:

        return RedirectResponse(
            headers=headers,
            status_code=status_code,
            url=self.path,
            background=self.background,
        )


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
        app: "Esmerald",
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


class Template(ResponseContainer[TemplateResponse]):
    """
    Template allows to pass the original template name and an alternative in case of exception
    not found.

    Args:
        name: Template name
        context: The context to be passed to the template
        alternative_template: The alternative template to be rendered if the original doesn't exist.
    """

    name: str
    context: Optional[Dict[str, Any]] = None
    alternative_template: Optional[str] = None

    def to_response(
        self,
        headers: Dict[str, Any],
        media_type: Union["MediaType", str],
        status_code: int,
        app: "Esmerald",
    ) -> "TemplateResponse":
        from esmerald.exceptions import ImproperlyConfigured
        from esmerald.responses import TemplateResponse

        if not app.template_engine:
            raise ImproperlyConfigured("Template engine is not configured")

        data = {
            "background": self.background,
            "context": self.context,
            "headers": headers,
            "status_code": status_code,
            "template_engine": app.template_engine,
            "media_type": media_type,
        }
        try:
            return TemplateResponse(template_name=self.name, **data)
        except TemplateNotFound as e:
            if self.alternative_template:
                return TemplateResponse(template_name=self.alternative_template, **data)
            raise e


class JSON(ResponseContainer[JSONResponse]):
    """
    Returns a wrapper of a JSONResponse.
    """

    content: Optional[Dict[str, Any]] = None
    status_code: Optional[int] = None

    def to_response(
        self,
        headers: Dict[str, Any],
        media_type: Union["MediaType", str],
        status_code: int,
        app: "Esmerald",
    ) -> JSONResponse:
        status = self.status_code or status_code

        return JSONResponse(
            content=self.content,
            headers=headers,
            status_code=status,
            media_type=media_type,
            background=self.background,
        )


class OrJSON(JSON, ResponseContainer[ORJSONResponse]):
    ...


class UJSON(JSON, ResponseContainer[UJSONResponse]):
    ...


class ResponseHeader(BaseModel):
    value: Any = None

    @validator("value", always=True)
    def validate_value(
        cls, value: Any, values: Dict[str, Any]
    ) -> Any:  # pylint: disable=no-self-argument
        if value is not None:
            return value
