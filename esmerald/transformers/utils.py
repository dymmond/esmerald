from typing import TYPE_CHECKING, Any, Dict, List, NamedTuple, Set, Tuple, Type, Union, cast

from lilya.datastructures import URL
from pydantic.fields import FieldInfo

from esmerald.enums import ParamType, ScopeType
from esmerald.exceptions import ImproperlyConfigured, ValidationErrorException
from esmerald.params import Cookie, Header, Path, Query
from esmerald.parsers import ArbitraryExtraBaseModel, HashableBaseModel
from esmerald.requests import Request
from esmerald.typing import Undefined
from esmerald.utils.constants import REQUIRED

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.injector import Inject
    from esmerald.transformers.datastructures import EsmeraldSignature, Parameter
    from esmerald.types import ConnectionType


class ParamSetting(NamedTuple):
    default_value: Any
    field_alias: str
    field_name: str
    is_required: bool
    param_type: ParamType
    field_info: FieldInfo


class Dependency(HashableBaseModel, ArbitraryExtraBaseModel):
    def __init__(
        self, key: str, inject: "Inject", dependencies: List["Dependency"], **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.key = key
        self.inject = inject
        self.dependencies = dependencies


def _merge_difference_parameters(difference: Set[ParamSetting]) -> Set[ParamSetting]:
    """
    Merge difference parameters based on field alias and requirement.

    Args:
        difference (Set[ParamSetting]): Set of difference parameters.

    Returns:
        Set[ParamSetting]: Merged difference parameters.
    """
    merged_result = set()

    for parameter in difference:
        if parameter.is_required or not any(
            param.field_alias == parameter.field_alias and param.is_required
            for param in difference
        ):
            merged_result.add(parameter)

    return merged_result


def merge_sets(first_set: Set[ParamSetting], second_set: Set[ParamSetting]) -> Set[ParamSetting]:
    """
    Merge two sets of parameter settings.

    Args:
        first_set (Set[ParamSetting]): First set of parameter settings.
        second_set (Set[ParamSetting]): Second set of parameter settings.

    Returns:
        Set[ParamSetting]: Merged set of parameter settings.
    """
    merged_result = first_set.intersection(second_set)
    difference = first_set.symmetric_difference(second_set)

    merged_result.update(_merge_difference_parameters(difference))

    return merged_result


def _get_default_value(field_info: FieldInfo) -> Any:
    """
    Get the default value from field information.

    Args:
        field_info (FieldInfo): Information about the field.

    Returns:
        Any: Default value of the field.
    """
    return field_info.default if field_info.default is not Undefined else None


def create_parameter_setting(
    allow_none: bool,
    field_info: FieldInfo,
    field_name: str,
    path_parameters: Set[str],
) -> ParamSetting:
    """
    Create a setting definition for a parameter.

    Args:
        allow_none (bool): Flag indicating if None is allowed.
        field_info (FieldInfo): Information about the field.
        field_name (str): Name of the field.
        path_parameters (Set[str]): Set of path parameters.

    Returns:
        ParamSetting: Parameter setting definition.
    """
    extra = cast("Dict[str, Any]", field_info.json_schema_extra) or {}
    is_required = extra.get(REQUIRED, True)
    default_value = _get_default_value(field_info)

    field_alias = extra.get(ParamType.QUERY) or field_name
    param_type = getattr(field_info, "in_", ParamType.QUERY)
    param: Union[Path, Header, Cookie, Query]

    if field_name in path_parameters:
        field_alias = field_name
        param_type = ParamType.PATH
        param = Path(default=default_value)
    elif extra.get(ParamType.HEADER):
        field_alias = extra[ParamType.HEADER]
        param_type = ParamType.HEADER
        param = Header(default=default_value)
    elif extra.get(ParamType.COOKIE):
        field_alias = extra[ParamType.COOKIE]
        param_type = ParamType.COOKIE
        param = Cookie(default=default_value)
    else:
        param = Query(default=default_value)

    if not field_info.alias:
        field_info.alias = field_name

    for key, _ in param._attributes_set.items():
        setattr(param, key, getattr(field_info, key, None))

    param_settings = ParamSetting(
        param_type=param_type,
        field_alias=field_alias,
        default_value=default_value,
        field_name=field_name,
        field_info=param,
        is_required=is_required and (default_value is None and not allow_none),
    )
    return param_settings


def _get_missing_required_params(params: Any, expected: Set[ParamSetting]) -> List[str]:
    """
    Get missing required parameters.

    Args:
        params (Any): Request parameters.
        expected (Set[ParamSetting]): Set of expected parameters.

    Returns:
        List[str]: List of missing required parameters.
    """
    missing_params = []
    for param in expected:
        if param.is_required and param.field_alias not in params:
            missing_params.append(param.field_alias)
    return missing_params


def get_request_params(params: Any, expected: Set[ParamSetting], url: URL) -> Any:
    """
    Gather the parameters from the request.

    Args:
        params (Any): Request parameters.
        expected (Set[ParamSetting]): Set of expected parameters.
        url (URL): The URL.

    Returns:
        Any: The gathered parameters.

    Raises:
        ValidationErrorException: If required parameters are missing.
    """
    missing_params = _get_missing_required_params(params, expected)
    if missing_params:
        raise ValidationErrorException(
            f"Missing required parameter(s) {', '.join(missing_params)} for URL {url}."
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
        return cast("Type[EsmeraldSignature]", value.signature_model)
    except AttributeError as exc:
        raise ImproperlyConfigured(f"The 'signature' attribute for {value} is not set.") from exc


def get_field_definition_from_param(param: "Parameter") -> Tuple[Any, Any]:
    if param.default_defined:
        definition = param.annotation, param.default
    elif not param.optional:
        definition = param.annotation, ...
    return definition
