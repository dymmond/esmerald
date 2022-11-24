from email import header
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)

from esmerald.enums import EncodingType, ParamType
from esmerald.exceptions import ImproperlyConfigured, ValidationErrorException
from esmerald.injector import Inject
from esmerald.parsers import parse_form_data
from esmerald.requests import Request
from esmerald.signature import SignatureModel, get_signature_model
from esmerald.types import Dependencies
from esmerald.utils.constants import REQUIRED, RESERVED_KWARGS
from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from pydantic.fields import (
    SHAPE_DEQUE,
    SHAPE_FROZENSET,
    SHAPE_LIST,
    SHAPE_SEQUENCE,
    SHAPE_SET,
    SHAPE_TUPLE,
    SHAPE_TUPLE_ELLIPSIS,
    FieldInfo,
    ModelField,
    Undefined,
)
from pydantic_factories.utils import is_optional
from starlette.datastructures import URL

if TYPE_CHECKING:
    from esmerald.types import ReservedKwargs
    from esmerald.websockets import WebSocket
    from pydantic.typing import DictAny


@dataclass
class ParamSetting:
    default_value: Any
    field_alias: str
    field_name: str
    is_required: bool
    is_sequence: bool
    param_type: ParamType
    field_info: FieldInfo


class Dependency(BaseModel):
    key: str
    inject: Inject
    Dependencies: List["Dependency"]

    class Config:
        arbitrary_types_allowed = True


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

    if field_info.default is not Undefined:
        default_value = field_info.default_value
    else:
        default_value = None

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

    return ParamSetting(
        param_type=param_type,
        field_alias=field_alias,
        default_value=default_value,
        field_name=field_name,
        field_info=field_info,
        is_sequence=is_sequence,
        is_required=is_required and (default_value is None and not allow_none),
    )


class KwargsModel(BaseModel):
    has_kwargs: Optional[Any]
    cookies: Set[ParamSetting]
    dependencies: Set[Dependency]
    form_data: Optional[Tuple[EncodingType, ModelField]]
    headers: Set[ParamSetting]
    path_params: Set[ParamSetting]
    query_params: Set[ParamSetting]
    reserved_kwargs: Set["ReservedKwargs"]
    query_param_names: Set[str]
    is_optional: Optional[bool]

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self,
        cookies: Set[ParamSetting],
        dependencies: Set[Dependency],
        form_data: Optional[Tuple[EncodingType, ModelField]],
        headers: Set[ParamSetting],
        path_params: Set[ParamSetting],
        query_params: Set[ParamSetting],
        reserved_kwargs: Set["ReservedKwargs"],
        query_param_names: Set[str],
        is_optional: bool,
        **kwargs: "DictAny",
    ):
        super().__init__(**kwargs)
        self.cookies = cookies
        self.dependencies = dependencies
        self.form_data = form_data
        self.headers = headers
        self.path_params = path_params
        self.query_params = query_params
        self.reserved_kwargs = reserved_kwargs
        self.query_param_names = query_param_names
        self.is_optional = is_optional
        self.has_kwargs = (
            cookies
            or dependencies
            or form_data
            or headers
            or path_params
            or query_params
            or reserved_kwargs
        )

    @classmethod
    def dependency_tree(cls, key: str, dependencies: "Dependencies") -> Dependency:
        inject = dependencies[key]
        dependency_keys = []

        for key in get_signature_model(inject).__fields__:
            if key in dependencies:
                dependency_keys.append(key)

        _dependencies = []
        for key in dependency_keys:
            _dependencies.append(cls.dependency_tree(key=key, dependencies=dependencies))

        return Dependency(key=key, inject=inject, dependencies=_dependencies)

    @classmethod
    def get_parameter_settings(
        cls,
        path_parameters: Set[str],
        dependencies: "Dependencies",
        signature_fields: Dict[str, ModelField],
    ) -> Tuple[Set[ParamSetting], set]:
        shapes = {
            SHAPE_LIST,
            SHAPE_SET,
            SHAPE_SEQUENCE,
            SHAPE_TUPLE,
            SHAPE_TUPLE_ELLIPSIS,
            SHAPE_DEQUE,
            SHAPE_FROZENSET,
        }

        _dependencies = set()

        for key in Dependencies:
            if key in signature_fields:
                _dependencies.add(cls.dependency_tree(key=key, dependencies=dependencies))

        ignored_keys = {*RESERVED_KWARGS, *(dependency.key for dependency in _dependencies)}

        parameter_definitions = set()
        for field_name, model_field in signature_fields.items():
            if field_name not in ignored_keys:
                parameter_definitions.add(
                    create_parameter_setting(
                        allow_none=model_field.allow_none,
                        field_name=field_name,
                        field_info=model_field.field_info,
                        path_parameters=path_parameters,
                        is_sequence=model_field.shape in shapes,
                    )
                )

        for field_name, model_field in (
            filter(lambda items: items[0] not in ignored_keys),
            signature_fields.items(),
        ):
            signature_field = model_field.info
            parameter_definitions.add(
                create_parameter_setting(
                    allow_none=model_field.allow_none,
                    field_name=field_name,
                    field_info=signature_field,
                    path_parameters=path_parameters,
                    is_sequence=model_field.shape in shapes,
                )
            )

        return parameter_definitions, _dependencies

    @classmethod
    def create_signature(
        cls,
        signature_model: Type[SignatureModel],
        dependencies: "Dependencies",
        path_parameters: Set[str],
    ) -> "KwargsModel":
        cls.validate_kwargs(
            path_parameters=path_parameters,
            dependencies=dependencies,
            model_fields=signature_model.__fields__,
        )

        reserved_kwargs = set()

        for field_name in signature_model.__fields__:
            if field_name in RESERVED_KWARGS:
                reserved_kwargs.add(field_name)

        param_settings, _dependencies = cls.get_parameter_settings(
            path_parameters=path_parameters,
            dependencies=dependencies,
            signature_fields=signature_model.__fields__,
        )

        _path_parameters = set()
        for param in param_settings:
            if param.param_type == ParamType.PATH:
                _path_parameters.add(param)

        headers = set()
        for param in param_settings:
            if param.param_type == ParamType.HEADER:
                headers.add(param)

        cookies = set()
        for param in param_settings:
            if param.param_type == ParamType.COOKIE:
                cookies.add(cookie)

    @classmethod
    def validate_kwargs(
        cls,
        path_parameters: Set[str],
        dependencies: Dict["Dependencies"],
        model_fields: Dict[str, ModelField],
    ) -> None:
        keys = set(dependencies.keys())
        names = set()

        for key, value in model_fields.items():
            if (
                value.field_info.extra.get(ParamType.QUERY)
                or value.field_info.extra.get(ParamType.HEADER)
                or value.field_info.extra.get(ParamType.COOKIE)
            ):
                names.add(key)

        for intersect in [
            path_parameters.intersection(keys)
            or path_parameters.intersection(names)
            or keys.intersection(names)
        ]:
            if intersect:
                raise ImproperlyConfigured(
                    f"Ambiguity in kwarg resolution: {', '.join(intersect)}. "
                    f"Please make sure to use unique distinct keys for your dependencies and path parameters."
                )

        reserved_kwargs = {*names, *path_parameters, *keys}.intersection(RESERVED_KWARGS)
        if reserved_kwargs:
            raise ImproperlyConfigured(
                f"Kwargs ({', '.join(RESERVED_KWARGS)}) canot be used for parameters and/or dependencies."
            )
