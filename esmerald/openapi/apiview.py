from typing import TYPE_CHECKING, Callable, Dict

from esmerald.enums import MediaType, OpenAPIMediaType
from esmerald.exceptions import ImproperlyConfigured
from esmerald.requests import Request
from esmerald.responses import Response
from esmerald.routing.handlers import get
from esmerald.routing.views import APIView
from orjson import OPT_INDENT_2, dumps
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND

if TYPE_CHECKING:
    from openapi_schemas_pydantic.v3_1_0.open_api import OpenAPI
    from typing_extensions import Literal

MSG_OPENAPI_NOT_INITIALIZED = "Esmerald has not been created with an OpenAPIConfig"


class OpenAPIView(APIView):
    """
    The view that manages the OpenAPI documentation
    """

    path: str = "/docs"
    style: str = "body { margin: 0; padding: 0 }"
    redoc_version: str = "next"
    swagger_ui_version: str = "4.14.0"
    stoplight_elements_version: str = "7.6.5"
    favicon_url: str = "https://esmerald.dymmond.com/statics/images/favicon.ico"
    redoc_google_fonts: bool = True
    redoc_js_url: str = (
        f"https://cdn.jsdelivr.net/npm/redoc@{redoc_version}/bundles/redoc.standalone.js"
    )
    swagger_css_url: str = (
        f"https://cdn.jsdelivr.net/npm/swagger-ui-dist@{swagger_ui_version}/swagger-ui.css"
    )
    swagger_ui_bundle_js_url: str = (
        f"https://cdn.jsdelivr.net/npm/swagger-ui-dist@{swagger_ui_version}/swagger-ui-bundle.js"
    )
    swagger_ui_standalone_preset_js_url: str = f"https://cdn.jsdelivr.net/npm/swagger-ui-dist@{swagger_ui_version}/swagger-ui-standalone-preset.js"
    stoplight_elements_css_url: str = (
        f"https://unpkg.com/@stoplight/elements@{stoplight_elements_version}/styles.min.css"
    )
    stoplight_elements_js_url: str = (
        f"https://unpkg.com/@stoplight/elements@{stoplight_elements_version}/web-components.min.js"
    )

    _dumped_schema: str = ""
    _dumped_modified_schema: str = ""

    @staticmethod
    def get_schema_from_request(request: Request) -> "OpenAPI":
        if not request.app.openapi_schema:
            raise ImproperlyConfigured(MSG_OPENAPI_NOT_INITIALIZED)
        return request.app.openapi_schema

    def should_serve_endpoint(self, request: Request) -> bool:
        if not request.app.openapi_config:
            raise ImproperlyConfigured(MSG_OPENAPI_NOT_INITIALIZED)

        request_path = set(filter(None, request.url.path.split("/")))
        root_path = request.app.root_path or set(filter(None, self.path.split("/")))

        config = request.app.openapi_config

        if request_path == root_path and config.root_schema_site in config.enabled_endpoints:
            return True

        if request_path & config.enabled_endpoints:
            return True

        return False

    @property
    def favicon(self) -> str:
        return (
            f"<link rel='icon' type='image/x-icon' href='{self.favicon_url}'>"
            if self.favicon_url
            else "<meta/>"
        )

    @property
    def render_methods_map(
        self,
    ) -> Dict["Literal['redoc', 'swagger', 'elements']", Callable[[Request], str]]:
        """
        Returns:
            A mapping of string keys to render methods.
        """
        return {
            "redoc": self.render_redoc,
            "swagger": self.render_swagger_ui,
            "elements": self.render_stoplight_elements,
        }

    @get(
        path="/openapi.yaml",
        media_type=OpenAPIMediaType.OPENAPI_YAML,
        include_in_schema=False,
    )
    def retrieve_schema_yaml(self, request: Request) -> Response:

        if not request.app.openapi_config:  # pragma: no cover
            raise ImproperlyConfigured(MSG_OPENAPI_NOT_INITIALIZED)

        if self.should_serve_endpoint(request):
            return Response(
                content=self.get_schema_from_request(request),
                status_code=HTTP_200_OK,
                media_type=OpenAPIMediaType.OPENAPI_YAML,
            )
        return Response(
            content={},
            status_code=HTTP_404_NOT_FOUND,
            media_type=MediaType.JSON,
        )

    @get(
        path="/openapi.json",
        media_type=OpenAPIMediaType.OPENAPI_JSON,
        include_in_schema=False,
    )
    def retrieve_schema_json(self, request: Request) -> Response:
        if not request.app.openapi_config:  # pragma: no cover
            raise ImproperlyConfigured(MSG_OPENAPI_NOT_INITIALIZED)

        if self.should_serve_endpoint(request):
            return Response(
                content=self.get_schema_from_request(request),
                status_code=HTTP_200_OK,
                media_type=OpenAPIMediaType.OPENAPI_JSON,
            )
        return Response(
            content={},
            status_code=HTTP_404_NOT_FOUND,
            media_type=MediaType.JSON,
        )

    @get(path="/", media_type=MediaType.HTML, include_in_schema=False)
    def root(self, request: Request) -> Response:
        config = request.app.openapi_config
        if not config:  # pragma: no cover
            raise ImproperlyConfigured(MSG_OPENAPI_NOT_INITIALIZED)
        render_method = self.render_methods_map[config.root_schema_site]

        if self.should_serve_endpoint(request):
            return Response(
                content=render_method(request),
                status_code=HTTP_200_OK,
                media_type=MediaType.HTML,
            )
        return Response(
            content=self.render_404_page(),
            status_code=HTTP_404_NOT_FOUND,
            media_type=MediaType.HTML,
        )

    @get(path="/swagger", media_type=MediaType.HTML, include_in_schema=False)
    def swagger_ui(self, request: Request) -> Response:
        if not request.app.openapi_config:  # pragma: no cover
            raise ImproperlyConfigured(MSG_OPENAPI_NOT_INITIALIZED)

        if self.should_serve_endpoint(request):
            return Response(
                content=self.render_swagger_ui(request),
                status_code=HTTP_200_OK,
                media_type=MediaType.HTML,
            )
        return Response(
            content=self.render_404_page(),
            status_code=HTTP_404_NOT_FOUND,
            media_type=MediaType.HTML,
        )

    @get(path="/elements", media_type=MediaType.HTML, include_in_schema=False)
    def stoplight_elements(self, request: Request) -> Response:
        if not request.app.openapi_config:  # pragma: no cover
            raise ImproperlyConfigured(MSG_OPENAPI_NOT_INITIALIZED)

        if self.should_serve_endpoint(request):
            return Response(
                content=self.render_stoplight_elements(request),
                status_code=HTTP_200_OK,
                media_type=MediaType.HTML,
            )
        return Response(
            content=self.render_404_page(),
            status_code=HTTP_404_NOT_FOUND,
            media_type=MediaType.HTML,
        )

    @get(path="/redoc", media_type=MediaType.HTML, include_in_schema=False)
    def redoc(self, request: Request) -> Response:  # pragma: no cover
        if not request.app.openapi_config:  # pragma: no cover
            raise ImproperlyConfigured(MSG_OPENAPI_NOT_INITIALIZED)

        if self.should_serve_endpoint(request):
            return Response(
                content=self.render_redoc(request),
                status_code=HTTP_200_OK,
                media_type=MediaType.HTML,
            )
        return Response(
            content=self.render_404_page(),
            status_code=HTTP_404_NOT_FOUND,
            media_type=MediaType.HTML,
        )

    def render_swagger_ui(self, request: Request) -> str:
        schema = self.get_schema_from_request(request)
        # Note: Fix for Swagger rejection OpenAPI >=3.1
        if self._dumped_modified_schema == "":
            schema_copy = schema.copy()
            schema_copy.openapi = "3.0.3"
            self._dumped_modified_schema = dumps(
                schema_copy.json(by_alias=True, exclude_none=True),
                option=OPT_INDENT_2,
            ).decode("utf-8")

        head = f"""
          <head>
            <title>{schema.info.title}</title>
            {self.favicon}
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="{self.swagger_css_url}" rel="stylesheet">
            <script src="{self.swagger_ui_bundle_js_url}" crossorigin></script>
            <script src="{self.swagger_ui_standalone_preset_js_url}" crossorigin></script>
            <style>{self.style}</style>
          </head>
        """
        body = f"""
          <body>
            <div id='swagger-container'/>
            <script type="text/javascript">
            const ui = SwaggerUIBundle({{
                spec: JSON.parse({self._dumped_modified_schema}),
                dom_id: '#swagger-container',
                deepLinking: true,
                showExtensions: true,
                showCommonExtensions: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
            }})
            </script>
          </body>
        """
        return f"""
        <!DOCTYPE html>
            <html>
                {head}
                {body}
            </html>
        """

    def render_stoplight_elements(self, request: Request) -> str:
        schema = self.get_schema_from_request(request)
        head = f"""
          <head>
            <title>{schema.info.title}</title>
            {self.favicon}
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <link rel="stylesheet" href="{self.stoplight_elements_css_url}">
            <script src="{self.stoplight_elements_js_url}" crossorigin></script>
            <style>{self.style}</style>
          </head>
        """
        body = f"""
          <body>
            <elements-api
                apiDescriptionUrl="{self.path}/openapi.json"
                router="hash"
                layout="sidebar"
            />
          </body>
        """
        return f"""
        <!DOCTYPE html>
            <html>
                {head}
                {body}
            </html>
        """

    def render_redoc(self, request: Request) -> str:  # pragma: no cover
        schema = self.get_schema_from_request(request)
        if self._dumped_schema == "":
            self._dumped_schema = dumps(
                schema.json(by_alias=True, exclude_none=True),
                option=OPT_INDENT_2,
            ).decode("utf-8")
        head = f"""
          <head>
            <title>{schema.info.title}</title>
            {self.favicon}
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            """
        if self.redoc_google_fonts:
            head += """
            <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
            """
        head += f"""
            <script src="{self.redoc_js_url}" crossorigin></script>
            <style>
                {self.style}
            </style>
          </head>
        """
        body = f"""
          <body>
            <div id='redoc-container'/>
            <script type="text/javascript">
                Redoc.init(
                    JSON.parse({self._dumped_schema}),
                    undefined,
                    document.getElementById('redoc-container')
                )
            </script>
          </body>
        """
        return f"""
        <!DOCTYPE html>
            <html>
                {head}
                {body}
            </html>
        """

    def render_404_page(self) -> str:
        """This method renders an HTML 404 page.

        Returns:
            A rendered html string.
        """

        return f"""
        <!DOCTYPE html>
        <html>
            <head>
                <title>404 Not found</title>
                {self.favicon}
                <meta charset="utf-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    {self.style}
                </style>
            </head>
            <body>
                <h1>Error 404</h1>
            </body>
        </html>
        """
