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

import msgspec
from pydantic import create_model

from esmerald.exceptions import ImproperlyConfigured
from esmerald.parsers import ArbitraryExtraBaseModel
from esmerald.transformers.constants import CLASS_SPECIAL_WORDS, VALIDATION_NAMES
from esmerald.transformers.datastructures import EsmeraldSignature, Parameter
from esmerald.transformers.utils import get_field_definition_from_param
from esmerald.typing import Undefined
from esmerald.utils.dependency import is_dependency_field, should_skip_dependency_validation
from esmerald.utils.helpers import is_class_and_subclass

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

    def handle_msgspec_structs(
        self, parameters: Generator[Parameter, None, None] = None
    ) -> Dict[str, msgspec.Struct]:
        """
        Handles any msgspec case being sent by the payload.
        """
        msgpspec_structs: Dict[str, msgspec.Struct] = {}
        if parameters is None:
            parameters = self.parameters

        for param in parameters:
            origin = get_origin(param.annotation)

            if not origin:
                if isinstance(param.annotation, msgspec.Struct) or is_class_and_subclass(
                    param.annotation, msgspec.Struct
                ):
                    msgpspec_structs[param.name] = param.annotation
            else:
                arguments: List[Type[type]] = self.extract_arguments(param=param.annotation)

                if any(isinstance(value, msgspec.Struct) for value in arguments) or any(
                    is_class_and_subclass(value, msgspec.Struct) for value in arguments
                ):
                    msgpspec_structs[param.name] = param.annotation
        return msgpspec_structs

    def create_signature(self) -> Type[EsmeraldSignature]:
        """
        Creates the EsmeraldSignature based on the type of parameteres.

        This allows to understand if the msgspec is also available and allowed.
        """
        try:
            msgpspec_structs: Dict[str, msgspec.Struct] = self.handle_msgspec_structs()

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
            model.msgspec_structs = msgpspec_structs
            return model
        except TypeError as e:
            raise ImproperlyConfigured(  # pragma: no cover
                f"Error creating signature for '{self.fn_name}': '{e}'."
            ) from e
