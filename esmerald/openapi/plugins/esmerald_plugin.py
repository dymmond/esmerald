import inspect
from collections import namedtuple
from functools import partial
from typing import TYPE_CHECKING

from spectree.plugins.base import BasePlugin, Context

from esmerald.requests import Request
from esmerald.routing import gateways
from esmerald.routing.handlers import get
from esmerald.utils.url import clean_path

METHODS = {"get", "post", "put", "patch", "delete"}
Gateway = namedtuple("Gateway", ["path", "methods", "func", "handler"])

if TYPE_CHECKING:
    from esmerald.applications import Esmerald


def PydanticResponse(content):
    from starlette.responses import JSONResponse

    class _PydanticResponse(JSONResponse):
        def render(self, content) -> bytes:
            self._model_class = content.__class__
            return super().render(content.dict())

    return _PydanticResponse(content)


def generate_page_templates(config, ui, response):
    @get()
    async def handler(request: Request) -> response:
        return response(
            config.page_templates[ui].format(
                spec_url=config.spec_url,
                spec_path=config.path,
                **config.swagger_oauth2_config(),
            )
        )

    return handler


class EsmeraldPlugin(BasePlugin):
    ASYNC = True

    def __init__(self, spectree):
        super().__init__(spectree)
        from starlette.convertors import CONVERTOR_TYPES

        self.conv2type = {conv: typ for typ, conv in CONVERTOR_TYPES.items()}

    def register_route(self, app):
        self.app: "Esmerald" = app
        from starlette.responses import HTMLResponse, JSONResponse

        @get()
        async def spec_tree(request: Request) -> JSONResponse:
            return JSONResponse(self.spectree.spec)

        self.app.add_route(
            self.config.spec_url,
            spec_tree,
        )

        for ui in self.config.page_templates:
            handler = generate_page_templates(
                config=self.config,
                ui=ui,
                response=HTMLResponse,
            )
            self.app.add_route(path=f"/{self.config.path}/{ui}", handler=handler)
        self.app.router.activate()

    async def request_validation(self, request, query, json, headers, cookies):
        use_json = json and request.method not in ("GET", "DELETE")
        request.context = Context(
            query.parse_obj(request.query_params) if query else None,
            json.parse_raw(await request.body() or "{}") if use_json else None,
            headers.parse_obj(request.headers) if headers else None,
            cookies.parse_obj(request.cookies) if cookies else None,
        )

    def find_routes(self):
        routes = []

        def parse_route(app, prefix=""):
            # :class:`starlette.staticfiles.StaticFiles` doesn't have routes
            if not app.routes:
                return
            for route in app.routes:
                if route.path.startswith(f"/{self.config.path}"):
                    continue

                if isinstance(route, gateways.Gateway) and (
                    not route.handler.include_in_schema or not route.include_in_schema
                ):
                    continue

                func = route.app
                if isinstance(func, partial):
                    try:
                        func = func.__wrapped__
                    except AttributeError:
                        pass

                if getattr(func, "fn", None) and inspect.isclass(func.fn):
                    for method in METHODS:
                        if getattr(func.fn, method, None):
                            path = clean_path(prefix + route.path)
                            routes.append(
                                Gateway(
                                    f"{path}",
                                    {method.upper()},
                                    getattr(func, method),
                                    route,
                                )
                            )
                elif getattr(func, "fn", None) and inspect.isfunction(func.fn):
                    path = clean_path(prefix + route.path)
                    routes.append(
                        Gateway(f"{path}", route.methods, route.endpoint.fn, route.handler)
                    )
                else:
                    path = clean_path(prefix + route.path)
                    parse_route(route, prefix=f"{path}")

        parse_route(self.app)
        return routes

    def bypass(self, func, method):
        if method in ["HEAD", "OPTIONS"]:
            return True
        return False

    def parse_func(self, route):
        for method in route.methods or ["GET"]:
            yield method, route.func, route.handler

    def parse_path(self, route, path_parameter_descriptions):
        from starlette.routing import compile_path

        _, path, variables = compile_path(route.path)
        parameters = []

        for name, conv in variables.items():
            schema = None
            typ = self.conv2type[conv]
            if typ == "int":
                schema = {"type": "integer", "format": "int32"}
            elif typ == "float":
                schema = {
                    "type": "number",
                    "format": "float",
                }
            elif typ == "path":
                schema = {
                    "type": "string",
                    "format": "path",
                }
            elif typ == "str":
                schema = {"type": "string"}

            description = (
                path_parameter_descriptions.get(name, "") if path_parameter_descriptions else ""
            )
            parameters.append(
                {
                    "name": name,
                    "in": "path",
                    "required": True,
                    "schema": schema,
                    "description": description,
                }
            )

        return path, parameters
