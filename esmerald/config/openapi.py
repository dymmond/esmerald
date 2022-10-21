from typing import TYPE_CHECKING, Dict, List, Optional, Set, Type, Union, cast

from esmerald.openapi.path_item import create_path_item
from esmerald.routing.gateways import Gateway
from esmerald.routing.router import Include
from openapi_schema_pydantic.v3.v3_1_0 import (
    Components,
    Contact,
    ExternalDocumentation,
    Info,
    License,
    OpenAPI,
    PathItem,
    Reference,
    SecurityRequirement,
    Server,
    Tag,
)
from pydantic import AnyUrl, BaseModel
from pydantic_openapi_schema import construct_open_api_with_schema_class
from typing_extensions import Literal

if TYPE_CHECKING:
    from esmerald.applications import Esmerald
    from esmerald.openapi.apiview import OpenAPIView


class OpenAPIConfig(BaseModel):
    create_examples: bool = False
    openapi_apiview: Type["OpenAPIView"]
    title: str
    version: str
    contact: Optional[Contact] = None
    description: Optional[str] = None
    external_docs: Optional[ExternalDocumentation] = None
    license: Optional[License] = None
    security: Optional[List[SecurityRequirement]] = None
    components: Optional[Union[Components, List[Components]]] = None
    servers: List[Server] = [Server(url="/")]
    summary: Optional[str] = None
    tags: Optional[List[Tag]] = None
    terms_of_service: Optional[AnyUrl] = None
    use_handler_docstrings: bool = False
    webhooks: Optional[Dict[str, Union[PathItem, Reference]]] = None
    root_schema_site: Literal["redoc", "swagger", "elements"] = "redoc"
    enabled_endpoints: Set[str] = {
        "redoc",
        "swagger",
        "elements",
        "openapi.json",
        "openapi.yaml",
    }

    def to_openapi_schema(self) -> "OpenAPI":
        if isinstance(self.components, list):
            merged_components = Components()
            for components in self.components:
                for key in components.__fields__.keys():
                    value = getattr(components, key, None)
                    if value:
                        merged_value_dict = getattr(merged_components, key, {}) or {}
                        merged_value_dict.update(value)
                        setattr(merged_components, key, merged_value_dict)
            self.components = merged_components

        return OpenAPI(
            externalDocs=self.external_docs,
            security=self.security,
            components=cast("Components", self.components),
            servers=self.servers,
            tags=self.tags,
            webhooks=self.webhooks,
            info=Info(
                title=self.title,
                version=self.version,
                description=self.description,
                contact=self.contact,
                license=self.license,
                summary=self.summary,
                termsOfService=self.terms_of_service,
            ),
        )

    def get_include_handlers(
        self, router: "Include", route_list: Optional[List["Gateway"]] = None
    ):
        if not route_list:
            route_list = []
        for route in router.routes:
            if isinstance(route, Include):
                route_list = self.get_include_handlers(route, route_list)
            elif isinstance(route, Gateway):
                route_list.append(route)
        return route_list

    def create_openapi_schema_model(self, app: "Esmerald") -> "OpenAPI":
        from esmerald.applications import ChildEsmerald, Esmerald

        schema = self.to_openapi_schema()
        schema.paths = {}
        for route in app.routes:
            if (
                isinstance(route, Gateway)
                and any(
                    handler.include_in_schema for handler, _ in route.handler.route_map.values()
                )
                and (route.handler.path_format or "/") not in schema.paths
            ):
                schema.paths[route.path_format or "/"] = create_path_item(
                    route=route.handler,
                    create_examples=self.create_examples,
                    use_handler_docstrings=self.use_handler_docstrings,
                )

            if isinstance(route, Include):
                routes = self.get_include_handlers(route)
                for route in routes:
                    if (
                        isinstance(route, Gateway)
                        and any(
                            handler.include_in_schema
                            for handler, _ in route.handler.route_map.values()
                        )
                        and (route.handler.path_format or "/") not in schema.paths
                    ):
                        schema.paths[route.path_format or "/"] = create_path_item(
                            route=route.handler,
                            create_examples=self.create_examples,
                            use_handler_docstrings=self.use_handler_docstrings,
                        )
            if isinstance(route, (Esmerald, ChildEsmerald)):
                ...

        return construct_open_api_with_schema_class(schema)
