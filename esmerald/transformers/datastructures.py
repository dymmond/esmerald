"""
Signature is widely used by Pydantic and comes from the inpect library.
A lot of great work was done using the Signature and Esmerald is no exception.
"""

from inspect import Parameter as InspectParameter
from inspect import Signature as InspectSignature
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Generator,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)

from esmerald.enums import ScopeType
from esmerald.exceptions import (
    ImproperlyConfigured,
    InternalServerError,
    ValidationErrorException,
)
from esmerald.requests import Request
from esmerald.transformers.constants import (
    CLASS_SPECIAL_WORDS,
    UNDEFINED,
    VALIDATION_NAMES,
)
from esmerald.transformers.utils import get_connection_info
from esmerald.utils.dependency import (
    is_dependency_field,
    should_skip_dependency_validation,
)
from esmerald.utils.helpers import is_optional_union
from esmerald.websockets import WebSocket
from pydantic import BaseConfig, BaseModel, ValidationError, create_model
from pydantic_factories import ModelFactory

if TYPE_CHECKING:
    from pydantic.error_wrappers import ErrorDict
    from pydantic.typing import AnyCallable, DictAny
    from starlette.datastructures import URL

IntValError = Union[InternalServerError, ValidationError]


class EsmeraldSignature(BaseModel):
    dependency_names: ClassVar[Set[str]]
    return_annotation: ClassVar[Any]

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def parse_values_for_connection(
        cls, connection: Union[Request, WebSocket], **kwargs: "DictAny"
    ) -> "DictAny":
        try:
            signature = cls(**kwargs)
            values = {}
            for key in cls.__fields__:
                values[key] = signature.field_value(key)
        except ValidationError as e:
            raise cls.build_exception(connection, e) from e

    @classmethod
    def build_exception(
        cls, connection: Union[Request, WebSocket], exception: ValidationError
    ) -> IntValError:
        server_errors = []
        client_errors = []

        for err in exception.errors():
            if not cls.is_server_error(err):
                client_errors.append(err)
            else:
                server_errors.append(err)

        method, url = get_connection_info(connection=connection)
        error_message = f"Validation failed for {url} with method {method}."

        if client_errors:
            return ValidationErrorException(detail=error_message, extra=client_errors)
        return InternalServerError(detail=error_message, extra=server_errors)

    @classmethod
    def is_server_error(cls, error: "ErrorDict") -> bool:
        """
        Classic approach functionality used widely to check if is a server error or not.
        """
        return error["loc"][-1] in cls.dependency_names

    def field_value(self, key: str) -> Any:
        return self.__getattribute__(key)


class Parameter(BaseModel):
    annotation: Optional[Any]
    default: Optional[Any]
    name: Optional[str]
    optional: Optional[bool]
    fn_name: Optional[str]
    param_name: Optional[str]
    parameter: Optional[InspectParameter]

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self, fn_name: str, param_name: str, parameter: InspectParameter, **kwargs: "DictAny"
    ) -> None:
        super().__init__(**kwargs)
        if parameter.annotation is Signature.empty:
            raise ImproperlyConfigured(
                f"The parameter name {param_name} from {fn_name} does not have a type annotation. "
                "If it should receive any value, use 'Any' as type."
            )
        self.annotation = parameter.annotation
        self.default = parameter.default
        self.param_name = param_name
        self.optional = is_optional_union(self.annotation)

    @property
    def default_defined(self) -> bool:
        return self.default not in UNDEFINED
