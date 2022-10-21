from collections import defaultdict
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Type

from pydantic import BaseModel
from spectree import SpecTree
from spectree.models import Tag
from spectree.plugins import BasePlugin
from spectree.utils import get_model_key, get_security, parse_name, parse_params

from esmerald._openapi.constants import REF_PREFIX
from esmerald._openapi.plugins.esmerald_plugin import EsmeraldPlugin
from esmerald._openapi.utils import parse_request, parse_resp

if TYPE_CHECKING:
    from esmerald.applications import Esmerald


validation_error_definition = {
    "title": "ValidationError",
    "type": "object",
    "properties": {
        "loc": {
            "title": "Location",
            "type": "array",
            "items": {"anyOf": [{"type": "string"}, {"type": "integer"}]},
        },
        "msg": {"title": "Message", "type": "string"},
        "type": {"title": "Error Type", "type": "string"},
    },
    "required": ["loc", "msg", "type"],
}

validation_error_response_definition = {
    "title": "HTTPValidationError",
    "type": "object",
    "properties": {
        "detail": {
            "title": "Detail",
            "type": "array",
            "items": {"$ref": REF_PREFIX + "ValidationError"},
        }
    },
}


class OpenAPI(SpecTree):
    """
    Extends the existing functionality of Spectree to Esmerald.
    """

    def __init__(
        self,
        backend_name: str = "base",
        backend: Optional[Type[BasePlugin]] = EsmeraldPlugin,
        app: "Esmerald" = None,
        before: Callable = ...,
        after: Callable = ...,
        validation_error_status: int = 422,
        **kwargs: Any,
    ):
        super().__init__(
            backend_name, backend, app, before, after, validation_error_status, **kwargs
        )

    def _generate_spec(self) -> Dict[str, Any]:
        """
        generate OpenAPI spec according to routes and decorators
        """
        routes: Dict[str, Dict] = defaultdict(dict)
        tags = {}
        operation_ids = set()

        for route in self.backend.find_routes():
            for method, func, handler in self.backend.parse_func(route):
                if self.backend.bypass(func, method) or self.bypass(func):
                    continue

                path_parameter_descriptions = getattr(func, "path_parameter_descriptions", None)
                path, parameters = self.backend.parse_path(route, path_parameter_descriptions)

                fields = {k: v for k, v in handler.signature_model.__fields__.items()}

                field_names = []
                for field, model in fields.items():
                    if model.type_ == Any:
                        continue
                    if issubclass(model.type_, BaseModel):
                        model_key = self._add_model(model=model.type_)
                    else:
                        model_key = get_model_key(model=model.type_)
                    field_names.append({field: model_key})

                name = parse_name(func)
                handler_tags = getattr(handler, "tags", ())
                for tag in handler_tags:
                    if str(tag) not in tags:
                        tags[str(tag)] = tag.dict() if isinstance(tag, Tag) else {"name": tag}

                if handler.operation_id in operation_ids:
                    operation_id = f"{handler.operation_id}_{method.lower()}_{path}"
                else:
                    operation_id = handler.operation_id

                operation_ids.add(operation_id)
                routes[path][method.lower()] = {}
                responses = getattr(handler, "responses", None)
                if not responses:
                    handler.responses = {
                        handler.status_code: {"description": handler.response_description}
                    }

                request_body = parse_request(field_names)
                routes.update(
                    {
                        path: {
                            method.lower(): {
                                "summary": handler.summary or f"{name}",
                                "operationId": operation_id,
                                "description": handler.description or "",
                                "tags": [str(x) for x in getattr(handler, "tags", ())],
                                "responses": parse_resp(handler),
                                "security": get_security(handler.security) or [],
                                "deprecated": handler.deprecated,
                                "requestBody": request_body,
                                "parameters": parse_params(func, parameters[:], self.models),
                            }
                        }
                    }
                )

        spec: Dict[str, Any] = {
            "openapi": self.config.openapi_version,
            "info": self.config.openapi_info(),
            "tags": list(tags.values()),
            "paths": {**routes},
        }

        try:
            spec.update(
                {"components": {"schemas": {**self.models, **self._get_model_definitions()}}}
            )

        except UnboundLocalError:
            ...

        if self.config.servers:
            spec["servers"] = [server.dict(exclude_none=True) for server in self.config.servers]

        if self.config.security_schemes:
            spec["components"]["securitySchemes"] = {
                scheme.name: scheme.data.dict(exclude_none=True, by_alias=True)
                for scheme in self.config.security_schemes
            }

        spec["security"] = get_security(self.config.security)
        return spec

    def _get_model_definitions(self) -> Dict[str, Any]:
        """
        Handle the definitions for the models.
        """
        definitions = super()._get_model_definitions()
        if "ValidationError" not in definitions:
            definitions.update(
                {
                    "ValidationError": validation_error_definition,
                    "HTTPValidationError": validation_error_response_definition,
                }
            )
        return definitions
