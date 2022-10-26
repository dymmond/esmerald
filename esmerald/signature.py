from inspect import Parameter, Signature
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Generator,
    List,
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
from esmerald.utils.dependency import (
    is_dependency_field,
    should_skip_dependency_validation,
)
from esmerald.utils.helpers import is_optional_union
from esmerald.websockets import WebSocket
from pydantic import BaseConfig, BaseModel, ValidationError, create_model
from pydantic.fields import FieldInfo, Undefined
from pydantic_factories import ModelFactory

if TYPE_CHECKING:
    from pydantic.error_wrappers import ErrorDict
    from pydantic.typing import AnyCallable
    from starlette.datastructures import URL


UNDEFINED_SENTINELS = {Undefined, Signature.empty}
SKIP_NAMES = {"self", "cls"}
SKIP_VALIDATION_NAMES = {"request", "socket", "state"}


class SignatureModel(BaseModel):
    class Config(BaseConfig):
        arbitrary_types_allowed = True

    dependency_names: ClassVar[Set[str]]
    return_annotation: ClassVar[Any]

    @classmethod
    def parse_values_from_connection_kwargs(
        cls, connection: Union[Request, WebSocket], **kwargs: Any
    ) -> Dict[str, Any]:
        try:
            signature = cls(**kwargs)
            return {key: signature.resolve_field_value(key) for key in cls.__fields__}
        except ValidationError as exc:
            raise cls.construct_exception(connection, exc) from exc

    def resolve_field_value(self, key: str) -> Any:
        value = self.__getattribute__(key)  # pylint: disable=unnecessary-dunder-call
        return value

    @classmethod
    def construct_exception(
        cls, connection: Union[Request, WebSocket], exc: ValidationError
    ) -> Union[InternalServerError, ValidationError]:
        server_errors: List["ErrorDict"] = []
        client_errors: List["ErrorDict"] = []

        for error in exc.errors():
            if cls.is_server_error(error):
                server_errors.append(error)
            else:
                client_errors.append(error)

        method, url = cls.get_connection_method_and_url(connection)

        if client_errors:
            return ValidationErrorException(
                detail=f"Validation failed for {method} {url}", extra=client_errors
            )

        return InternalServerError(
            detail=f"A dependency failed validation for {method} {url}",
            extra=server_errors,
        )

    @classmethod
    def is_server_error(cls, error: "ErrorDict") -> bool:
        """Check whether given validation error is a server error."""
        return error["loc"][-1] in cls.dependency_names

    @staticmethod
    def get_connection_method_and_url(connection: Union[Request, WebSocket]) -> Tuple[str, "URL"]:
        """Extract method and URL from Request or WebSocket."""
        method = ScopeType.WEBSOCKET if isinstance(connection, WebSocket) else connection.method
        return method, connection.url


class SignatureParameter:
    __slots__ = (
        "annotation",
        "default",
        "name",
        "optional",
    )

    annotation: Any
    default: Any
    name: str
    optional: bool

    def __init__(self, fn_name: str, parameter_name: str, parameter: Parameter) -> None:
        if parameter.annotation is Signature.empty:
            raise ImproperlyConfigured(
                f"Kwarg {parameter_name} of {fn_name} does not have a type annotation. If it "
                f"should receive any value, use the 'Any' type."
            )
        self.annotation = parameter.annotation
        self.default = parameter.default
        self.name = parameter_name
        self.optional = is_optional_union(parameter.annotation)

    @property
    def default_defined(self) -> bool:
        return self.default not in UNDEFINED_SENTINELS


class SignatureModelFactory:
    __slots__ = (
        "defaults",
        "dependency_names",
        "field_definitions",
        "fn_name",
        "signature",
    )

    def __init__(
        self,
        fn: "AnyCallable",
        dependency_names: Set[str],
    ) -> None:
        if fn is None:
            raise ImproperlyConfigured(
                "Parameter `fn` to `SignatureModelFactory` cannot be `None`."
            )
        self.signature = Signature.from_callable(fn)
        self.fn_name = fn.__name__ if hasattr(fn, "__name__") else "anonymous"
        self.field_definitions: Dict[str, Any] = {}
        self.defaults: Dict[str, Any] = {}
        self.dependency_names = dependency_names

    def check_for_unprovided_dependency(self, parameter: SignatureParameter) -> None:
        if parameter.optional:
            return
        if not is_dependency_field(parameter.default):
            return
        field_info: FieldInfo = parameter.default
        if field_info.default is not Undefined:
            return
        if parameter.name not in self.dependency_names:
            raise ImproperlyConfigured(
                f"Explicit dependency '{parameter.name}' for '{self.fn_name}' has no default value, "
                f"or provided dependency."
            )

    def collect_dependency_names(self, parameter: SignatureParameter) -> None:
        if is_dependency_field(parameter.default):
            self.dependency_names.add(parameter.name)

    def set_field_default(self, parameter: SignatureParameter) -> None:
        if parameter.default_defined:
            self.defaults[parameter.name] = parameter.default

    @staticmethod
    def create_field_definition_from_parameter(
        parameter: SignatureParameter,
    ) -> Tuple[Any, Any]:
        if parameter.default_defined:
            field_definition = (parameter.annotation, parameter.default)
        elif not parameter.optional:
            field_definition = (parameter.annotation, ...)
        else:
            field_definition = (parameter.annotation, None)
        return field_definition

    @property
    def signature_parameters(self) -> Generator[SignatureParameter, None, None]:
        for name, parameter in self.signature.parameters.items():
            if name in SKIP_NAMES:
                continue
            yield SignatureParameter(self.fn_name, name, parameter)

    def should_skip_parameter_validation(self, parameter: SignatureParameter) -> bool:
        return parameter.name in SKIP_VALIDATION_NAMES or should_skip_dependency_validation(
            parameter.default
        )

    def create_signature_model(self) -> Type[SignatureModel]:
        try:
            for parameter in self.signature_parameters:
                self.check_for_unprovided_dependency(parameter)
                self.collect_dependency_names(parameter)
                self.set_field_default(parameter)
                if self.should_skip_parameter_validation(parameter):
                    # pydantic has issues with none-pydantic classes that receive generics
                    self.field_definitions[parameter.name] = (Any, ...)
                    continue
                if ModelFactory.is_constrained_field(parameter.default):
                    self.field_definitions[parameter.name] = (parameter.default, ...)
                    continue
                self.field_definitions[
                    parameter.name
                ] = self.create_field_definition_from_parameter(parameter)
            model: Type[SignatureModel] = create_model(
                self.fn_name + "_signature_model",
                __base__=SignatureModel,
                **self.field_definitions,
            )
            model.return_annotation = self.signature.return_annotation
            model.dependency_names = self.dependency_names
            return model
        except TypeError as e:
            raise ImproperlyConfigured(
                f"Error creating signature model for '{self.fn_name}': '{e}'"
            ) from e


def get_signature_model(value: Any) -> Type[SignatureModel]:
    try:
        return cast("Type[SignatureModel]", getattr(value, "signature_model"))
    except AttributeError as e:  # pragma: no cover
        raise ImproperlyConfigured(
            f"The 'signature_model' attribute for {value} is not set"
        ) from e
