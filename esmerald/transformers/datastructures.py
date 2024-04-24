import re
from inspect import Parameter as InspectParameter, Signature
from typing import Any, ClassVar, Dict, Optional, Set, Union

from msgspec import ValidationError as MsgspecValidationError
from orjson import loads
from pydantic import ValidationError

from esmerald.encoders import Encoder
from esmerald.exceptions import ImproperlyConfigured, InternalServerError, ValidationErrorException
from esmerald.parsers import ArbitraryBaseModel
from esmerald.requests import Request
from esmerald.transformers.constants import UNDEFINED
from esmerald.transformers.utils import get_connection_info
from esmerald.utils.helpers import is_optional_union
from esmerald.websockets import WebSocket


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
        cls, connection: Union[Request, WebSocket], exception: MsgspecValidationError
    ) -> ValidationErrorException:
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
        if parameter.annotation is Signature.empty:
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
