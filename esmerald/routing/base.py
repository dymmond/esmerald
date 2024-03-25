from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from functools import partial
from inspect import Signature, isawaitable
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
    cast,
)
from uuid import UUID

from lilya._internal._connection import Connection
from lilya.responses import Response as LilyaResponse
from lilya.routing import compile_path
from lilya.transformers import TRANSFORMER_TYPES
from lilya.types import Receive, Scope, Send
from typing_extensions import TypedDict

from esmerald.backgound import BackgroundTask, BackgroundTasks
from esmerald.datastructures import ResponseContainer
from esmerald.enums import MediaType
from esmerald.exceptions import ImproperlyConfigured
from esmerald.injector import Inject
from esmerald.permissions.utils import continue_or_raise_permission_exception
from esmerald.requests import Request
from esmerald.responses import JSONResponse, Response
from esmerald.routing.apis.base import View
from esmerald.transformers.model import TransformerModel
from esmerald.transformers.signature import SignatureFactory
from esmerald.transformers.utils import get_signature
from esmerald.typing import Void, VoidType
from esmerald.utils.constants import DATA, PAYLOAD
from esmerald.utils.helpers import is_async_callable, is_class_and_subclass
from esmerald.utils.sync import AsyncCallable

if TYPE_CHECKING:  # pragma: no cover
    from openapi_schemas_pydantic.v3_1_0.security_scheme import SecurityScheme

    from esmerald.applications import Esmerald
    from esmerald.interceptors.interceptor import EsmeraldInterceptor
    from esmerald.interceptors.types import Interceptor
    from esmerald.permissions import BasePermission
    from esmerald.permissions.types import Permission
    from esmerald.routing.router import HTTPHandler
    from esmerald.types import (
        APIGateHandler,
        AsyncAnyCallable,
        Dependencies,
        ResponseCookies,
        ResponseHeaders,
    )
    from esmerald.typing import AnyCallable

param_type_map = {
    "str": str,
    "int": int,
    "float": float,
    "uuid": UUID,
    "decimal": Decimal,
    "date": date,
    "datetime": datetime,
    "time": time,
    "timedelta": timedelta,
    "path": Path,
}

CONV2TYPE = {conv: typ for typ, conv in TRANSFORMER_TYPES.items()}


T = TypeVar("T", bound="BaseHandlerMixin")


class PathParameterSchema(TypedDict):
    name: str
    full: str
    type: Type


class OpenAPIDefinitionMixin:  # pragma: no cover
    def parse_path(self, path: str) -> List[Union[str, PathParameterSchema]]:
        """
        Using the Lilya TRANSFORMERS and the application registered convertors,
        transforms the path into a PathParameterSchema used for the OpenAPI definition.
        """
        _, path, variables, _ = compile_path(path)

        parsed_components: List[Union[str, PathParameterSchema]] = []

        for name, convertor in variables.items():
            _type = CONV2TYPE[convertor]
            parsed_components.append(
                PathParameterSchema(name=name, type=param_type_map[_type], full=name)
            )
        return parsed_components


class BaseSignature:
    """
    In charge of handling the signartures of the handlers.
    """

    def create_signature_model(self, is_websocket: bool = False) -> None:
        """
        Creates a signature model for the given route.

        Websockets do not support methods.
        """
        if not self.signature_model:
            self.signature_model = SignatureFactory(
                fn=cast("AnyCallable", self.fn),
                dependency_names=self.dependency_names,
            ).create_signature()

        for dependency in list(self.get_dependencies().values()):
            if not dependency.signature_model:
                dependency.signature_model = SignatureFactory(
                    fn=dependency.dependency, dependency_names=self.dependency_names
                ).create_signature()

        transformer_model = self.create_handler_transformer_model()
        if not is_websocket:
            self.transformer = transformer_model
            for method in self.methods:
                self.route_map[method] = (self, transformer_model)
        else:
            self.websocket_parameter_model = transformer_model

    def create_handler_transformer_model(self) -> "TransformerModel":
        """Method to create a TransformerModel for a given handler."""
        dependencies = self.get_dependencies()
        signature_model = get_signature(self)

        return TransformerModel.create_signature(
            signature_model=signature_model,
            dependencies=dependencies,
            path_parameters=self.path_parameters,
        )


