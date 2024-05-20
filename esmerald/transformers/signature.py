from inspect import Signature as InspectSignature
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    List,
    Set,
    Type,
    Union,
    _GenericAlias,
    get_args,
    get_origin,
)

from pydantic import create_model

from esmerald.encoders import ENCODER_TYPES
from esmerald.exceptions import ImproperlyConfigured
from esmerald.parsers import ArbitraryExtraBaseModel
from esmerald.transformers.constants import CLASS_SPECIAL_WORDS, VALIDATION_NAMES
from esmerald.transformers.datastructures import EsmeraldSignature, Parameter
from esmerald.transformers.utils import get_field_definition_from_param
from esmerald.typing import Undefined
from esmerald.utils.dependency import is_dependency_field, should_skip_dependency_validation

if TYPE_CHECKING:
    from esmerald.typing import AnyCallable  # pragma: no cover


object_setattr = object.__setattr__


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
    def parameters(self) -> Generator[Parameter, None, None]:
        for name, param in self.signature.parameters.items():
            if name in CLASS_SPECIAL_WORDS:
                continue
            yield Parameter(self.fn_name, name, param)

    def skip_parameter_validation(self, param: Parameter) -> bool:
        return param.name in VALIDATION_NAMES or should_skip_dependency_validation(param.default)

    def extract_arguments(
        self, param: Union[Parameter, None] = None, argument_list: Union[List[Any], None] = None
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
        self, parameters: Generator[Parameter, None, None] = None
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
