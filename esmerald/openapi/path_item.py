from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, cast

from openapi_schemas_pydantic.v3_1_0.operation import Operation
from openapi_schemas_pydantic.v3_1_0.path_item import PathItem
from starlette.routing import get_name

from esmerald.enums import HttpMethod
from esmerald.openapi.parameters import create_parameter_for_handler
from esmerald.openapi.request_body import create_request_body
from esmerald.openapi.responses import create_responses

if TYPE_CHECKING:
    from openapi_schemas_pydantic.v3_1_0 import SecurityRequirement
    from pydantic import BaseModel

    from esmerald.routing.handlers import HTTPHandler
    from esmerald.types import AnyCallable


def get_description_for_handler(
    handler: "HTTPHandler", use_handler_docstrings: bool
) -> Optional[str]:
    description = handler.description
    if description is None and use_handler_docstrings:
        return handler.fn.__doc__
    return description


def extract_level_values(
    handler: "HTTPHandler",
) -> Tuple[Optional[List[str]], Optional[List[Dict[str, List[str]]]]]:
    tags: List[str] = []
    security: List["SecurityRequirement"] = []

    for layer in handler.parent_levels:
        if hasattr(layer, "tags"):
            tags.extend(layer.tags or [])
        if hasattr(layer, "security"):
            security.extend(layer.security or [])
    return list(set(tags)) if tags else None, security or None


def create_path_item(
    route: "HTTPHandler", create_examples: bool, use_handler_docstrings: bool
) -> PathItem:
    path_item = PathItem()

    # remove the HEAD from the docs
    route_map = {k: v for k, v in route.route_map.items() if k != HttpMethod.HEAD}

    for http_method, handler_tuple in route_map.items():
        handler, _ = handler_tuple

        if handler.include_in_schema:
            handler_fields = cast("BaseModel", handler.signature_model).__fields__
            parameters = (
                create_parameter_for_handler(
                    handler=handler,
                    handler_fields=handler_fields,
                    path_parameters=handler.normalised_path_params,
                    create_examples=create_examples,
                )
                or None
            )
            raises_validation_error = bool(
                "data" in handler_fields or path_item.parameters or parameters
            )
            handler_name = get_name(cast("AnyCallable", handler.fn)).replace("_", " ").title()
            request_body = None

            if "data" in handler_fields:
                request_body = create_request_body(
                    field=handler_fields["data"], create_examples=create_examples
                )

            tags, security = extract_level_values(handler=handler)
            operation = Operation(
                operationId=handler.operation_id or handler_name,
                tags=tags,
                summary=handler.summary,
                description=get_description_for_handler(handler, use_handler_docstrings),
                deprecated=handler.deprecated,
                responses=create_responses(
                    handler=handler,
                    raises_validation_error=raises_validation_error,
                    create_examples=create_examples,
                ),
                requestBody=request_body,
                parameters=parameters,
                security=security,
            )
            setattr(path_item, http_method.lower(), operation)
    return path_item