class BaseResponseHandler:
    """
    In charge of handling the responses of the handlers.
    """

    def response_container_handler(
        self,
        cookies: "ResponseCookies",
        headers: Dict[str, Any],
        media_type: str,
        status_code: int,
    ) -> "AsyncAnyCallable":
        """Creates a handler for ResponseContainer Types"""

        async def response_content(
            data: ResponseContainer, app: Type["Esmerald"], **kwargs: Dict[str, Any]
        ) -> LilyaResponse:
            _headers = {**self.get_headers(headers), **data.headers}
            _cookies = self.get_cookies(data.cookies, cookies)
            response: Response = data.to_response(
                app=app,
                headers=_headers,
                status_code=status_code,
                media_type=media_type,
            )
            for cookie in _cookies:
                response.set_cookie(**cookie)
            return response

        return response_content

    def response_handler(
        self,
        cookies: "ResponseCookies",
        headers: Optional["ResponseHeaders"] = None,
        status_code: Optional[int] = None,
        media_type: Optional[str] = MediaType.TEXT,
    ) -> "AsyncAnyCallable":
        async def response_content(data: Response, **kwargs: Dict[str, Any]) -> LilyaResponse:
            _cookies = self.get_cookies(data.cookies, cookies)
            _headers = {
                **self.get_headers(headers),
                **data.headers,
                **self.allow_header,
            }

            for cookie in _cookies:
                data.set_cookie(**cookie)

            if status_code:
                data.status_code = status_code

            if media_type:
                data.media_type = media_type

            for header, value in _headers.items():
                data.headers[header] = value
            return data

        return response_content

    def json_response_handler(
        self,
        status_code: Optional[int] = None,
        cookies: Optional["ResponseCookies"] = None,
        headers: Optional["ResponseHeaders"] = None,
    ) -> "AsyncAnyCallable":
        """Creates a handler function for Esmerald JSON responses"""

        async def response_content(data: Response, **kwargs: Dict[str, Any]) -> LilyaResponse:
            _cookies = self.get_cookies(cookies, [])
            _headers = {
                **self.get_headers(headers),
                **data.headers,
                **self.allow_header,
            }
            for cookie in _cookies:
                data.set_cookie(**cookie)  # pragma: no cover

            for header, value in _headers.items():
                data.headers[header] = value

            if status_code:
                data.status_code = status_code
            return data

        return response_content

    def starlette_response_handler(
        self,
        cookies: "ResponseCookies",
        headers: Optional["ResponseHeaders"] = None,
    ) -> "AsyncAnyCallable":
        """Creates an handler for Lilya Responses."""

        async def response_content(data: LilyaResponse, **kwargs: Dict[str, Any]) -> LilyaResponse:
            _cookies = self.get_cookies(cookies, [])
            _headers = {
                **self.get_headers(headers),
                **data.headers,
                **self.allow_header,
            }
            for cookie in _cookies:
                data.set_cookie(**cookie)  # pragma: no cover

            for header, value in _headers.items():
                data.headers[header] = value
            return data

        return response_content

    def _handler(
        self,
        background: Optional[Union["BackgroundTask", "BackgroundTasks"]],
        cookies: "ResponseCookies",
        headers: Dict[str, Any],
        media_type: str,
        response_class: Any,
        status_code: int,
    ) -> "AsyncAnyCallable":
        async def response_content(data: Any, **kwargs: Dict[str, Any]) -> LilyaResponse:

            data = await self.get_response_data(data=data)
            _cookies = self.get_cookies(cookies, [])
            if isinstance(data, JSONResponse):
                response = data
                response.status_code = status_code
                response.background = background
            else:
                response = response_class(
                    background=background,
                    content=data,
                    headers=headers,
                    media_type=media_type,
                    status_code=status_code,
                )

            for cookie in _cookies:
                response.set_cookie(**cookie)  # pragma: no cover
            return response

        return response_content

    async def get_response_for_request(
        self,
        scope: "Scope",
        request: Request,
        route: "HTTPHandler",
        parameter_model: "TransformerModel",
    ) -> "LilyaResponse":
        """
        Get response for the given request using the specified route and parameter model.

        Args:
            scope (Scope): The scope of the request.
            request (Request): The incoming request.
            route (HTTPHandler): The route handler for the request.
            parameter_model (TransformerModel): The parameter model for handling request parameters.

        Returns:
            LilyaResponse: The response generated for the request.
        """
        response = await self.call_handler_function(
            scope=scope,
            request=request,
            route=route,
            parameter_model=parameter_model,
        )
        return cast("LilyaResponse", response)

    async def call_handler_function(
        self,
        scope: "Scope",
        request: Request,
        route: "HTTPHandler",
        parameter_model: "TransformerModel",
    ) -> Any:
        """
        Call the handler function for the given request and return the response data.

        Args:
            scope (Scope): The scope of the request.
            request (Request): The incoming request.
            route (HTTPHandler): The route handler for the request.
            parameter_model (TransformerModel): The parameter model for handling request parameters.

        Returns:
            Any: The response data generated by the handler function.
        """
        response_data = await self._get_response_data(
            route=route,
            parameter_model=parameter_model,
            request=request,
        )

        return await self.to_response(
            app=scope["app"],
            data=response_data,
        )

    @staticmethod
    async def _get_response_data(
        route: "HTTPHandler", parameter_model: "TransformerModel", request: Request
    ) -> Any:
        """
        Determine required kwargs for the given handler, assign to the object dictionary, and get the response data.

        Args:
            route (HTTPHandler): The route handler for the request.
            parameter_model (TransformerModel): The parameter model for handling request parameters.
            request (Request): The incoming request.

        Returns:
            Any: The response data generated by processing the request.
        """
        signature_model = get_signature(route)
        is_data_or_payload: str = None

        if parameter_model.has_kwargs:
            kwargs = parameter_model.to_kwargs(connection=request, handler=route)

            is_data_or_payload = DATA if kwargs.get(DATA) else PAYLOAD
            request_data = kwargs.get(DATA) or kwargs.get(PAYLOAD)

            if request_data:
                kwargs[is_data_or_payload] = await request_data

            for dependency in parameter_model.dependencies:
                kwargs[dependency.key] = await parameter_model.get_dependencies(
                    dependency=dependency, connection=request, **kwargs
                )

            parsed_kwargs = signature_model.parse_values_for_connection(
                connection=request, **kwargs
            )
        else:
            parsed_kwargs = {}

        if isinstance(route.parent, View):
            fn = partial(
                cast("AnyCallable", route.fn),
                route.parent,
                **parsed_kwargs,
            )
        else:
            fn = partial(cast("AnyCallable", route.fn), **parsed_kwargs)

        if is_async_callable(fn):
            return await fn()
        return fn()

    def get_response_handler(self) -> Callable[[Any], Awaitable[LilyaResponse]]:
        """
        Checks and validates the type of return response and maps to the corresponding
        handler with the given parameters.
        """
        if self._response_handler is Void:
            media_type = (
                self.media_type.value if isinstance(self.media_type, Enum) else self.media_type
            )

            response_class = self.get_response_class()
            headers = self.get_response_headers()
            cookies = self.get_response_cookies()

            if is_class_and_subclass(self.handler_signature.return_annotation, ResponseContainer):
                handler = self.response_container_handler(
                    cookies=cookies,
                    media_type=self.media_type,
                    status_code=self.status_code,
                    headers=headers,
                )
            elif is_class_and_subclass(
                self.handler_signature.return_annotation,
                JSONResponse,
            ):
                handler = self.json_response_handler(
                    status_code=self.status_code, cookies=cookies, headers=headers
                )
            elif is_class_and_subclass(self.handler_signature.return_annotation, Response):
                handler = self.response_handler(
                    cookies=cookies,
                    status_code=self.status_code,
                    media_type=self.media_type,
                    headers=headers,
                )
            elif is_class_and_subclass(self.handler_signature.return_annotation, LilyaResponse):
                handler = self.starlette_response_handler(
                    cookies=cookies,
                    headers=headers,
                )
            else:
                handler = self._handler(
                    background=self.background,
                    cookies=cookies,
                    headers=headers,
                    media_type=media_type,
                    response_class=response_class,
                    status_code=self.status_code,
                )
            self._response_handler = handler

        return cast(
            "Callable[[Any], Awaitable[LilyaResponse]]",
            self._response_handler,
        )


