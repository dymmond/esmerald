import http.client
import inspect
import warnings
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)

from pydantic.fields import FieldInfo
from starlette.responses import JSONResponse
from starlette.routing import BaseRoute
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from typing_extensions import Literal

from esmerald._openapi._utils import (
    JsonSchema,
    get_schema_from_model_field,
    status_code_ranges,
    validation_error_definition,
    validation_error_response_definition,
)
from esmerald._openapi.constants import METHODS_WITH_BODY, REF_PREFIX, REF_TEMPLATE
from esmerald._openapi.models import Contact, License, OpenAPI, Server, Tag
from esmerald.params import Body, Param
from esmerald.responses import Response
from esmerald.routing import gateways, router
from esmerald.transformers.model import TransformerModel
from esmerald.typing import ModelMap, Undefined
from esmerald.utils.constants import DATA

if TYPE_CHECKING:
    from esmerald.applications import Esmerald


def get_flat_params(route: BaseRoute) -> List[Any]:
    """Gets all the neded params of the request and route"""
    path_params = [param.field_info for param in route.transformer.get_path_params()]
    cookie_params = [param.field_info for param in route.transformer.get_cookie_params()]
    query_params = [param.field_info for param in route.transformer.get_query_params()]
    header_params = [param.field_info for param in route.transformer.get_header_params()]

    return path_params + query_params + cookie_params + header_params


def get_fields_from_routes(
    routes: Sequence[BaseRoute], request_fields: Optional[List[FieldInfo]] = None
) -> List[FieldInfo]:
    """Extracts the fields from the given routes of Esmerald"""
    body_fields: List[FieldInfo] = []
    response_from_routes: List[FieldInfo] = []
    request_fields: List[FieldInfo] = []

    for route in routes:
        if getattr(route, "include_in_schema", None) and isinstance(route, router.Include):
            request_fields = get_fields_from_routes(route.routes, request_fields)
            continue

        if getattr(route, "include_in_schema", None) and isinstance(route, gateways.Gateway):
            if DATA in route.handler.signature_model.__fields__:
                data_field = route.handler.signature_model.__fields__["data"]
                body_fields.append(data_field)
            if route.handler.responses:
                response_from_routes.append(route.handler.responses.values())
            params = get_flat_params(route.handler)
            request_fields.append(params)
    return list(body_fields + response_from_routes + request_fields)


def get_openapi(
    *,
    title: str,
    version: str,
    openapi_version: str = "3.1.0",
    summary: Optional[str] = None,
    description: Optional[str] = None,
    routes: Sequence[BaseRoute],
    tags: Optional[List[Tag]] = None,
    servers: Optional[List[Server]] = None,
    terms_of_service: Optional[str] = None,
    contact: Optional[Contact] = None,
    license: Optional[License] = None,
) -> Dict[str, Any]:
    """
    Builds the whole OpenAPI route structure and object
    """
    info: Dict[str, Any] = {"title": title, "version": version}
    if summary:
        info["summary"] = summary
    if description:
        info["description"] = description
    if terms_of_service:
        info["termsOfService"] = terms_of_service
    if contact:
        info["contact"] = contact
    if license:
        info["license"] = license
    output: Dict[str, Any] = {"openapi": openapi_version, "info": info}

    if servers:
        output["servers"] = servers

    components: Dict[str, Dict[str, Any]] = {}
    paths: Dict[str, Dict[str, Any]] = {}
    operation_ids: Set[str] = set()
    all_fields = get_fields_from_routes(list(routes or []))
    # breakpoint()
    model_name_map = get_compat_model_name_map(all_fields)
    schema_generator = JsonSchema(ref_template=REF_TEMPLATE)
    field_mapping, definitions = get_definitions(
        fields=all_fields,
        schema_generator=schema_generator,
        model_name_map=model_name_map,
    )

    # Iterate through the routes
    for route in routes:
        if isinstance(route, Gateway):
            result = get_openapi_path(
                route=route,
                operation_ids=operation_ids,
                schema_generator=schema_generator,
                model_name_map=model_name_map,
                field_mapping=field_mapping,
            )
            if result:
                path, security_schemes, path_definitions = result
                if path:
                    paths.setdefault(route.path_format, {}).update(path)
                if security_schemes:
                    components.setdefault("securitySchemes", {}).update(security_schemes)
                if path_definitions:
                    definitions.update(path_definitions)

    if definitions:
        components["schemas"] = {k: definitions[k] for k in sorted(definitions)}
    if components:
        output["components"] = components
    output["paths"] = paths
    if tags:
        output["tags"] = tags

    openapi = OpenAPI(**output)
    return openapi.model_json_schema(by_alias=True)
