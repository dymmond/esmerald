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
from esmerald.utils.constants import EXTRA_KEY_REQUIRED, RESERVED_KWARGS
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


class ParameterDefinition(NamedTuple):
    default_value: Any
    field_alias: str
    field_name: str
    is_required: bool
    is_sequence: bool
    param_type: ParamType
    field_info: FieldInfo


class Dependency:
    __slots__ = ("key", "inject", "dependencies")

    def __init__(self, key: str, inject: Inject, dependencies: List["Dependency"]) -> None:
        self.key = key
        self.inject = inject
        self.dependencies = dependencies


def merge_parameter_sets(
    first: Set[ParameterDefinition], second: Set[ParameterDefinition]
) -> Set[ParameterDefinition]:
    result: Set[ParameterDefinition] = first.intersection(second)
    difference = first.symmetric_difference(second)
    for param in difference:
        # add the param if it's either required or no-other param in difference is the same but required
        if param.is_required or not any(
            p.field_alias == param.field_alias and p.is_required for p in difference
        ):
            result.add(param)
    return result


class KwargsModel:
    __slots__ = (
        "has_kwargs",
        "expected_cookie_params",
        "expected_dependencies",
        "expected_form_data",
        "expected_header_params",
        "expected_path_params",
        "expected_query_params",
        "expected_reserved_kwargs",
        "sequence_query_parameter_names",
        "is_data_optional",
    )

    def __init__(
        self,
        *,
        expected_cookie_params: Set[ParameterDefinition],
        expected_dependencies: Set[Dependency],
        expected_form_data: Optional[Tuple[EncodingType, ModelField]],
        expected_header_params: Set[ParameterDefinition],
        expected_path_params: Set[ParameterDefinition],
        expected_query_params: Set[ParameterDefinition],
        expected_reserved_kwargs: Set["ReservedKwargs"],
        sequence_query_parameter_names: Set[str],
        is_data_optional: bool,
    ) -> None:
        self.expected_cookie_params = expected_cookie_params
        self.expected_dependencies = expected_dependencies
        self.expected_form_data = expected_form_data
        self.expected_header_params = expected_header_params
        self.expected_path_params = expected_path_params
        self.expected_query_params = expected_query_params
        self.expected_reserved_kwargs = expected_reserved_kwargs
        self.sequence_query_parameter_names = sequence_query_parameter_names
        self.has_kwargs = (
            expected_cookie_params
            or expected_dependencies
            or expected_form_data
            or expected_header_params
            or expected_path_params
            or expected_query_params
            or expected_reserved_kwargs
        )
        self.is_data_optional = is_data_optional

    @classmethod
    def _get_param_definitions(
        cls,
        path_parameters: Set[str],
        dependencies: Dict[str, Inject],
        signature_model_fields: Dict[str, ModelField],
    ) -> Tuple[Set[ParameterDefinition], set]:
        sequence_shapes = {
            SHAPE_LIST,
            SHAPE_SET,
            SHAPE_SEQUENCE,
            SHAPE_TUPLE,
            SHAPE_TUPLE_ELLIPSIS,
            SHAPE_DEQUE,
            SHAPE_FROZENSET,
        }

        expected_dependencies = {
            cls._create_dependency_graph(key=key, dependencies=dependencies)
            for key in dependencies
            if key in signature_model_fields
        }
        ignored_keys = {
            *RESERVED_KWARGS,
            *(dependency.key for dependency in expected_dependencies),
        }

        param_definitions = {
            *(
                cls._create_parameter_definition(
                    allow_none=model_field.allow_none,
                    field_name=field_name,
                    field_info=model_field.field_info,
                    path_parameters=path_parameters,
                    is_sequence=model_field.shape in sequence_shapes,
                )
                for field_name, model_field in signature_model_fields.items()
                if field_name not in ignored_keys
            ),
        }

        for field_name, model_field in filter(
            lambda items: items[0] not in ignored_keys,
            signature_model_fields.items(),
        ):
            signature_field_info = model_field.field_info
            param_definitions.add(
                cls._create_parameter_definition(
                    allow_none=model_field.allow_none,
                    field_name=field_name,
                    field_info=signature_field_info,
                    path_parameters=path_parameters,
                    is_sequence=model_field.shape in sequence_shapes,
                )
            )
        return param_definitions, expected_dependencies

    @classmethod
    def create_for_signature_model(
        cls,
        signature_model: Type[SignatureModel],
        dependencies: Dict[str, Inject],
        path_parameters: Set[str],
    ) -> "KwargsModel":
        cls._validate_raw_kwargs(
            path_parameters=path_parameters,
            dependencies=dependencies,
            model_fields=signature_model.__fields__,
        )
        expected_reserved_kwargs = {
            field_name
            for field_name in signature_model.__fields__
            if field_name in RESERVED_KWARGS
        }

        param_definitions, expected_dependencies = cls._get_param_definitions(
            path_parameters,
            dependencies,
            signature_model_fields=signature_model.__fields__,
        )

        expected_path_parameters = {p for p in param_definitions if p.param_type == ParamType.PATH}
        expected_header_parameters = {
            p for p in param_definitions if p.param_type == ParamType.HEADER
        }
        expected_cookie_parameters = {
            p for p in param_definitions if p.param_type == ParamType.COOKIE
        }
        expected_query_parameters = {
            p for p in param_definitions if p.param_type == ParamType.QUERY
        }
        sequence_query_parameter_names = {
            p.field_alias
            for p in param_definitions
            if p.param_type == ParamType.QUERY and p.is_sequence
        }

        expected_form_data = None
        data_model_field = signature_model.__fields__.get("data")
        if data_model_field:
            media_type = data_model_field.field_info.extra.get("media_type")
            if media_type in [
                EncodingType.MULTI_PART,
                EncodingType.URL_ENCODED,
            ]:
                expected_form_data = (media_type, data_model_field)

        for dependency in expected_dependencies:
            dependency_kwargs_model = cls.create_for_signature_model(
                signature_model=get_signature_model(dependency.inject),
                dependencies=dependencies,
                path_parameters=path_parameters,
            )
            expected_path_parameters = merge_parameter_sets(
                expected_path_parameters, dependency_kwargs_model.expected_path_params
            )
            expected_query_parameters = merge_parameter_sets(
                expected_query_parameters, dependency_kwargs_model.expected_query_params
            )
            expected_cookie_parameters = merge_parameter_sets(
                expected_cookie_parameters,
                dependency_kwargs_model.expected_cookie_params,
            )
            expected_header_parameters = merge_parameter_sets(
                expected_header_parameters,
                dependency_kwargs_model.expected_header_params,
            )
            if (
                "data" in expected_reserved_kwargs
                and "data" in dependency_kwargs_model.expected_reserved_kwargs
            ):
                cls._validate_dependency_data(
                    expected_form_data=expected_form_data,
                    dependency_kwargs_model=dependency_kwargs_model,
                )
            expected_reserved_kwargs.update(dependency_kwargs_model.expected_reserved_kwargs)

        return KwargsModel(
            expected_form_data=expected_form_data,
            expected_dependencies=expected_dependencies,
            expected_path_params=expected_path_parameters,
            expected_query_params=expected_query_parameters,
            expected_cookie_params=expected_cookie_parameters,
            expected_header_params=expected_header_parameters,
            expected_reserved_kwargs=cast("Set[ReservedKwargs]", expected_reserved_kwargs),
            sequence_query_parameter_names=sequence_query_parameter_names,
            is_data_optional=is_optional(signature_model.__fields__["data"])
            if "data" in expected_reserved_kwargs
            else False,
        )

    def to_kwargs(self, connection: Union["WebSocket", "Request"]) -> Dict[str, Any]:
        connection_query_params = {
            k: self._sequence_or_scalar_param(k, v) for k, v in connection.query_params.items()
        }

        query_params = self._collect_params(
            params=connection_query_params,
            expected=self.expected_query_params,
            url=connection.url,
        )

        path_params = self._collect_params(
            params=connection.path_params,
            expected=self.expected_path_params,
            url=connection.url,
        )
        header_params = self._collect_params(
            params=connection.headers,
            expected=self.expected_header_params,
            url=connection.url,
        )
        cookie_params = self._collect_params(
            params=connection.cookies,
            expected=self.expected_cookie_params,
            url=connection.url,
        )

        if not self.expected_reserved_kwargs:
            return {**path_params, **query_params, **header_params, **cookie_params}

        reserved_kwargs: Dict[str, Any] = {}
        if "state" in self.expected_reserved_kwargs:
            reserved_kwargs["state"] = connection.app.state.copy()
        if "headers" in self.expected_reserved_kwargs:
            reserved_kwargs["headers"] = connection.headers
        if "cookies" in self.expected_reserved_kwargs:
            reserved_kwargs["cookies"] = connection.cookies
        if "query" in self.expected_reserved_kwargs:
            reserved_kwargs["query"] = connection_query_params
        if "request" in self.expected_reserved_kwargs:
            reserved_kwargs["request"] = connection
        if "socket" in self.expected_reserved_kwargs:
            reserved_kwargs["socket"] = connection
        if "data" in self.expected_reserved_kwargs:
            reserved_kwargs["data"] = self._get_request_data(request=cast("Request", connection))
        return {
            **reserved_kwargs,
            **path_params,
            **query_params,
            **header_params,
            **cookie_params,
        }

    @staticmethod
    def _collect_params(
        params: Mapping[str, Any], expected: Set[ParameterDefinition], url: URL
    ) -> Dict[str, Any]:
        """Collects request params, checking for missing required values."""
        missing_params = [
            p.field_alias for p in expected if p.is_required and p.field_alias not in params
        ]
        if missing_params:
            raise ValidationErrorException(
                f"Missing required parameter(s) {', '.join(missing_params)} for url {url}"
            )
        return {p.field_name: params.get(p.field_alias, p.default_value) for p in expected}

    async def resolve_dependency(
        self,
        dependency: "Dependency",
        connection: Union["WebSocket", "Request"],
        **kwargs: Any,
    ) -> Any:
        signature_model = get_signature_model(dependency.inject)
        for sub_dependency in dependency.dependencies:
            kwargs[sub_dependency.key] = await self.resolve_dependency(
                dependency=sub_dependency, connection=connection, **kwargs
            )
        dependency_kwargs = signature_model.parse_values_from_connection_kwargs(
            connection=connection, **kwargs
        )
        return await dependency.inject(**dependency_kwargs)

    @classmethod
    def _create_dependency_graph(cls, key: str, dependencies: Dict[str, Inject]) -> Dependency:
        inject = dependencies[key]
        sub_dependency_keys = [
            k for k in get_signature_model(inject).__fields__ if k in dependencies
        ]
        return Dependency(
            key=key,
            inject=inject,
            dependencies=[
                cls._create_dependency_graph(key=k, dependencies=dependencies)
                for k in sub_dependency_keys
            ],
        )

    @staticmethod
    def _create_parameter_definition(
        allow_none: bool,
        field_info: FieldInfo,
        field_name: str,
        path_parameters: Set[str],
        is_sequence: bool,
    ) -> ParameterDefinition:
        extra = field_info.extra
        is_required = extra.get(EXTRA_KEY_REQUIRED, True)
        default_value = field_info.default if field_info.default is not Undefined else None

        field_alias = extra.get(ParamType.QUERY) or field_name
        param_type = getattr(field_info, "in_", ParamType.QUERY)

        if field_name in path_parameters:
            field_alias = field_name
            param_type = ParamType.PATH
        elif extra.get(ParamType.HEADER):
            field_alias = extra[ParamType.HEADER]
            param_type = ParamType.HEADER
        elif extra.get(ParamType.COOKIE):
            field_alias = extra[ParamType.COOKIE]
            param_type = ParamType.COOKIE

        return ParameterDefinition(
            param_type=param_type,
            field_name=field_name,
            field_alias=field_alias,
            default_value=default_value,
            is_required=is_required and (default_value is None and not allow_none),
            is_sequence=is_sequence,
            field_info=field_info,
        )

    @classmethod
    def _validate_dependency_data(
        cls,
        expected_form_data: Optional[Tuple[EncodingType, ModelField]],
        dependency_kwargs_model: "KwargsModel",
    ) -> None:
        if (expected_form_data and not dependency_kwargs_model.expected_form_data) or (
            not expected_form_data and dependency_kwargs_model.expected_form_data
        ):
            raise ImproperlyConfigured(
                "Dependencies have incompatible 'data' kwarg types: one expects JSON and the other expects form-data"
            )
        if expected_form_data and dependency_kwargs_model.expected_form_data:
            local_media_type, _ = expected_form_data
            dependency_media_type, _ = dependency_kwargs_model.expected_form_data
            if local_media_type != dependency_media_type:
                raise ImproperlyConfigured(
                    "Dependencies have incompatible form-data encoding: one expects url-encoded and the other expects multi-part"
                )

    @classmethod
    def _validate_raw_kwargs(
        cls,
        path_parameters: Set[str],
        dependencies: Dict[str, Inject],
        model_fields: Dict[str, ModelField],
    ) -> None:
        dependency_keys = set(dependencies.keys())

        parameter_names = {
            *(
                k
                for k, f in model_fields.items()
                if f.field_info.extra.get(ParamType.QUERY)
                or f.field_info.extra.get(ParamType.HEADER)
                or f.field_info.extra.get(ParamType.COOKIE)
            ),
        }

        for intersection in [
            path_parameters.intersection(dependency_keys)
            or path_parameters.intersection(parameter_names)
            or dependency_keys.intersection(parameter_names)
        ]:
            if intersection:
                raise ImproperlyConfigured(
                    f"Kwarg resolution ambiguity detected for the following keys: {', '.join(intersection)}. "
                    f"Make sure to use distinct keys for your dependencies, path parameters and aliased parameters."
                )

        used_reserved_kwargs = {
            *parameter_names,
            *path_parameters,
            *dependency_keys,
        }.intersection(RESERVED_KWARGS)
        if used_reserved_kwargs:
            raise ImproperlyConfigured(
                f"Reserved kwargs ({', '.join(RESERVED_KWARGS)}) cannot be used for dependencies and parameter arguments. "
                f"The following kwargs have been used: {', '.join(used_reserved_kwargs)}"
            )

    def _sequence_or_scalar_param(self, key: str, value: List[str]) -> Union[str, List[str]]:
        return (
            value[0]
            if key not in self.sequence_query_parameter_names and len(value) == 1
            else value
        )

    async def _get_request_data(self, request: "Request") -> Any:
        if self.expected_form_data:
            media_type, model_field = self.expected_form_data
            form_data = await request.form()
            parsed_form = parse_form_data(
                media_type=media_type, form_data=form_data, field=model_field
            )
            return parsed_form if parsed_form or not self.is_data_optional else None
        return await request.json()