class BaseHandlerMixin(BaseSignature, BaseResponseHandler, OpenAPIDefinitionMixin):
    """
    Base of HTTPHandler and WebSocketHandler.
    """

    @property
    def handler_signature(self) -> Signature:
        """The Signature of 'self.fn'."""
        return Signature.from_callable(cast("AnyCallable", self.fn))

    @property
    def path_parameters(self) -> Set[str]:
        """
        Gets the path parameters in a set format.

        Example: {'name', 'id'}
        """
        parameters = set()
        for param_name, _ in self.param_convertors.items():
            parameters.add(param_name)
        return parameters

    @property
    def stringify_parameters(self) -> List[str]:  # pragma: no cover
        """
        Gets the param:type in string like list.
        Used for the directive `esmerald show_urls`.
        """
        path_components = self.parse_path(self.path)
        parameters = [component for component in path_components if isinstance(component, dict)]

        stringified_parameters = [
            f"{param['name']}:{param['type'].__name__}" for param in parameters
        ]
        return stringified_parameters

    @property
    def parent_levels(self) -> List[Any]:
        """
        Returns the handler from the app down to the route handler.

        Who is the parent of a given layer/level.

        Example:

            app = Esmerald(routes=[
                Include(path='/api/v1', routes=[
                    Gateway(path='/home', handler=home)
                ])
            ])

            1. Parent of Gateway is the Include.
            2. Parent of the Include is the Esmerald router.
            3. Parent of the Esmerald router is the Esmerald app itself.
        """
        levels = []
        current: Any = self
        while current:
            levels.append(current)
            current = current.parent
        return list(reversed(levels))

    @property
    def dependency_names(self) -> Set[str]:
        """A unique set of all dependency names provided in the handlers parent
        levels."""
        level_dependencies = (level.dependencies or {} for level in self.parent_levels)
        return {name for level in level_dependencies for name in level.keys()}

    def get_permissions(self) -> List["AsyncCallable"]:
        """
        Returns all the permissions in the handler scope from the ownsership layers.
        """
        if self._permissions is Void:
            self._permissions: Union[List["Permission"], "VoidType"] = []
            for layer in self.parent_levels:
                self._permissions.extend(layer.permissions or [])
            self._permissions = cast(
                "List[Permission]",
                [AsyncCallable(permissions) for permissions in self._permissions],
            )
        return cast("List[AsyncCallable]", self._permissions)

    def get_dependencies(self) -> "Dependencies":
        """
        Returns all dependencies of the handler function's starting from the parent levels.
        """
        if not self.signature_model:
            raise RuntimeError(
                "get_dependencies cannot be called before a signature model has been generated"
            )

        if not self._dependencies or self._dependencies is Void:
            self._dependencies: "Dependencies" = {}
            for level in self.parent_levels:
                for key, value in (level.dependencies or {}).items():
                    self.is_unique_dependency(
                        dependencies=self._dependencies,
                        key=key,
                        injector=value,
                    )
                    self._dependencies[key] = value
        return self._dependencies

    @staticmethod
    def is_unique_dependency(dependencies: "Dependencies", key: str, injector: Inject) -> None:
        """
        Validates that a given inject has not been already defined under a
        different key in any of the levels.
        """
        for dependency_key, value in dependencies.items():
            if injector == value:
                raise ImproperlyConfigured(
                    f"Injector for key {key} is already defined under the different key {dependency_key}. "
                    f"If you wish to override a inject, it must have the same key."
                )

    def get_cookies(
        self, local_cookies: "ResponseCookies", other_cookies: "ResponseCookies"
    ) -> List[Dict[str, Any]]:  # pragma: no cover
        """
        Returns a unique list of cookies.
        """
        filtered_cookies = [*local_cookies]
        for cookie in other_cookies:
            if not any(cookie.key == c.key for c in filtered_cookies):
                filtered_cookies.append(cookie)
        normalized_cookies: List[Dict[str, Any]] = []
        for cookie in filtered_cookies:
            normalized_cookies.append(
                cookie.model_dump(exclude_none=True, exclude={"description"})
            )
        return normalized_cookies

    def get_headers(self, headers: "ResponseHeaders") -> Dict[str, Any]:
        """
        Returns a dict of response headers.
        """
        return {k: v.value for k, v in headers.items()}

    async def get_response_data(self, data: Any) -> Any:  # pragma: no cover
        """
        Retrives the response data for sync and async.
        """
        if isawaitable(data):
            data = await data
        return data

    async def allow_connection(self, connection: "Connection") -> None:  # pragma: no cover
        """
        Validates the connection.

        Handles with the permissions for each view (get, put, post, delete, patch, route...) after the request.

        Raises a PermissionDenied exception if not allowed..
        """
        for permission in self.get_permissions():
            awaitable: "BasePermission" = cast("BasePermission", await permission())
            request: "Request" = cast("Request", connection)
            handler = cast("APIGateHandler", self)
            await continue_or_raise_permission_exception(request, handler, awaitable)

    def get_security_schemes(self) -> List["SecurityScheme"]:
        """
        Returns all security schemes from every level.
        """
        security_schemes: List["SecurityScheme"] = []
        for layer in self.parent_levels:
            security_schemes.extend(layer.security or [])
        return security_schemes

    def get_handler_tags(self) -> List[str]:
        """
        Returns all the tags associated with the handler
        by checking the parents as well.
        """
        tags: List[str] = []
        for layer in self.parent_levels:
            tags.extend(layer.tags or [])

        tags_clean: List[str] = []
        for tag in tags:
            if tag not in tags_clean:
                tags_clean.append(tag)

        return tags_clean if tags_clean else None


class BaseInterceptorMixin(BaseHandlerMixin):  # pragma: no cover
    def get_interceptors(self) -> List["AsyncCallable"]:
        """
        Returns all the interceptors in the handler scope from the ownsership layers.
        """
        if self._interceptors is Void:
            self._interceptors: Union[List["Interceptor"], "VoidType"] = []
            for layer in self.parent_levels:
                self._interceptors.extend(layer.interceptors or [])
            self._interceptors = cast(
                "List[Interceptor]",
                [AsyncCallable(interceptors) for interceptors in self._interceptors],
            )
        return cast("List[AsyncCallable]", self._interceptors)

    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        Checks for every interceptor on each level and runs them all before reaching any
        of the handlers.
        """
        for interceptor in self.get_interceptors():
            awaitable: "EsmeraldInterceptor" = await interceptor()
            await awaitable.intercept(scope, receive, send)
