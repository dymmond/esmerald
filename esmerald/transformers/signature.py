import re
from inspect import Parameter as InspectParameter, Signature as InspectSignature
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Generator,
    List,
    Optional,
    Set,
    Type,
    Union,
    _GenericAlias,
    get_args,
    get_origin,
)

from orjson import loads
from pydantic import ValidationError, create_model

from esmerald.encoders import ENCODER_TYPES, Encoder
from esmerald.exceptions import ImproperlyConfigured, InternalServerError, ValidationErrorException
from esmerald.parsers import ArbitraryBaseModel, ArbitraryExtraBaseModel
from esmerald.requests import Request
from esmerald.transformers.constants import CLASS_SPECIAL_WORDS, UNDEFINED, VALIDATION_NAMES
from esmerald.transformers.utils import get_connection_info, get_field_definition_from_param
from esmerald.typing import Undefined
from esmerald.utils.dependency import is_dependency_field, should_skip_dependency_validation
from esmerald.utils.helpers import is_optional_union
from esmerald.websockets import WebSocket

if TYPE_CHECKING:
    from esmerald.typing import AnyCallable  # pragma: no cover


object_setattr = object.__setattr__


class Parameter(ArbitraryBaseModel):
    annotation: Optional[Any] = None
    default: Optional[Any] = None
    name: Optional[str] = None
    optional: Optional[bool] = None
    fn_name: Optional[str] = None
    param_name: Optional[str] = None
    parameter: Optional[InspectParameter] = None

    def __init__(
        self, fn_name: str, param_name: str, parameter: InspectParameter, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        if parameter.annotation is InspectSignature.empty:
            raise ImproperlyConfigured(  # pragma: no cover
                f"The parameter name {param_name} from {fn_name} does not have a type annotation. "
                "If it should receive any value, use 'Any' as type."
            )
        self.annotation = parameter.annotation
        self.default = parameter.default
        self.param_name = param_name
        self.name = param_name
        self.optional = is_optional_union(self.annotation)

    @property
    def default_defined(self) -> bool:
        return self.default not in UNDEFINED


class EsmeraldSignature(ArbitraryBaseModel):
    dependency_names: ClassVar[Set[str]]
    return_annotation: ClassVar[Any]
    encoders: ClassVar[Dict[str, Any]]

    @classmethod
    def parse_encoders(cls, kwargs: Any) -> Any:
        """
        Parses the kwargs into a proper structure of the encoder
        itself.

        The encoders **must** be of Esmerald encoder or else
        it will default to Lilya encoders.

        Lilya encoders do not implement custom `encode()` functionality.
        """
        for key, value in kwargs.items():
            if key in cls.encoders:
                encoder: "Encoder" = cls.encoders[key]["encoder"]
                annotation = cls.encoders[key]["annotation"]
                kwargs[key] = (
                    encoder.encode(annotation, value) if isinstance(encoder, Encoder) else value
                )
        return kwargs

    @classmethod
    def parse_values_for_connection(
        cls, connection: Union[Request, WebSocket], **kwargs: Any
    ) -> Any:
        try:
            if cls.encoders:
                kwargs = cls.parse_encoders(kwargs)

            signature = cls(**kwargs)
            values = {}
            for key in cls.model_fields:
                values[key] = signature.field_value(key)
            return values
        except ValidationError as e:
            raise cls.build_base_system_exception(connection, e) from e
        except Exception as e:
            raise cls.build_encoder_exception(connection, e) from e

    @classmethod
    def build_encoder_exception(
        cls, connection: Union[Request, WebSocket], exception: Exception
    ) -> Exception:
        """
        Builds the exceptions for the message spec.
        """
        error_pattern = re.compile(r"`\$\.(.+)`$")

        match = error_pattern.search(str(exception))
        if match:
            keys = list(match.groups())
            message = {keys[0]: str(exception).split(" - ")[0]}
        else:
            message = str(exception)  # type: ignore

        method, url = get_connection_info(connection=connection)
        error_message = f"Validation failed for {url} with method {method}."

        return ValidationErrorException(detail=error_message, extra=[message])

    @classmethod
    def build_base_system_exception(
        cls, connection: Union[Request, WebSocket], exception: ValidationError
    ) -> Union[InternalServerError, ValidationErrorException]:
        server_errors = []
        client_errors = []

        for err in loads(exception.json()):
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
    def is_server_error(cls, error: Any) -> bool:
        """
        Classic approach functionality used widely to check if is a server error or not.
        """
        return error["loc"][-1] in cls.dependency_names

    def field_value(self, key: str) -> Any:
        return self.__getattribute__(key)


class SignatureFactory(ArbitraryExtraBaseModel):
    def __init__(self, fn: "AnyCallable", dependency_names: Set[str], **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.fn = fn
        self.signature = InspectSignature.from_callable(self.fn)
        self.fn_name = fn.__name__ if hasattr(fn, "__name__") else "anonymous"
        self.defaults: Dict[str, Any] = {}
        self.dependency_names = dependency_names
        self.field_definitions: Dict[Any, Any] = {}

    def validate_missing_dependency(self, param: Any) -> None:
        if param.optional:
            return
        if not is_dependency_field(param.default):
            return
        field = param.default
        if field.default is not Undefined:
            return
        if param.name not in self.dependency_names:
            raise ImproperlyConfigured(
                f"Explicit dependency '{param.name}' for '{self.fn_name}' has no default value, "
                f"or provided dependency."
            )

    def get_dependency_names(self, param: Any) -> None:
        if is_dependency_field(param.default):
            self.dependency_names.add(param.name)

    def set_default_field(self, param: Any) -> None:
        if param.default_defined:
            self.defaults[param.name] = param.default

    @property
    def parameters(self) -> Generator["Parameter", None, None]:
        for name, param in self.signature.parameters.items():
            if name in CLASS_SPECIAL_WORDS:
                continue
            yield Parameter(self.fn_name, name, param)

    def skip_parameter_validation(self, param: "Parameter") -> bool:
        return param.name in VALIDATION_NAMES or should_skip_dependency_validation(param.default)

    def extract_arguments(
        self, param: Union["Parameter", None] = None, argument_list: Union[List[Any], None] = None
    ) -> List[Type[type]]:
        """
        Recursively extracts the types.
        """
        arguments: List[Any] = list(argument_list) if argument_list is not None else []
        args = get_args(param)

        for arg in args:
            if isinstance(arg, _GenericAlias):
                arguments.extend(self.extract_arguments(param=arg, argument_list=arguments))
            else:
                if arg not in arguments:
                    arguments.append(arg)
        return arguments

    def handle_encoders(
        self, parameters: Generator["Parameter", None, None] = None
    ) -> Dict[str, Any]:
        """
        Handles the extraction of any of the passed encoders.
        """
        custom_encoders: Dict[str, Any] = {}

        if parameters is None:
            parameters = self.parameters

        for param in parameters:
            origin = get_origin(param.annotation)

            for encoder in ENCODER_TYPES:
                if not origin:
                    if encoder.is_type(param.annotation):
                        custom_encoders[param.name] = {
                            "encoder": encoder,
                            "annotation": param.annotation,
                        }
                    continue
                else:
                    arguments: List[Type[type]] = self.extract_arguments(param=param.annotation)

                    if any(encoder.is_type(value) for value in arguments):
                        custom_encoders[param.name] = {
                            "encoder": encoder,
                            "annotation": param.annotation,
                        }
                    continue
        return custom_encoders

    def create_signature(self) -> Type[EsmeraldSignature]:
        """
        Creates the EsmeraldSignature based on the type of parameters.

        This allows to understand if the msgspec is also available and allowed.
        """
        try:
            encoders: Dict[str, Any] = self.handle_encoders()

            for param in self.parameters:
                self.validate_missing_dependency(param)
                self.get_dependency_names(param)
                self.set_default_field(param)

                if self.skip_parameter_validation(param):
                    self.field_definitions[param.name] = (Any, ...)
                    continue
                self.field_definitions[param.name] = get_field_definition_from_param(param)

            model: Type["EsmeraldSignature"] = create_model(
                self.fn_name + "_signature",
                __base__=EsmeraldSignature,
                **self.field_definitions,
            )
            model.return_annotation = self.signature.return_annotation
            model.dependency_names = self.dependency_names
            model.encoders = encoders
            return model
        except TypeError as e:
            raise ImproperlyConfigured(  # pragma: no cover
                f"Error creating signature for '{self.fn_name}': '{e}'."
            ) from e
