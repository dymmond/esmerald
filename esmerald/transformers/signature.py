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


def is_server_error(error: Any, klass: Type["SignatureModel"]) -> bool:
    """
    Determines if the given error is classified as a server error.

    Args:
        error (Any): The error object to evaluate.
        klass (SignatureModel): The class containing dependency names to check against.

    Returns:
        bool: True if the error is a server error, False otherwise.
    """
    return error["loc"][-1] in klass.dependency_names


class Parameter(ArbitraryBaseModel):
    """
    Represents a function parameter with associated metadata.

    Attributes:
        annotation (Optional[Any]): Type annotation of the parameter.
        default (Optional[Any]): Default value of the parameter.
        name (Optional[str]): Name of the parameter.
        optional (Optional[bool]): Indicates if the parameter is optional.
        fn_name (Optional[str]): Name of the function to which the parameter belongs.
        param_name (Optional[str]): Name of the parameter.
        parameter (Optional[InspectParameter]): Original inspect parameter object.

    Raises:
        ImproperlyConfigured: If the parameter lacks a type annotation.

    Notes:
        - The `annotation` attribute is set from the `parameter.annotation`.
        - `default_defined` property checks if a default value is defined for the parameter.
    """

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
        if parameter.annotation is InspectParameter.empty:
            raise ImproperlyConfigured(
                f"The parameter '{param_name}' from '{fn_name}' does not have a type annotation. "
                "If it should receive any value, use 'Any' as type."
            )
        self.annotation = parameter.annotation
        self.default = parameter.default
        self.param_name = param_name
        self.name = param_name
        self.optional = is_optional_union(self.annotation)

    @property
    def default_defined(self) -> bool:
        """
        Checks if a default value is defined for the parameter.

        Returns:
            bool: True if a default value is defined, False otherwise.
        """
        return bool(self.default not in UNDEFINED)


