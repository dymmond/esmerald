from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Set, Tuple, Type, Union, cast

from pydantic.fields import FieldInfo

from esmerald.context import Context
from esmerald.enums import EncodingType, ParamType
from esmerald.exceptions import ImproperlyConfigured
from esmerald.parsers import ArbitraryExtraBaseModel, parse_form_data
from esmerald.requests import Request
from esmerald.transformers.datastructures import EsmeraldSignature as SignatureModel
from esmerald.transformers.utils import (
    Dependency,
    ParamSetting,
    create_parameter_setting,
    get_request_params,
    get_signature,
    merge_sets,
)
from esmerald.utils.constants import CONTEXT, DATA, PAYLOAD, RESERVED_KWARGS
from esmerald.utils.pydantic.schema import is_field_optional

if TYPE_CHECKING:
    from esmerald.routing.router import HTTPHandler, WebSocketHandler
    from esmerald.types import Dependencies  # pragma: no cover
    from esmerald.websockets import WebSocket  # pragma: no cover


MEDIA_TYPES = [EncodingType.MULTI_PART, EncodingType.URL_ENCODED]
MappingUnion = Mapping[Union[int, str], Any]


class TransformerModel(ArbitraryExtraBaseModel):
    def __init__(
        self,
        cookies: Set[ParamSetting],
        dependencies: Set[Dependency],
        form_data: Optional[Tuple[EncodingType, FieldInfo]],
        headers: Set[ParamSetting],
        path_params: Set[ParamSetting],
        query_params: Set[ParamSetting],
        reserved_kwargs: Set[str],
        query_param_names: Set[ParamSetting],
        is_optional: bool,
        **kwargs: Any,
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
        self.is_optional = is_optional

    def get_cookie_params(self) -> Set[ParamSetting]:
        return self.cookies

    def get_path_params(self) -> Set[ParamSetting]:
        return self.path_params

    def get_query_params(self) -> Set[ParamSetting]:
        return self.query_params

    def get_header_params(self) -> Set[ParamSetting]:
        return self.headers

    def to_kwargs(
        self,
        connection: Union["WebSocket", "Request"],
        handler: Union["HTTPHandler", "WebSocketHandler"] = None,
    ) -> Any:
        connection_params = {}
        for key, value in connection.query_params.items():
            if key not in self.query_param_names and len(value) == 1:
                value = value[0]
                connection_params[key] = value

        query_params = get_request_params(
            params=cast("MappingUnion", connection.query_params),
            expected=self.query_params,
            url=connection.url,
        )
        path_params = get_request_params(
            params=cast("MappingUnion", connection.path_params),
            expected=self.path_params,
            url=connection.url,
        )
        headers = get_request_params(
            params=cast("MappingUnion", connection.headers),
            expected=self.headers,
            url=connection.url,
        )
        cookies = get_request_params(
            params=cast("MappingUnion", connection.cookies),
            expected=self.cookies,
            url=connection.url,
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
            handler=handler,
        )

    def handle_reserved_kwargs(
        self,
        connection: Union["WebSocket", "Request"],
        connection_params: Any,
        path_params: Any,
        query_params: Any,
        headers: Any,
        cookies: Any,
        handler: Optional[Any] = None,
    ) -> Any:
        reserved_kwargs: Any = {}
        if DATA in self.reserved_kwargs:
            reserved_kwargs[DATA] = self.get_request_data(request=cast("Request", connection))
        if PAYLOAD in self.reserved_kwargs:
            reserved_kwargs[PAYLOAD] = self.get_request_data(request=cast("Request", connection))

        if CONTEXT in self.reserved_kwargs and handler is not None:
            reserved_kwargs[CONTEXT] = self.get_request_context(
                handler=handler, request=cast("Request", connection)
            )

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
            reserved_kwargs["state"] = connection.app.state.copy()  # pragma: no cover

        return {**reserved_kwargs, **path_params, **query_params, **headers, **cookies}

    async def get_request_data(self, request: "Request") -> Any:
        # Fast exit principle
        if not self.form_data:
            return await request.json()

        media_type, field = self.form_data
        form_data = await request.form()
        parsed_form = parse_form_data(media_type, form_data, field)
        return parsed_form if parsed_form or not self.is_optional else None

    def get_request_context(
        self, handler: Union["HTTPHandler", "WebSocketHandler"], request: "Request"
    ) -> Context:
        """
        Generates the context of the handler where additional information can be provided and passed properly.
        """
        return Context(__handler__=handler, __request__=request)

    async def get_dependencies(
        self,
        dependency: "Dependency",
        connection: Union["WebSocket", "Request"],
        **kwargs: Any,
    ) -> Any:
        signature_model = get_signature(dependency.inject)
        for _dependency in dependency.dependencies:
            kwargs[_dependency.key] = await self.get_dependencies(
                dependency=_dependency, connection=connection, **kwargs
            )
        dependency_kwargs = signature_model.parse_values_for_connection(
            connection=connection, **kwargs
        )
        return await dependency.inject(**dependency_kwargs)


def dependency_tree(key: str, dependencies: "Dependencies") -> Dependency:
    inject = dependencies[key]
    dependency_keys = [key for key in get_signature(inject).model_fields if key in dependencies]
    return Dependency(
        key=key,
        inject=inject,
        dependencies=[
            dependency_tree(key=key, dependencies=dependencies) for key in dependency_keys
        ],
    )


def get_parameter_settings(
    path_parameters: Set[str], dependencies: Dict[str, Any], signature_fields: Dict[str, Any]
) -> Tuple[Set[ParamSetting], Set["Dependency"]]:
    """
    Get parameter settings and dependencies for given inputs.

    Args:
        path_parameters (set): Set of path parameters.
        dependencies (dict): Dependency information.
        signature_fields (dict): Dictionary containing field information.

    Returns:
        tuple: A tuple containing sets of parameter settings and dependencies.
    """

    # Set to store dependencies
    _dependencies: Any = set()

    # Set to store ignored keys
    ignored_keys = {
        *RESERVED_KWARGS,
        *(dependency.key for dependency in _dependencies),
    }

    # Set to store parameter definitions
    parameter_definitions = set()

    # Iterate through dependencies to add relevant dependencies
    for key in dependencies:
        if key in signature_fields:
            _dependencies.add(dependency_tree(key=key, dependencies=dependencies))

    # Iterate through signature fields to create parameter settings
    for field_name, model_field in signature_fields.items():
        if field_name not in ignored_keys:
            allow_none = getattr(model_field, "allow_none", True)
            parameter_definitions.add(
                create_parameter_setting(
                    allow_none=allow_none,
                    field_name=field_name,
                    field_info=model_field,
                    path_parameters=path_parameters,
                )
            )

    # Filter out ignored keys and create parameter settings
    filtered = [
        (field_name, model_field)
        for field_name, model_field in signature_fields.items()
        if field_name not in ignored_keys
    ]
    for field_name, model_field in filtered:
        signature_field = model_field
        allow_none = getattr(signature_field, "allow_none", True)
        parameter_definitions.add(
            create_parameter_setting(
                allow_none=allow_none,
                field_name=field_name,
                field_info=signature_field,
                path_parameters=path_parameters,
            )
        )

    return parameter_definitions, _dependencies


def _filter_param_settings_by_type(
    param_settings: Set[ParamSetting], param_type: ParamType
) -> Set[ParamSetting]:
    """
    Filter parameter settings by parameter type.

    Args:
        param_settings (Set[ParamSetting]): Set of parameter settings.
        param_type (ParamType): Parameter type to filter.

    Returns:
        Set[ParamSetting]: Filtered parameter settings.
    """
    return {param for param in param_settings if param.param_type == param_type}


def _get_form_data(
    signature_model: Type[SignatureModel],
) -> Optional[Tuple["EncodingType", "FieldInfo"]]:
    """
    Get form data from the signature model.

    Args:
        signature_model (Type[SignatureModel]): The signature model.

    Returns:
        Optional[Tuple[str, Any]]: Tuple containing media type and data field, or None.
    """
    data_field = signature_model.model_fields.get(DATA) or signature_model.model_fields.get(
        PAYLOAD
    )
    if data_field:
        extra = getattr(data_field, "json_schema_extra", None) or {}
        media_type = extra.get("media_type")
        if media_type in MEDIA_TYPES:
            return media_type, data_field
    return None


def create_signature(
    signature_model: Type[SignatureModel],
    dependencies: "Dependencies",
    path_parameters: Set[str],
) -> "TransformerModel":
    """
    Create a transformer model based on the signature model.

    Args:
        signature_model (Type[SignatureModel]): The signature model.
        dependencies (Dependencies): Dependency information.
        path_parameters (Set[str]): Set of path parameters.

    Returns:
        TransformerModel: The created transformer model.
    """
    validate_kwargs(
        path_parameters=path_parameters,
        dependencies=dependencies,
        model_fields=signature_model.model_fields,
    )

    reserved_kwargs = {
        field_name for field_name in signature_model.model_fields if field_name in RESERVED_KWARGS
    }

    param_settings, _dependencies = get_parameter_settings(
        path_parameters=path_parameters,
        dependencies=dependencies,
        signature_fields=signature_model.model_fields,
    )

    path_params = _filter_param_settings_by_type(param_settings, ParamType.PATH)
    query_params = _filter_param_settings_by_type(param_settings, ParamType.QUERY)
    cookies = _filter_param_settings_by_type(param_settings, ParamType.COOKIE)
    headers = _filter_param_settings_by_type(param_settings, ParamType.HEADER)

    form_data: Union[Tuple["EncodingType", "FieldInfo"], None] = _get_form_data(signature_model)

    # Update parameters
    (
        path_params,
        query_params,
        cookies,
        headers,
        reserved_kwargs,
    ) = update_parameters(
        global_dependencies=dependencies,
        local_dependencies=_dependencies,
        path_params=path_params,
        query_params=query_params,
        cookies=cookies,
        headers=headers,
        reserved_kwargs=reserved_kwargs,
        path_parameters=path_parameters,
        form_data=form_data,
    )

    is_optional = False
    if DATA in reserved_kwargs and PAYLOAD in reserved_kwargs:
        raise ImproperlyConfigured("Only 'data' or 'payload' must be provided but not both.")

    if DATA in reserved_kwargs:
        is_optional = is_field_optional(signature_model.model_fields["data"])
    elif PAYLOAD in reserved_kwargs:
        is_optional = is_field_optional(signature_model.model_fields["payload"])

    query_param_names: Any = set()
    return TransformerModel(
        form_data=form_data,
        dependencies=_dependencies,
        path_params=path_params,
        query_params=query_params,
        cookies=cookies,
        headers=headers,
        reserved_kwargs=reserved_kwargs,
        query_param_names=query_param_names,
        is_optional=is_optional,
    )


def _update_parameters_with_dependency(
    dependency: "Dependency",
    global_dependencies: "Dependencies",
    path_params: Any,
    query_params: Any,
    cookies: Any,
    headers: Any,
    reserved_kwargs: Any,
    path_parameters: Any,
    form_data: Any,
) -> Tuple[Any, Any, Any, Any, Any]:
    """
    Update parameters based on a dependency.

    Args:
        dependency (Dependency): The dependency to process.
        global_dependencies (Dependencies): Global dependency information.
        path_params (Any): Existing path parameters.
        query_params (Any): Existing query parameters.
        cookies (Any): Existing cookies.
        headers (Any): Existing headers.
        reserved_kwargs (Any): Existing reserved keywords.
        path_parameters (Any): Path parameters.
        form_data (Any): Form data.

    Returns:
        Tuple[Any, Any, Any, Any, Any]: Updated parameters.
    """
    dependency_model = create_signature(
        signature_model=get_signature(dependency.inject),
        dependencies=global_dependencies,
        path_parameters=path_parameters,
    )
    path_params = merge_sets(path_params, dependency_model.path_params)
    query_params = merge_sets(query_params, dependency_model.query_params)
    cookies = merge_sets(cookies, dependency_model.cookies)
    headers = merge_sets(headers, dependency_model.headers)

    if DATA in reserved_kwargs and DATA in dependency_model.reserved_kwargs:
        validate_data(form_data, dependency_model)
    elif PAYLOAD in reserved_kwargs and PAYLOAD in dependency_model.reserved_kwargs:
        validate_data(form_data, dependency_model)
    reserved_kwargs.update(dependency_model.reserved_kwargs)

    return path_params, query_params, cookies, headers, reserved_kwargs


def update_parameters(
    global_dependencies: "Dependencies",
    local_dependencies: Set["Dependency"],
    path_params: Any,
    query_params: Any,
    cookies: Any,
    headers: Any,
    reserved_kwargs: Any,
    path_parameters: Any,
    form_data: Any,
) -> Tuple[Any, Any, Any, Any, Any]:
    """
    Update parameters with local dependencies.

    Args:
        global_dependencies (Dependencies): Global dependency information.
        local_dependencies (Set[Dependency]): Local dependency set.
        path_params (Any): Existing path parameters.
        query_params (Any): Existing query parameters.
        cookies (Any): Existing cookies.
        headers (Any): Existing headers.
        reserved_kwargs (Any): Existing reserved keywords.
        path_parameters (Any): Path parameters.
        form_data (Any): Form data.

    Returns:
        Tuple[Any, Any, Any, Any, Any]: Updated parameters.
    """
    for dependency in local_dependencies:
        path_params, query_params, cookies, headers, reserved_kwargs = (
            _update_parameters_with_dependency(
                dependency,
                global_dependencies,
                path_params,
                query_params,
                cookies,
                headers,
                reserved_kwargs,
                path_parameters,
                form_data,
            )
        )

    return path_params, query_params, cookies, headers, reserved_kwargs


def validate_data(
    form_data: Optional[Tuple[EncodingType, FieldInfo]],
    dependency_model: "TransformerModel",
) -> None:  # pragma: no cover
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


def _get_names_from_model_fields(model_fields: Dict[str, FieldInfo]) -> Set[str]:
    """
    Extract names from model fields.

    Args:
        model_fields (Dict[str, FieldInfo]): Dictionary of model fields.

    Returns:
        Set[str]: Set of names extracted from model fields.
    """
    names = set()
    for key, value in model_fields.items():
        if value.json_schema_extra is not None:
            extra = cast("Dict[str, Any]", value.json_schema_extra)
            if (
                extra.get(ParamType.QUERY)
                or extra.get(ParamType.HEADER)
                or extra.get(ParamType.COOKIE)
            ):
                names.add(key)
    return names


def _check_ambiguity_in_kwargs(
    path_parameters: Set[str], dependencies: "Dependencies", model_fields: Dict[str, FieldInfo]
) -> None:
    """
    Check ambiguity in keyword argument resolution.

    Args:
        path_parameters (Set[str]): Set of path parameters.
        dependencies (Dependencies): Dependency information.
        model_fields (Dict[str, FieldInfo]): Dictionary of model fields.

    Raises:
        ImproperlyConfigured: If ambiguity in keyword argument resolution is detected.
    """
    keys = set(dependencies.keys())
    names = _get_names_from_model_fields(model_fields)

    intersection = (
        path_parameters.intersection(keys)
        or path_parameters.intersection(names)
        or keys.intersection(names)
    )
    if intersection:
        raise ImproperlyConfigured(
            f"Ambiguity in kwarg resolution: {', '.join(intersection)}. "
            f"Please make sure to use unique distinct keys for your dependencies and path parameters."
        )


def validate_kwargs(
    path_parameters: Set[str],
    dependencies: "Dependencies",
    model_fields: Dict[str, FieldInfo],
) -> None:
    """
    Validate keyword arguments.

    Args:
        path_parameters (Set[str]): Set of path parameters.
        dependencies (Dependencies): Dependency information.
        model_fields (Dict[str, FieldInfo]): Dictionary of model fields.

    Raises:
        ImproperlyConfigured: If keyword arguments are invalid.
    """
    _check_ambiguity_in_kwargs(path_parameters, dependencies, model_fields)

    reserved_kwargs = {
        *_get_names_from_model_fields(model_fields),
        *path_parameters,
        *dependencies.keys(),
    }.intersection(RESERVED_KWARGS)
    if reserved_kwargs:
        raise ImproperlyConfigured(
            f"Kwargs ({', '.join(RESERVED_KWARGS)}) cannot be used for parameters and/or dependencies."
        )
