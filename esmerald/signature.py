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

from pydantic import BaseConfig, BaseModel, ValidationError, create_model
from pydantic.fields import FieldInfo, Undefined
from pydantic_factories import ModelFactory

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
        """Given a dictionary of values extracted from the connection, create
        an instance of the given SignatureModel subclass and return the parsed
        values.

        This is not equivalent to calling the '.dict'  method of the
        pydantic model, because it doesn't convert nested values into
        dictionary, just extracts the data from the signature model
        """
        try:
            signature = cls(**kwargs)
            return {key: signature.resolve_field_value(key) for key in cls.__fields__}
        except ValidationError as exc:
            raise cls.construct_exception(connection, exc) from exc

    def resolve_field_value(self, key: str) -> Any:
        """Given a field key, return value using plugin mapping, if
        available."""
        value = self.__getattribute__(key)  # pylint: disable=unnecessary-dunder-call
        return value

    @classmethod
    def construct_exception(
        cls, connection: Union[Request, WebSocket], exc: ValidationError
    ) -> Union[InternalServerError, ValidationError]:
        """Distinguish between validation errors that arise from parameters and
        dependencies.

        If both parameter and dependency values are invalid, we raise the client error first.

        Parameters
        ----------
        connection : Request | WebSocket
        exc : ValidationError

        Returns
        -------
        ValidationError | InternalServerError
        """
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
    """Represents the parameters of a callable for purpose of signature model
    generation.

    Parameters
    ----------
    fn_name : str
        Name of function.
    parameter_name : str
        Name of parameter.
    parameter : inspect.Parameter
    """

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
        """`True` if `self.default` is not one of the undefined sentinel types.

        Returns
        -------
        bool
        """
        return self.default not in UNDEFINED_SENTINELS


class SignatureModelFactory:
    """Utility class for constructing the signature model and grouping
    associated state.

    Instance available at `SignatureModel.factory`.

    Parameters
    ----------
    fn : AnyCallable
    dependency_names : Set[str]

    The following attributes are populated after the `model()` method has been called to generate
    the `SignatureModel` subclass.

    Attributes
    ----------
    field_definitions : dict[str, Tuple[Any, Any]
        Maps parameter name to the `(<type>, <default>)` tuple passed to `pydantic.create_model()`.
    defaults : dict[str, Any]
        Maps parameter name to default value, if one defined.
    dependency_names : set[str]
        The names of all known dependency parameters.
    """

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
        """Where a dependency has been explicitly marked using the `Dependency`
        function, it is a configuration error if that dependency has been
        defined without a default value, and it hasn't been provided to the
        handler.

        Parameters
        ----------
        parameter : SignatureParameter

        Raises
        ------
        `ImproperlyConfigured`
        """
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
        """Add parameter name of dependencies declared using `Dependency()`
        function to the set of all dependency names.

        Parameters
        ----------
        parameter : SignatureParameter
        """
        if is_dependency_field(parameter.default):
            self.dependency_names.add(parameter.name)

    def set_field_default(self, parameter: SignatureParameter) -> None:
        """If `parameter` has defined default, map it to the parameter name in
        `self.defaults`.

        Parameters
        ----------
        parameter : SignatureParameter
        """
        if parameter.default_defined:
            self.defaults[parameter.name] = parameter.default

    @staticmethod
    def create_field_definition_from_parameter(
        parameter: SignatureParameter,
    ) -> Tuple[Any, Any]:
        """Construct an `(<annotation>, <default>)` tuple, appropriate for
        `pydantic.create_model()`.

        Parameters
        ----------
        parameter : SignatureParameter

        Returns
        -------
        tuple[Any, Any]
        """
        if parameter.default_defined:
            field_definition = (parameter.annotation, parameter.default)
        elif not parameter.optional:
            field_definition = (parameter.annotation, ...)
        else:
            field_definition = (parameter.annotation, None)
        return field_definition

    @property
    def signature_parameters(self) -> Generator[SignatureParameter, None, None]:
        """Iterable of `SignatureModel` instances, that represent the
        parameters of the function signature that should be included in the
        `SignatureModel` type.

        Returns
        -------
        Generator[SignatureParameter, None, None]
        """
        for name, parameter in self.signature.parameters.items():
            if name in SKIP_NAMES:
                continue
            yield SignatureParameter(self.fn_name, name, parameter)

    def should_skip_parameter_validation(self, parameter: SignatureParameter) -> bool:
        """Identify dependencies for which provided values should not be
        validated.

        Args:
            parameter (SignatureParameter): A parameter to be added to the signature model.

        Returns:
            A boolean indicating whether injected values for this parameter should not be validated.
        """
        return parameter.name in SKIP_VALIDATION_NAMES or should_skip_dependency_validation(
            parameter.default
        )

    def create_signature_model(self) -> Type[SignatureModel]:
        """Constructs a `SignatureModel` type that represents the signature of
        `self.fn`

        Returns
        -------
        type[SignatureModel]
        """
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
    """Helper function to retrieve and validate the signature model from a
    provider or handler."""
    try:
        return cast("Type[SignatureModel]", getattr(value, "signature_model"))
    except AttributeError as e:  # pragma: no cover
        raise ImproperlyConfigured(
            f"The 'signature_model' attribute for {value} is not set"
        ) from e
