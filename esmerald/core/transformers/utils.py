from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Mapping,
    NamedTuple,
    Set,
    Tuple,
    Type,
    Union,
    cast,
    get_args,
    get_origin,
)

from lilya.datastructures import URL
from pydantic.fields import FieldInfo

from esmerald.exceptions import ImproperlyConfigured, ValidationErrorException
from esmerald.params import Cookie, Header, Path, Query
from esmerald.parsers import ArbitraryExtraBaseModel, HashableBaseModel
from esmerald.requests import Request
from esmerald.typing import Undefined
from esmerald.utils.constants import REQUIRED
from esmerald.utils.dependencies import is_requires
from esmerald.utils.enums import ParamType, ScopeType
from esmerald.utils.helpers import is_class_and_subclass, is_union
from esmerald.utils.schema import should_skip_json_schema

if TYPE_CHECKING:  # pragma: no cover
    from esmerald.core.transformers.signature import Parameter, SignatureModel
    from esmerald.injector import Inject
    from esmerald.types import ConnectionType


class ParamSetting(NamedTuple):
    default_value: Any
    field_alias: str
    field_name: str
    is_required: bool
    param_type: ParamType
    field_info: FieldInfo
    is_security: bool = False
    is_requires_dependency: bool = False


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
    is_security: bool,
    is_requires_dependency: bool,
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
        # Checking if the value should go to body or query params
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
        is_security=is_security,
        is_requires_dependency=is_requires_dependency,
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


async def get_request_params(
    params: Mapping[Union[int, str], Any],
    expected: Set[ParamSetting],
    url: URL,
) -> Any:
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

    values: Dict[Any, Any] = {}
    for param in expected:
        is_requires_dependency = is_requires(param.default_value)

        # Using the default value if the parameter is a dependency requires
        if is_requires_dependency:
            values[param.field_name] = param.default_value
            continue

        if not is_union(param.field_info.annotation):
            annotation = get_origin(param.field_info.annotation)
            origin = annotation or param.field_info.annotation
            if is_class_and_subclass(origin, (list, tuple)):
                values[param.field_name] = params.values()
            elif is_class_and_subclass(origin, dict):
                values[param.field_name] = dict(params.items()) if params else None
            else:
                values[param.field_name] = params.get(param.field_alias, param.default_value)
        elif is_union(param.field_info.annotation):
            arguments = get_args(param.field_info.annotation)
            if any(is_class_and_subclass(origin, (list, tuple)) for origin in arguments):
                values[param.field_name] = params.values()
            elif any(is_class_and_subclass(origin, dict) for origin in arguments):
                values[param.field_name] = dict(params.items()) if params else None
            else:
                values[param.field_name] = params.get(param.field_alias, param.default_value)
    return values


def get_connection_info(connection: "ConnectionType") -> Tuple[str, "URL"]:
    """
    Extacts the information from the ConnectionType.
    """
    method = connection.method if isinstance(connection, Request) else ScopeType.WEBSOCKET
    return method, connection.url


def get_signature(value: Any) -> Type["SignatureModel"]:
    try:
        return cast("Type[SignatureModel]", value.signature_model)
    except AttributeError as exc:
        raise ImproperlyConfigured(f"The 'signature' attribute for {value} is not set.") from exc


def get_field_definition_from_param(param: "Parameter") -> Tuple[Any, Any]:
    """
    This method will make sure that __future__ references are resolved by
    the Any type. This is necessary because the signature model will be
    generated before the actual type is resolved.
    """
    annotation: Union[Any, FieldInfo]

    if param.optional:
        annotation = should_skip_json_schema(param)
    annotation = Any if isinstance(param.annotation, str) else param.annotation

    if param.default_defined:
        definition = annotation, param.default
    elif not param.optional:
        definition = annotation, ...
    else:
        definition = annotation, None
    return definition
