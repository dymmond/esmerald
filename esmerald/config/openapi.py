from typing import Any, Dict, List, Optional, Union

from openapi_schemas_pydantic.v3_1_0.security_scheme import SecurityScheme
from pydantic import AnyUrl, BaseModel

from esmerald.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from esmerald.openapi.models import Contact, License, Tag
from esmerald.openapi.openapi import get_openapi
from esmerald.requests import Request
from esmerald.responses import HTMLResponse, JSONResponse
from esmerald.routing.handlers import get


class OpenAPIConfig(BaseModel):
    title: Optional[str] = None
    version: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    contact: Optional[Contact] = None
    terms_of_service: Optional[AnyUrl] = None
    license: Optional[License] = None
    security: Optional[List[SecurityScheme]] = None
    servers: Optional[List[Dict[str, Union[str, Any]]]] = None
    tags: Optional[List[Tag]] = None
    openapi_version: Optional[str] = None
    openapi_url: Optional[str] = None
    root_path_in_servers: bool = True
    docs_url: Optional[str] = None
    redoc_url: Optional[str] = None
    swagger_ui_oauth2_redirect_url: Optional[str] = None
    redoc_js_url: str = None
    redoc_favicon_url: str = None
    swagger_ui_init_oauth: Optional[Dict[str, Any]] = None
    swagger_ui_parameters: Optional[Dict[str, Any]] = None
    swagger_js_url: Optional[str] = None
    swagger_css_url: Optional[str] = None
    swagger_favicon_url: Optional[str] = None

    def openapi(self, app: Any) -> Dict[str, Any]:
        """Loads the OpenAPI routing schema"""
        openapi_schema = get_openapi(
            title=self.title,
            version=self.version,
            openapi_version=self.openapi_version,
            summary=self.summary,
            description=self.description,
            routes=app.routes,
            tags=self.tags,
            servers=self.servers,
            terms_of_service=self.terms_of_service,
            contact=self.contact,
            license=self.license,
        )
        app.openapi_schema = openapi_schema
        return openapi_schema

    def enable(self, app: Any) -> None:
        """Enables the OpenAPI documentation"""
        if self.openapi_url:
            urls = {server.get("url") for server in self.servers}
            server_urls = set(urls)

            @get(path=self.openapi_url)
            async def _openapi(request: Request) -> JSONResponse:
                root_path = request.scope.get("root_path", "").rstrip("/")
                if root_path not in server_urls:
                    if root_path and self.root_path_in_servers:
                        self.servers.insert(0, {"url": root_path})
                        server_urls.add(root_path)
                return JSONResponse(self.openapi(app))

            app.add_route(
                path="/", handler=_openapi, include_in_schema=False, activate_openapi=False
            )

        if self.openapi_url and self.docs_url:

            @get(path=self.docs_url)
            async def swagger_ui_html(request: Request) -> HTMLResponse:
                root_path = request.scope.get("root_path", "").rstrip("/")
                openapi_url = root_path + self.openapi_url
                oauth2_redirect_url = self.swagger_ui_oauth2_redirect_url
                if oauth2_redirect_url:
                    oauth2_redirect_url = root_path + oauth2_redirect_url
                return get_swagger_ui_html(
                    openapi_url=openapi_url,
                    title=self.title + " - Swagger UI",
                    oauth2_redirect_url=oauth2_redirect_url,
                    init_oauth=self.swagger_ui_init_oauth,
                    swagger_ui_parameters=self.swagger_ui_parameters,
                    swagger_js_url=self.swagger_js_url,
                    swagger_favicon_url=self.swagger_favicon_url,
                    swagger_css_url=self.swagger_css_url,
                )

            app.add_route(
                path="/",
                handler=swagger_ui_html,
                include_in_schema=False,
                activate_openapi=False,
            )

        if self.swagger_ui_oauth2_redirect_url:

            @get(self.swagger_ui_oauth2_redirect_url)
            async def swagger_ui_redirect(request: Request) -> HTMLResponse:
                return get_swagger_ui_oauth2_redirect_html()

            app.add_route(
                path="/",
                handler=swagger_ui_redirect,
                include_in_schema=False,
                activate_openapi=False,
            )

        if self.openapi_url and self.redoc_url:

            @get(self.redoc_url)
            async def redoc_html(request: Request) -> HTMLResponse:
                root_path = request.scope.get("root_path", "").rstrip("/")
                openapi_url = root_path + self.openapi_url
                return get_redoc_html(
                    openapi_url=openapi_url,
                    title=self.title + " - ReDoc",
                    redoc_js_url=self.redoc_js_url,
                    redoc_favicon_url=self.redoc_favicon_url,
                )

            app.add_route(
                path="/", handler=redoc_html, include_in_schema=False, activate_openapi=False
            )

        app.router.activate()
