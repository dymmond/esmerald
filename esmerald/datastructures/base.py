from abc import ABC, abstractmethod
from copy import copy
from http.cookies import SimpleCookie
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)

from pydantic import BaseModel, ConfigDict, field_validator  # noqa
from pydantic._internal._schema_generation_shared import (
    GetJsonSchemaHandler as GetJsonSchemaHandler,
)
from pydantic.json_schema import JsonSchemaValue as JsonSchemaValue
from pydantic_core.core_schema import CoreSchema, PlainValidatorFunctionSchema
from pydantic_core.core_schema import (
    with_info_plain_validator_function as general_plain_validator_function,
)
from starlette.datastructures import URL as URL  # noqa: F401
from starlette.datastructures import Address as Address  # noqa: F401
from starlette.datastructures import FormData as FormData  # noqa: F401
from starlette.datastructures import Headers as Headers  # noqa: F401
from starlette.datastructures import MutableHeaders as MutableHeaders  # noqa
from starlette.datastructures import QueryParams as QueryParams  # noqa: F401
from starlette.datastructures import Secret as StarletteSecret  # noqa
from starlette.datastructures import State as StarletteStateClass  # noqa: F401
from starlette.datastructures import UploadFile as StarletteUploadFile  # noqa
from starlette.datastructures import URLPath as URLPath  # noqa: F401
from starlette.responses import Response as StarletteResponse  # noqa
from typing_extensions import Literal

from esmerald.backgound import BackgroundTask, BackgroundTasks  # noqa
from esmerald.enums import MediaType

R = TypeVar("R", bound=StarletteResponse)

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.applications import Esmerald


class UploadFile(StarletteUploadFile):  # pragma: no cover
    """
    Adding pydantic specific functionalitty for parsing.
    """

    @classmethod
    def __get_validators__(cls: Type["UploadFile"]) -> Iterable[Callable[..., Any]]:
        yield cls.validate

    @classmethod
    def validate(cls: Type["UploadFile"], v: Any) -> Any:
        if not isinstance(v, StarletteUploadFile):
            raise ValueError(f"Expected UploadFile, got: {type(v)}")
        return v

    @classmethod
    def _validate(cls, __input_value: Any, _: Any) -> "UploadFile":
        if not isinstance(__input_value, StarletteUploadFile):
            raise ValueError(f"Expected UploadFile, got: {type(__input_value)}")
        return cast(UploadFile, __input_value)

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return {"type": "string", "format": "binary"}

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Type[Any], handler: Callable[[Any], CoreSchema]
    ) -> CoreSchema:
        return cast(PlainValidatorFunctionSchema, general_plain_validator_function(cls._validate))


class Secret(StarletteSecret):  # pragma: no cover
    def __len__(self) -> int:
        return len(self._value)


class State(StarletteStateClass):  # pragma: no cover
    state: Dict[str, Any]

    def __copy__(self) -> "State":
        return self.__class__(copy(self._state))

    def __len__(self) -> int:
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
        cookie_dict = self.model_dump()
        for key in ["expires", "path", "domain", "secure", "httponly", "samesite"]:
            if cookie_dict[key] is not None:
                simple_cookie[self.key][key] = cookie_dict[key]
        return simple_cookie.output(**kwargs).strip()


class ResponseContainer(BaseModel, ABC, Generic[R]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    background: Optional[Union[BackgroundTask, BackgroundTasks]] = None
    headers: Dict[str, Any] = {}
    cookies: List[Cookie] = []

    @abstractmethod
    def to_response(
        self,
        headers: Dict[str, Any],
        media_type: Union["MediaType", str],
        status_code: int,
        app: Type["Esmerald"],
    ) -> R:  # pragma: no cover
        raise NotImplementedError("not implemented")


class ResponseHeader(BaseModel):
    value: Optional[Any] = None

    @field_validator("value")  # type: ignore
    def validate_value(cls, value: Any, values: Dict[str, Any]) -> Any:
        if value is not None:
            return value