class SignatureModel(ArbitraryBaseModel):
    """
    Represents a signature model for function signatures.

    Attributes:
        dependency_names (ClassVar[Set[str]]): Class variable holding a set of dependency names.
            This attribute is used to store names of dependencies required by the function signature.
        return_annotation (ClassVar[Any]): Class variable holding the return annotation type.
            This attribute represents the type annotation indicating the expected return type of the signature.
        encoders (ClassVar[Dict[str, "Encoder"]]): Class variable holding a dictionary of encoders.
            This attribute stores encoder instances associated with parameter names,
            allowing customized encoding and decoding of function parameters.

    Note:
        - `dependency_names` and `return_annotation` are intended to be set statically for the class.
        - `encoders` should be populated dynamically with encoder instances as needed.
    """

    dependency_names: ClassVar[Set[str]]
    return_annotation: ClassVar[Any]
    encoders: ClassVar[Dict["Encoder", Any]]

    @classmethod
    def parse_encoders(cls, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses the kwargs into a proper structure for the encoder itself.

        The encoders **must** be of Esmerald encoder type or else
        they will default to Lilya encoders. Lilya encoders do not implement
        custom `encode()` functionality.

        Args:
            kwargs (Dict[str, Any]): The keyword arguments to be parsed.

        Returns:
            Dict[str, Any]: The parsed keyword arguments with appropriate encoding applied.
        """

        def encode_value(encoder: "Encoder", annotation: Any, value: Any) -> Any:
            """
            Encodes a value using the given encoder and annotation.

            Args:
                encoder (Any): The encoder to use for encoding.
                annotation (Any): The annotation to guide the encoding process.
                value (Any): The value to be encoded.

            Returns:
                Any: The encoded value if the encoder is valid, otherwise the original value.
            """
            if hasattr(encoder, "encode"):
                return encoder.encode(annotation, value)
            return value

        for key, value in kwargs.items():
            if key in cls.encoders:
                encoder_info: Dict[str, "Encoder"] = cls.encoders[key]  # type: ignore
                encoder: "Encoder" = encoder_info["encoder"]
                annotation = encoder_info["annotation"]
                kwargs[key] = encode_value(encoder, annotation, value)

        return kwargs

    @classmethod
    def parse_values_for_connection(
        cls, connection: Union[Request, WebSocket], **kwargs: Dict[str, Any]
    ) -> Any:
        """
        Parses keyword arguments for connection, applies encoders if defined,
        and retrieves validated model fields.

        Args:
            connection (Union[Request, WebSocket]): The connection object.
            kwargs (Any): Keyword arguments to parse.

        Returns:
            Dict[str, Any]: Dictionary of validated model fields.

        Raises:
            BaseSystemException: If validation error occurs.
            EncoderException: If encoder error occurs.
        """
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
        Constructs an exception for encoder-related errors.

        Args:
            connection (Union[Request, WebSocket]): The connection object where the error occurred.
            exception (Exception): The original exception object.

        Returns:
            Exception: Constructed exception with detailed error message and context.
        """

        def extract_error_message(exception: Exception) -> Dict[str, Any]:
            """
            Extracts error message from the exception and organizes it into a dictionary format.

            Args:
                exception (Exception): The original exception object.

            Returns:
                dict: Dictionary containing the extracted error message.
            """
            error_pattern = re.compile(r"`\$\.(.+)`$")
            match = error_pattern.search(str(exception))

            if match:
                keys = list(match.groups())
                return {keys[0]: str(exception).split(" - ")[0]}
            else:
                return str(exception)  # type: ignore

        try:
            method, url = get_connection_info(connection)
            error_message = f"Validation failed for {url} with method {method}."
            error_detail = extract_error_message(exception)
            return ValidationErrorException(detail=error_message, extra=[error_detail])
        except Exception as e:
            # Handle any unexpected errors here
            # Return the original exception if unable to construct ValidationErrorException
            return e

    @classmethod
    def build_base_system_exception(
        cls, connection: Union[Request, WebSocket], exception: ValidationError
    ) -> Union["InternalServerError", "ValidationErrorException", "Exception"]:
        """
        Constructs a system exception based on validation errors, categorizing them
        as server or client errors, and providing detailed context.

        Args:
            connection (Union[Request, WebSocket]): The connection object where the error occurred.
            exception (ValidationError): The validation error that occurred.

        Returns:
            Union[InternalServerError, ValidationErrorException]: The constructed exception with
            detailed error message and categorized errors.
        """

        def categorize_errors(errors: list) -> tuple:
            """
            Categorizes errors into server errors and client errors.

            Args:
                errors (list): List of errors to categorize.

            Returns:
                tuple: Two lists containing server errors and client errors respectively.
            """
            server_errors = []
            client_errors = []
            for err in errors:
                if is_server_error(err, cls):
                    server_errors.append(err)
                else:
                    client_errors.append(err)
            return server_errors, client_errors

        try:
            error_list = loads(exception.json())
            server_errors, client_errors = categorize_errors(error_list)

            method, url = get_connection_info(connection)
            error_message = f"Validation failed for {url} with method {method}."

            if client_errors:
                return ValidationErrorException(detail=error_message, extra=client_errors)
            return InternalServerError(detail=error_message, extra=server_errors)
        except Exception as e:
            # Handle any unexpected errors here
            # Return the original exception if unable to construct the expected exceptions
            return e

    def field_value(self, key: str) -> Any:
        return self.__getattribute__(key)


class SignatureFactory(ArbitraryExtraBaseModel):
    """
    Factory class for creating a signature model based on a callable function.

    Attributes:
        fn (AnyCallable): The callable function or method.
        signature (InspectSignature): Signature object obtained from inspecting `fn`.
        fn_name (str): Name of the function.
        defaults (Dict[str, Any]): Dictionary holding default values for function parameters.
        dependency_names (Set[str]): Set of dependency names required by the function.
        field_definitions (Dict[Any, Any]): Dictionary holding field definitions for the signature model.

    Raises:
        ImproperlyConfigured: If there is an error during signature creation.

    Notes:
        - The `fn_name` defaults to "anonymous" if the function lacks a `__name__` attribute.
        - `field_definitions` is used to define fields for the signature model.
    """

    def __init__(self, fn: "AnyCallable", dependency_names: Set[str], **kwargs: Any) -> None:
        """
        Initializes a SignatureFactory instance.

        Args:
            fn (AnyCallable): The callable function or method.
            dependency_names (Set[str]): Set of dependency names required by the function.
            **kwargs: Additional keyword arguments passed to ArbitraryExtraBaseModel constructor.

        Raises:
            ImproperlyConfigured: If there is an error during signature creation.
        """
        super().__init__(**kwargs)
        self.fn = fn
        self.signature = InspectSignature.from_callable(self.fn)
        self.fn_name = fn.__name__ if hasattr(fn, "__name__") else "anonymous"
        self.defaults: Dict[str, Any] = {}
        self.dependency_names = dependency_names
        self.field_definitions: Dict[Any, Any] = {}

    def validate_missing_dependency(self, param: Any) -> None:
        """
        Validates if a required dependency is missing. Raises an error if a non-optional
        dependency field does not have a default value and is not listed in the class's
        dependency names.

        Args:
            param (Any): The parameter to validate.

        Raises:
            ImproperlyConfigured: If a required dependency is missing.
        """
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
        """
        Adds the parameter name to the set of dependency names if the parameter is identified
        as a dependency field.

        Args:
            param (Any): The parameter to check and add if it is a dependency field.
        """
        if is_dependency_field(param.default):
            self.dependency_names.add(param.name)

    def set_default_field(self, param: Any) -> None:
        """
        Sets the default value for the parameter in the defaults dictionary if the parameter
        has a default value defined.

        Args:
            param (Any): The parameter to check and set the default value for.
        """
        if param.default_defined:
            self.defaults[param.name] = param.default

    @property
    def parameters(self) -> Generator["Parameter", None, None]:
        """
        Yields parameters of the function signature, excluding any special class-specific words.

        Returns:
            Generator[Parameter, None, None]: A generator yielding Parameter instances.
        """
        for name, param in self.signature.parameters.items():
            if name in CLASS_SPECIAL_WORDS:
                continue
            yield Parameter(self.fn_name, name, param)

    def skip_parameter_validation(self, param: "Parameter") -> bool:
        """
        Determines whether validation should be skipped for the given parameter.

        Args:
            param (Parameter): The parameter to evaluate.

        Returns:
            bool: True if validation should be skipped, False otherwise.
        """
        return param.name in VALIDATION_NAMES or should_skip_dependency_validation(param.default)

    def extract_arguments(
        self, param: Union["Parameter", None] = None, argument_list: Union[List[Any], None] = None
    ) -> List[Type[type]]:
        """
        Recursively extracts unique types from a parameter's type annotation.

        Args:
            param (Union[Parameter, None], optional): The parameter with type annotation to extract from.
            argument_list (Union[List[Any], None], optional): The list of arguments extracted so far.

        Returns:
            List[Type[type]]: A list of unique types extracted from the parameter's type annotation.
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

    def create_signature(self) -> Type[SignatureModel]:
        """
        Creates a SignatureModel based on function parameters and annotations.

        Returns:
            Type[SignatureModel]: The created SignatureModel class.

        Raises:
            ImproperlyConfigured: If there is an error during signature creation.
        """
        try:
            encoders = self._handle_encoders()
            self._process_parameters()

            model = self._build_signature_model(encoders)
            return model

        except TypeError as e:
            raise ImproperlyConfigured(
                f"Error creating signature for '{self.fn_name}': '{e}'."
            ) from e

    def _handle_encoders(self) -> Dict[str, Any]:
        """
        Extracts encoders for parameters based on their annotations.

        Returns:
            Dict[str, Any]: A dictionary mapping parameter names to encoder details.
        """
        encoders: Dict[str, Any] = {}
        for param in self.parameters:
            if not self._should_skip_parameter(param):
                encoder = self._find_encoder(param.annotation)
                if encoder:
                    encoders[param.name] = {
                        "encoder": encoder,
                        "annotation": param.annotation,
                    }
        return encoders

    def _should_skip_parameter(self, param: "Parameter") -> bool:
        """
        Checks if validation should be skipped for the given parameter.

        Args:
            param (Parameter): The parameter to check.

        Returns:
            bool: True if validation should be skipped, False otherwise.
        """
        return param.name in VALIDATION_NAMES or should_skip_dependency_validation(param.default)

    def _find_encoder(self, annotation: Any) -> Any:
        """
        Finds an appropriate encoder for the given parameter annotation.

        Args:
            annotation (Any): The parameter annotation to find an encoder for.

        Returns:
            Any: The encoder found, or None if no encoder matches.
        """
        origin = get_origin(annotation)
        for encoder in ENCODER_TYPES:
            if not origin and encoder.is_type(annotation):
                return encoder
            elif origin:
                arguments = self.extract_arguments(annotation)
                if any(encoder.is_type(arg) for arg in arguments):
                    return encoder
        return None

    def _process_parameters(self) -> None:
        """
        Processes parameters to validate dependencies, set default fields, and define field definitions.
        """
        for param in self.parameters:
            self.validate_missing_dependency(param)
            self.get_dependency_names(param)
            self.set_default_field(param)
            if not self._should_skip_parameter(param):
                self.field_definitions[param.name] = get_field_definition_from_param(param)
            else:
                self.field_definitions[param.name] = (Any, ...)

    def _build_signature_model(self, encoders: Dict[str, Any]) -> Type[SignatureModel]:
        """
        Builds the SignatureModel using field definitions, encoders, and return annotation.

        Args:
            encoders (Dict[str, Any]): A dictionary mapping parameter names to encoder details.

        Returns:
            Type[SignatureModel]: The created SignatureModel class.
        """
        model = create_model(
            self.fn_name + "_signature",
            __base__=SignatureModel,
            **self.field_definitions,
        )
        model.return_annotation = self.signature.return_annotation
        model.dependency_names = self.dependency_names
        model.encoders = encoders  # type: ignore
        return model
