from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)

from esmerald.enums import EncodingType, ParamType
from esmerald.exceptions import ImproperlyConfigured, ValidationErrorException
from esmerald.injector import Inject
from esmerald.parsers import parse_form_data
from esmerald.requests import Request
from esmerald.signature import SignatureModel, get_signature_model
from esmerald.utils.constants import REQUIRED, RESERVED_KWARGS
from esmerald.utils.pydantic import is_optional
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
from starlette.datastructures import URL

if TYPE_CHECKING:
    from esmerald.types import Dependencies, ReservedKwargs
    from esmerald.websockets import WebSocket
    from pydantic.typing import DictAny, MappingIntStrAny


MEDIA_TYPES = [EncodingType.MULTI_PART, EncodingType.URL_ENCODED]


class ParamSetting(NamedTuple):
    default_value: Any
    field_alias: str
    field_name: str
    is_required: bool
    is_sequence: bool
    param_type: ParamType
    field_info: FieldInfo


# class Dependency(BaseModel):
#     key: Optional[str]
#     inject: Optional[Inject]
#     dependencies: Optional[List["Dependency"]]

#     def __init__(
#         self, key: str, inject: Inject, dependencies: List["Dependency"], **kwargs: "DictAny"
#     ) -> None:
#         super().__init__(**kwargs)
#         self.key = key
#         self.inject = inject
#         self.dependencies = dependencies

#     class Config:
#         arbitrary_types_allowed = True


class Dependency:
    def __init__(
        self, key: str, inject: Inject, dependencies: List["Dependency"], **kwargs: "DictAny"
    ) -> None:
        super().__init__(**kwargs)
        self.key = key
        self.inject = inject
        self.dependencies = dependencies

    class Config:
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
            _params.append(param)
    if _params:
        raise ValidationErrorException(
            f"Missing required parameter(s) {', '.join(_params)} for url {url}"
        )
    values = {
        param.field_name: params.get(param.field_alias, param.default_value) for param in expected
    }
    return values


