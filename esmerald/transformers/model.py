from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Set, Tuple, Type, Union, cast

from pydantic.fields import FieldInfo

from esmerald.context import Context
from esmerald.enums import EncodingType, ParamType
from esmerald.exceptions import ImproperlyConfigured
from esmerald.parsers import ArbitraryExtraBaseModel, parse_form_data
from esmerald.requests import Request
from esmerald.transformers.signature import SignatureModel
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
    """
    Represents a transformer model with parameters and dependencies.

    Attributes:
        cookies (Set[ParamSetting]): Set of cookie parameters.
        dependencies (Set[Dependency]): Set of dependencies.
        form_data (Optional[Tuple[EncodingType, FieldInfo]]): Optional form data information.
        headers (Set[ParamSetting]): Set of header parameters.
        path_params (Set[ParamSetting]): Set of path parameters.
        query_params (Set[ParamSetting]): Set of query parameters.
        reserved_kwargs (Set[str]): Set of reserved keyword arguments.
        has_kwargs (bool): Flag indicating if any kwargs are present.
        is_optional (bool): Flag indicating if the model is optional.
    """

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
        """
        Initialize a TransformerModel instance.

        Args:
            cookies (Set[ParamSetting]): Set of cookie parameters.
            dependencies (Set[Dependency]): Set of dependencies.
            form_data (Optional[Tuple[EncodingType, FieldInfo]]): Optional form data information.
            headers (Set[ParamSetting]): Set of header parameters.
            path_params (Set[ParamSetting]): Set of path parameters.
            query_params (Set[ParamSetting]): Set of query parameters.
            reserved_kwargs (Set[str]): Set of reserved keyword arguments.
            is_optional (bool): Flag indicating if the model is optional.
            **kwargs (Any): Additional keyword arguments.
        """
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
        """
        Get cookie parameters.

        Returns:
            Set[ParamSetting]: Set of cookie parameters.
        """
        return self.cookies

    def get_path_params(self) -> Set[ParamSetting]:
        """
        Get path parameters.

        Returns:
            Set[ParamSetting]: Set of path parameters.
        """
        return self.path_params

    def get_query_params(self) -> Set[ParamSetting]:
        """
        Get query parameters.

        Returns:
            Set[ParamSetting]: Set of query parameters.
        """
        return self.query_params

    def get_header_params(self) -> Set[ParamSetting]:
        """
        Get header parameters.

        Returns:
            Set[ParamSetting]: Set of header parameters.
        """
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

    async def get_request_data(self, request: Request) -> Any:
        """
        Get request data asynchronously.

        Args:
            request (Request): HTTP Request object.

        Returns:
            Any: Parsed form data or JSON payload.
        """
        if not self.form_data:
            return await request.json()

        media_type, field = self.form_data
        form_data = await request.form()
        parsed_form = parse_form_data(media_type, form_data, field)
        return parsed_form if parsed_form or not self.is_optional else None

    def get_request_context(
        self, handler: Union["HTTPHandler", "WebSocketHandler"], request: Request
    ) -> Context:
        """
        Get request context.

        Args:
            handler (Union[HTTPHandler, WebSocketHandler]): HTTP or WebSocket handler.
            request (Request): HTTP Request object.

        Returns:
            Context: Context object containing handler and request information.
        """
        return Context(__handler__=handler, __request__=request)

    async def get_dependencies(
        self, dependency: Dependency, connection: Union["WebSocket", Request], **kwargs: Any
    ) -> Any:
        """
        Get dependencies asynchronously.

        Args:
            dependency (Dependency): Dependency object.
            connection (Union[WebSocket, Request]): WebSocket or HTTP Request object.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            Any: Dependencies resolved from the connection and dependencies.
        """
        signature_model = get_signature(dependency.inject)
        for _dependency in dependency.dependencies:
            kwargs[_dependency.key] = await self.get_dependencies(
                dependency=_dependency, connection=connection, **kwargs
            )
        dependency_kwargs = signature_model.parse_values_for_connection(
            connection=connection, **kwargs
        )
        return await dependency.inject(**dependency_kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert TransformerModel instance to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of TransformerModel instance.
        """
        return {
            "cookies": [param.dict() for param in self.cookies],
            "dependencies": [dep.dict() for dep in self.dependencies],
            "form_data": self.form_data,
            "headers": [param.dict() for param in self.headers],
            "path_params": [param.dict() for param in self.path_params],
            "query_params": [param.dict() for param in self.query_params],
            "reserved_kwargs": list(self.reserved_kwargs),
            "is_optional": self.is_optional,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransformerModel":
        """
        Create TransformerModel instance from dictionary.

        Args:
            data (Dict[str, Any]): Dictionary containing TransformerModel attributes.

        Returns:
            TransformerModel: TransformerModel instance created from dictionary.
        """
        return cls(
            cookies={ParamSetting(**param) for param in data.get("cookies", [])},
            dependencies={Dependency(**dep) for dep in data.get("dependencies", [])},
            form_data=data.get("form_data"),
            headers={ParamSetting(**param) for param in data.get("headers", [])},
            path_params={ParamSetting(**param) for param in data.get("path_params", [])},
            query_params={ParamSetting(**param) for param in data.get("query_params", [])},
            query_param_names={
                ParamSetting(**param) for param in data.get("query_param_names", [])
            },
            reserved_kwargs=set(data.get("reserved_kwargs", [])),
            is_optional=data.get("is_optional", False),
        )

    def merge_with(self, other: "TransformerModel") -> "TransformerModel":
        """
        Merge with another TransformerModel instance.

        Args:
            other (TransformerModel): Another TransformerModel instance to merge with.

        Returns:
            TransformerModel: Merged TransformerModel instance.
        """
        return TransformerModel(
            cookies=merge_sets(self.cookies, other.cookies),
            dependencies=merge_sets(self.dependencies, other.dependencies),  # type: ignore
            form_data=self.form_data if self.form_data == other.form_data else None,
            headers=merge_sets(self.headers, other.headers),
            path_params=merge_sets(self.path_params, other.path_params),
            query_params=merge_sets(self.query_params, other.query_params),
            query_param_names=merge_sets(self.query_param_names, other.query_param_names),
            reserved_kwargs=self.reserved_kwargs.union(other.reserved_kwargs),
            is_optional=self.is_optional or other.is_optional,
        )

    def _get_request_params(
        self,
        connection: Union["WebSocket", "Request"],
        handler: Union["HTTPHandler", "WebSocketHandler"] = None,
    ) -> Any:
        """
        Get request parameters.

        Args:
            connection (Union["WebSocket", "Request"]): Connection object.
            handler (Union["HTTPHandler", "WebSocketHandler"], optional): Handler object. Defaults to None.

        Returns:
            Any: Request parameters.
        """
        connection_params: Dict[str, Any] = {}
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
        """
        Handle reserved keyword arguments.

        Args:
            connection (Union["WebSocket", "Request"]): Connection object.
            connection_params (Any): Connection parameters.
            path_params (Any): Path parameters.
            query_params (Any): Query parameters.
            headers (Any): Headers.
            cookies (Any): Cookies.
            handler (Optional[Any], optional): Handler object. Defaults to None.

        Returns:
            Any: Reserved keyword arguments.
        """
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


def dependency_tree(key: str, dependencies: "Dependencies") -> Dependency:
    """
    Recursively build a dependency tree starting from a given key.

    Args:
        key (str): Key of the dependency to start building from.
        dependencies (Dependencies): Dictionary of dependencies.

    Returns:
        Dependency: Constructed dependency tree starting from the specified key.
    """
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
) -> Tuple[Set[ParamSetting], Set[Dependency]]:
    """
    Get parameter settings and dependencies based on input data.

    Args:
        path_parameters (Set[str]): Set of path parameters.
        dependencies (Dict[str, Any]): Dictionary of dependencies.
        signature_fields (Dict[str, Any]): Dictionary containing field information.

    Returns:
        Tuple[Set[ParamSetting], Set[Dependency]]: Tuple containing sets of parameter settings
        and dependencies.
    """
    _dependencies: Set[Dependency] = set()
    ignored_keys = {
        *RESERVED_KWARGS,
        *(dependency.key for dependency in _dependencies),
    }
    parameter_definitions: Set[ParamSetting] = set()

    for key in dependencies:
        if key in signature_fields:
            _dependencies.add(dependency_tree(key=key, dependencies=dependencies))

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
    signature_model: Type["SignatureModel"],
) -> Optional[Tuple[EncodingType, FieldInfo]]:
    """
    Get form data from the signature model.

    Args:
        signature_model (Type[SignatureModel]): The signature model.

    Returns:
        Optional[Tuple[EncodingType, FieldInfo]]: Tuple containing media type and data
        field information, or None if not found.
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
    signature_model: Type["SignatureModel"],
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

    form_data = _get_form_data(signature_model)

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
        is_optional = is_field_optional(signature_model.model_fields[DATA])
    elif PAYLOAD in reserved_kwargs:
        is_optional = is_field_optional(signature_model.model_fields[PAYLOAD])

    query_param_names: Set[ParamSetting] = set()
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
    dependency: Dependency,
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
    local_dependencies: Set[Dependency],
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
    dependency_model: TransformerModel,
) -> None:
    """
    Validate compatibility of form data
    between two models.

    Args:
        form_data (Optional[Tuple[EncodingType, FieldInfo]]): Form data tuple containing
            media type and data field information, or None.
        dependency_model (TransformerModel): Transformer model to validate against.

    Raises:
        ImproperlyConfigured: If dependencies have incompatible form-data encoding or
            incompatible 'data' kwarg types.
    """
    if form_data and dependency_model.form_data:
        media_type, _ = form_data
        dependency_media_type, _ = dependency_model.form_data
        if media_type != dependency_media_type:
            raise ImproperlyConfigured(
                "Dependencies have incompatible form-data encoding. "
                "They should both be the same. Either url-encoded or multi-part."
            )
    if (form_data and not dependency_model.form_data) or (
        not form_data and dependency_model.form_data
    ):
        raise ImproperlyConfigured(
            "Dependencies have incompatible 'data' kwarg types. "
            "One expects JSON and the other expects form-data."
        )


