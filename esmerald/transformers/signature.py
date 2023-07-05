from inspect import Signature as InspectSignature
from typing import TYPE_CHECKING, Any, Dict, Generator, Optional, Set, Type

from pydantic import create_model

from esmerald.exceptions import ImproperlyConfigured
from esmerald.parsers import ArbitraryExtraBaseModel
from esmerald.transformers.constants import CLASS_SPECIAL_WORDS, VALIDATION_NAMES
from esmerald.transformers.datastructures import EsmeraldSignature, Parameter
from esmerald.transformers.helpers import is_pydantic_constrained_field
from esmerald.transformers.utils import get_field_definition_from_param
from esmerald.typing import Undefined
from esmerald.utils.dependency import is_dependency_field, should_skip_dependency_validation

if TYPE_CHECKING:
    from esmerald.typing import AnyCallable


object_setattr = object.__setattr__


class SignatureFactory(ArbitraryExtraBaseModel):
    def __init__(
        self, fn: Optional["AnyCallable"], dependency_names: Set[str], **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        if not fn:
            raise ImproperlyConfigured("Parameter 'fn' to SignatureFactory cannot be `None`.")
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

    def create_signature(self) -> Type[EsmeraldSignature]:
        try:
            for param in self.parameters:
                self.validate_missing_dependency(param)
                self.get_dependency_names(param)
                self.set_default_field(param)

                if self.skip_parameter_validation(param):
                    self.field_definitions[param.name] = (Any, ...)
                    continue
                if is_pydantic_constrained_field(param.default):
                    self.field_definitions[param.name] = (param.default, ...)
                    continue
                self.field_definitions[param.name] = get_field_definition_from_param(param)

            model: Type["EsmeraldSignature"] = create_model(
                self.fn_name + "_signature",
                __base__=EsmeraldSignature,
                **self.field_definitions,
            )
            model.return_annotation = self.signature.return_annotation
            model.dependency_names = self.dependency_names
            return model
        except TypeError as e:
            raise ImproperlyConfigured(
                f"Error creating signature for '{self.fn_name}': '{e}'."
            ) from e
