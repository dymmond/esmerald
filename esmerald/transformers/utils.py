from typing import (
    TYPE_CHECKING,
    Any,
    List,
    NamedTuple,
    Set,
    Tuple,
    Type,
    cast,
)

from esmerald.enums import ParamType, ScopeType
from esmerald.exceptions import ImproperlyConfigured, ValidationErrorException
from esmerald.parsers import BaseModelExtra, HashableBaseModel
from esmerald.requests import Request
from esmerald.utils.constants import REQUIRED
from pydantic.fields import FieldInfo, Undefined
from starlette.datastructures import URL

if TYPE_CHECKING:
    from esmerald.injector import Inject
    from esmerald.transformers.datastructures import EsmeraldSignature, Parameter
    from esmerald.typing import ConnectionType
    from pydantic.typing import DictAny, MappingIntStrAny


class ParamSetting(NamedTuple):
    default_value: Any
    field_alias: str
    field_name: str
    is_required: bool
    is_sequence: bool
    param_type: ParamType
    field_info: FieldInfo


class Dependency(HashableBaseModel, BaseModelExtra):
    def __init__(
        self, key: str, inject: "Inject", dependencies: List["Dependency"], **kwargs: "DictAny"
    ) -> None:
        super().__init__(**kwargs)
        self.key = key
        self.inject = inject
        self.dependencies = dependencies

    class Config(BaseModelExtra.Config):
        arbitrary_types_allowed = True


def merge_sets(first_set: Set[ParamSetting], second_set: Set[ParamSetting]) -> Set[ParamSetting]:
    merged_result = first_set.intersection(second_set)
    difference = first_set.symmetric_difference(second_set)
    for parameter in difference:
        if parameter.is_required or not any(
            param.field_alias == parameter.field_alias and param.is_required
            for param in difference
        ):
            merged_result.add(parameter)
    return merged_result


def create_parameter_setting(
    allow_none: bool,
    field_info: FieldInfo,
    field_name: str,
    path_parameters: Set[str],
    is_sequence: bool,
) -> ParamSetting:
    """
    Creates a setting definition for a parameter.
    """
    extra = field_info.extra
    is_required = extra.get(REQUIRED, True)
    default_value = field_info.default if field_info.default is not Undefined else None

    field_alias = extra.get(ParamType.QUERY) or field_name
    param_type = getattr(field_info, "in_", ParamType.QUERY)

    if field_name in path_parameters:
        field_alias = field_name
        param_type = param_type.PATH
    elif extra.get(ParamType.HEADER):
        field_alias = extra[ParamType.HEADER]
        param_type = ParamType.HEADER
    elif extra.get(ParamType.COOKIE):
        field_alias = extra[ParamType.COOKIE]
        param_type = ParamType.COOKIE

    param_settings = ParamSetting(
        param_type=param_type,
        field_alias=field_alias,
        default_value=default_value,
        field_name=field_name,
        field_info=field_info,
        is_sequence=is_sequence,
        is_required=is_required and (default_value is None and not allow_none),
    )
    return param_settings


def get_request_params(
    params: "MappingIntStrAny", expected: Set[ParamSetting], url: URL
) -> "DictAny":
    """
    Gather the parameters from the request.
    """
    _params = []
    for param in expected:
        if param.is_required and param.field_alias not in params:
            _params.append(param.field_alias)
    if _params:
        raise ValidationErrorException(
            f"Missing required parameter(s) {', '.join(_params)} for url {url}."
        )
    values = {
        param.field_name: params.get(param.field_alias, param.default_value) for param in expected
    }
    return values


def get_connection_info(connection: "ConnectionType") -> Tuple[str, "URL"]:
    """
    Extacts the information from the ConnectionType.
    """
    method = connection.method if isinstance(connection, Request) else ScopeType.WEBSOCKET
    return method, connection.url


def get_signature(value: Any) -> Type["EsmeraldSignature"]:
    try:
        return cast("Type[EsmeraldSignature]", getattr(value, "signature_model"))
    except AttributeError as exc:
        raise ImproperlyConfigured(f"The 'signature' attribute for {value} is not set.") from exc


def get_field_definition_from_param(param: "Parameter") -> Tuple[Any, Any]:
    if param.default_defined:
        definition = (param.annotation, param.default)
    elif not param.optional:
        definition = (param.annotation, ...)
    else:
        definition = (param.annotation, None)
    return definition