def _get_names_from_model_fields(model_fields: Dict[str, FieldInfo]) -> Set[str]:
    """
    Extract names from model fields that have additional metadata relevant for parameters.

    Args:
        model_fields (Dict[str, FieldInfo]): Dictionary of model fields.

    Returns:
        Set[str]: Set of names extracted from model fields.
    """
    names = set()
    for key, value in model_fields.items():
        if value.json_schema_extra is not None:
            extra = cast(Dict[str, Any], value.json_schema_extra)
            if (
                extra.get(ParamType.QUERY)
                or extra.get(ParamType.HEADER)
                or extra.get(ParamType.COOKIE)
            ):
                names.add(key)
    return names


def _check_ambiguity_in_kwargs(
    path_parameters: Set[str], dependencies: Dict[str, Any], model_fields: Dict[str, FieldInfo]
) -> None:
    """
    Check for ambiguity in keyword argument resolution.

    Args:
        path_parameters (Set[str]): Set of path parameters.
        dependencies (Dict[str, Any]): Dependency information.
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
    dependencies: Dict[str, Any],
    model_fields: Dict[str, FieldInfo],
) -> None:
    """
    Validate keyword arguments for parameter and dependency definitions.

    Args:
        path_parameters (Set[str]): Set of path parameters.
        dependencies (Dict[str, Any]): Dependency information.
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