class KwargsModel(BaseModel):
    has_kwargs: Optional[Any]
    cookies: Optional[Set[ParamSetting]]
    dependencies: Optional[Set[Dependency]]
    form_data: Optional[Tuple[EncodingType, ModelField]]
    headers: Optional[Set[ParamSetting]]
    path_params: Optional[Set[ParamSetting]]
    query_params: Optional[Set[ParamSetting]]
    reserved_kwargs: Optional[Set["ReservedKwargs"]]
    query_param_names: Optional[Set[str]]
    is_data_optional: Optional[bool]

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
        is_data_optional: bool,
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
        self.has_kwargs = (
            cookies
            or dependencies
            or form_data
            or headers
            or path_params
            or query_params
            or reserved_kwargs
        )
        self.is_data_optional = is_data_optional

    @classmethod
    def dependency_tree(cls, key: str, dependencies: "Dependencies") -> Dependency:
        inject = dependencies[key]
        dependency_keys = [
            key for key in get_signature_model(inject).__fields__ if key in dependencies
        ]
        return Dependency(
            key=key,
            inject=inject,
            dependencies=[
                cls.dependency_tree(key=key, dependencies=dependencies) for key in dependency_keys
            ],
        )

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

        for key in dependencies:
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

        for field_name, model_field in filter(
            lambda items: items[0] not in ignored_keys,
            signature_fields.items(),
        ):
            signature_field = model_field.field_info
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

        path_params = set()
        for param in param_settings:
            if param.param_type == ParamType.PATH:
                path_params.add(param)

        headers = set()
        for param in param_settings:
            if param.param_type == ParamType.HEADER:
                headers.add(param)

        cookies = set()
        for param in param_settings:
            if param.param_type == ParamType.COOKIE:
                cookies.add(param)

        query_params = set()
        for param in param_settings:
            if param.param_type == ParamType.QUERY:
                query_params.add(param)

        query_params_names = set()
        for param in param_settings:
            if param.param_type == ParamType.QUERY and param.is_sequence:
                query_params_names.add(param)

        form_data = None

        # For the reserved keyword data
        data_field = signature_model.__fields__.get("data")
        if data_field:
            media_type = data_field.field_info.extra.get("media_type")
            if media_type in MEDIA_TYPES:
                form_data = (media_type, data_field)

        # Check the dependencies
        for dependency in _dependencies:
            dependency_model = cls.create_signature(
                signature_model=get_signature_model(dependency.inject),
                dependencies=dependencies,
                path_parameters=path_parameters,
            )
            path_params = merge_sets(path_params, dependency_model.path_params)
            query_params = merge_sets(query_params, dependency_model.query_params)
            cookies = merge_sets(cookies, dependency_model.cookies)
            headers = merge_sets(dependency_model.headers, dependency_model.headers)

            if "data" in reserved_kwargs and "data" in dependency_model.reserved_kwargs:
                cls.validate_data(form_data, dependency_model)
            reserved_kwargs.update(dependency_model.reserved_kwargs)

        is_data_optional = False
        if "data" in reserved_kwargs:
            is_data_optional = is_optional(signature_model.__fields__["data"])

        return KwargsModel(
            form_data=form_data,
            dependencies=_dependencies,
            path_params=path_params,
            query_params=query_params,
            cookies=cookies,
            headers=headers,
            reserved_kwargs=reserved_kwargs,
            query_param_names=query_params_names,
            is_data_optional=is_data_optional,
        )

    def to_kwargs(self, connection: Union["WebSocket", "Request"]) -> "DictAny":
        connection_params = {}
        for key, value in connection.query_params.items():
            if key not in self.query_param_names and len(value) == 1:
                value = value[0]
                connection_params[key] = value

        query_params = get_request_params(
            params=connection.query_params, expected=self.query_params, url=connection.url
        )
        path_params = get_request_params(
            params=connection.path_params, expected=self.path_params, url=connection.url
        )
        headers = get_request_params(
            params=connection.headers, expected=self.headers, url=connection.url
        )
        cookies = get_request_params(
            params=connection.cookies, expected=self.cookies, url=connection.url
        )

        if not self.reserved_kwargs:
            return {**query_params, **path_params, **headers, **cookies}

        return self.handle_reserved_kwargs(
            connection=connection,
            connection_params=connection_params,
            path_params=path_params,
            query_params=query_params,
            headers=headers,
            cookies=cookies,
        )

    def handle_reserved_kwargs(
        self,
        connection: Union["WebSocket", "Request"],
        connection_params: "DictAny",
        path_params: "DictAny",
        query_params: "DictAny",
        headers: "DictAny",
        cookies: "DictAny",
    ) -> "DictAny":
        reserved_kwargs: "DictAny" = {}
        if "data" in self.reserved_kwargs:
            reserved_kwargs["data"] = self.get_request_data(request=connection)
        if "request" in self.reserved_kwargs:
            reserved_kwargs["request"] = connection
        if "socket" in self.reserved_kwargs:
            reserved_kwargs["socket"] = connection
        if "headers" in self.reserved_kwargs:
            reserved_kwargs["headers"] = connection.headers
        if "cookies" in self.reserved_kwargs:
            reserved_kwargs["cookies"] = connection.cookies
        if "query" in self.reserved_kwargs:
            reserved_kwargs["query"] = connection_params
        if "state" in self.reserved_kwargs:
            reserved_kwargs["state"] = connection.app.state.copy()

        return {**reserved_kwargs, **path_params, **query_params, **headers, **cookies}

    @classmethod
    def validate_data(
        cls, form_data: Optional[Tuple[EncodingType, ModelField]], dependency_model: "KwargsModel"
    ) -> None:
        if form_data and dependency_model.form_data:
            media_type, _ = form_data
            dependency_media_type, _ = dependency_model.form_data
            if media_type != dependency_media_type:
                raise ImproperlyConfigured(
                    "Dependencies have incompatible form-data encoding. "
                    "They should both be the same. Either url-encoded or multi-part."
                )
        if (
            (form_data and not dependency_model.form_data)
            or not form_data
            and dependency_model.form_data
        ):
            raise ImproperlyConfigured(
                "Dependencies haev incompativle 'data' kwarg types. "
                "One expects JSON and the other expects form-data."
            )

    @classmethod
    def validate_kwargs(
        cls,
        path_parameters: Set[str],
        dependencies: "Dependencies",
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
                f"Kwargs ({', '.join(RESERVED_KWARGS)}) cannot be used for parameters and/or dependencies."
            )

    async def get_request_data(self, request: "Request") -> Any:
        # Fast exit
        if not self.form_data:
            return await request.json()

        media_type, field = self.form_data
        form_data = await request.form()
        parsed_form = parse_form_data(media_type, form_data, field)
        return parsed_form if parsed_form or not self.is_optional else None

    async def get_dependencies(
        self,
        dependency: "Dependency",
        connection: Union["WebSocket", "Request"],
        **kwargs: "DictAny",
    ) -> Any:
        signature_model = get_signature_model(dependency.inject)
        for _dependency in dependency.dependencies:
            kwargs[_dependency.key] = await self.get_dependencies(
                dependency=_dependency, connection=connection, **kwargs
            )
        dependency_kwargs = signature_model.parse_values_from_connection_kwargs(
            connection=connection, **kwargs
        )
        return await dependency.inject(**dependency_kwargs)
