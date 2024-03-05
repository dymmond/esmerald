import re
from inspect import Parameter as InspectParameter, Signature
from typing import Any, ClassVar, Dict, Optional, Set, Union

import msgspec
from msgspec import ValidationError as MsgspecValidationError
from orjson import loads
from pydantic import ValidationError

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
    msgspec_structs: ClassVar[Dict[str, msgspec.Struct]]

    @classmethod
    def parse_msgspec_structures(cls, kwargs: Any) -> Any:
        """
        Parses the kwargs for a possible msgspec Struct and instantiates it.
        """
        for k, v in kwargs.items():
            if k in cls.msgspec_structs:
                kwargs[k] = msgspec.json.decode(
                    msgspec.json.encode(v), type=cls.msgspec_structs[k]
                )
        return kwargs

    @classmethod
    def parse_values_for_connection(
        cls, connection: Union[Request, WebSocket], **kwargs: Any
    ) -> Any:
        try:
            if cls.msgspec_structs:
                kwargs = cls.parse_msgspec_structures(kwargs)

            signature = cls(**kwargs)
            values = {}
            for key in cls.model_fields:
                values[key] = signature.field_value(key)
            return values
        except ValidationError as e:
            raise cls.build_exception(connection, e) from e
        except MsgspecValidationError as e:
            raise cls.build_msgspec_exception(connection, e) from e

    @classmethod
    def build_msgspec_exception(
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
    def build_exception(
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
