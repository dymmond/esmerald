from abc import ABC, abstractmethod
from http.cookies import SimpleCookie
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Iterable,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)

from lilya._internal._message import Address as Address  # noqa
from lilya.datastructures import (
    URL as URL,  # noqa: F401
    DataUpload as LilyaUploadFile,  # noqa
    FormData as FormData,  # noqa
    Header as Header,  # noqa
    QueryParam as QueryParam,  # noqa
    Secret as Secret,  # noqa
    State as State,  # noqa
    URLPath as URLPath,  # noqa
)
from lilya.responses import Response as LilyaResponse  # noqa
from pydantic import BaseModel, ConfigDict, field_validator  # noqa
from pydantic._internal._schema_generation_shared import (  # noqa
    GetJsonSchemaHandler as GetJsonSchemaHandler,
)
from pydantic.json_schema import JsonSchemaValue as JsonSchemaValue
from pydantic_core.core_schema import (
    CoreSchema,
    with_info_plain_validator_function as general_plain_validator_function,
)
from typing_extensions import Literal

from esmerald.background import BackgroundTask, BackgroundTasks  # noqa
from esmerald.utils.enums import MediaType

R = TypeVar("R", bound=LilyaResponse)

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.applications import Esmerald


class UploadFile(LilyaUploadFile):  # pragma: no cover
    """
    Adding pydantic specific functionality for parsing.
    """

    @classmethod
    def __get_validators__(cls: Type["UploadFile"]) -> Iterable[Callable[..., Any]]:
        yield cls.validate

    @classmethod
    def validate(cls: Type["UploadFile"], v: Any) -> Any:
        if not isinstance(v, LilyaUploadFile):
            raise ValueError(f"Expected UploadFile, got: {type(v)}")
        return v

    @classmethod
    def _validate(cls, __input_value: Any, _: Any) -> "UploadFile":
        if not isinstance(__input_value, LilyaUploadFile):
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
        return general_plain_validator_function(cls._validate)


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
    headers: dict[str, Any] = {}
    cookies: list[Cookie] = []
    status_code: Optional[int] = None

    @abstractmethod
    def to_response(
        self,
        headers: dict[str, Any],
        media_type: Union["MediaType", str],
        status_code: int,
        app: Type["Esmerald"],
    ) -> R:  # pragma: no cover
        raise NotImplementedError("not implemented")


class ResponseHeader(BaseModel):
    value: Optional[Any] = None

    @field_validator("value")  # type: ignore
    def validate_value(cls, value: Any, values: dict[str, Any]) -> Any:
        if value is not None:
            return value
