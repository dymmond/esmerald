from __future__ import annotations

import asyncio
from typing import Any

from lilya._internal._path import clean_path

from esmerald import (
    HTTPException,
    Inject,
    Injects,
    Request,
    route,
)
from esmerald.responses import JSONResponse
from esmerald.utils.helpers import make_callable

try:
    from grpclib.exceptions import GRPCError, Status
    from grpclib.server import Server
except ImportError:
    Server = None
    GRPCError = None
    Status = None

# Mapping HTTP methods to Esmerald decorators
HTTP_ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "TRACE"]


class GrpcGateway:
    """
    GrpcGateway is a class that bridges gRPC services and HTTP endpoints.
    It exposes the methods of gRPC services as HTTP endpoints using Esmerald.

    Attributes:
        services (list[type]): List of gRPC service types that should be exposed over HTTP.
        grpc_server (Server): The gRPC server instance that handles the communication with the gRPC services.
        path (str): The base path to be used for generating HTTP routes. Default is "/grpc".

    Methods:
        __init__(services: list[type], expose_http: bool = True, **kwargs: Any) -> None:
            Initializes the GrpcGateway instance, setting up the gRPC server and optionally exposing HTTP endpoints.

        startup() -> None:
            Starts the gRPC server asynchronously.

        shutdown() -> None:
            Shuts down the gRPC server asynchronously.

        _register_http_endpoints() -> None:
            Registers HTTP endpoints for each gRPC service method, converting them into HTTP routes.

        __grpc_to_http_status(grpc_status: Status) -> int:
            Converts gRPC status codes to their corresponding HTTP status codes for error handling.
    """

    def __init__(
        self,
        path: str,
        services: list[type],
        expose_http: bool = True,
        http_methods: list[str] | None = None,
        **server_options: Any,
    ) -> None:
        """
        Initializes the GrpcGateway instance. Sets up the gRPC server and optionally exposes HTTP endpoints.

        Args:
            services (list[type]): List of gRPC service types that should be exposed over HTTP.
            expose_http (bool): Whether to automatically expose HTTP endpoints for the services. Default is True.
            http_methods (list[str]): If a list is provided,it will only enable the http methods when expose_http is true
            **kwargs (Any): Additional keyword arguments (e.g., to customize path).

        Raises:
            AssertionError: If grpclib is not available.
        """
        assert (
            Server
        ), "grpclib is required for gRPC support. Install it with `pip install grpclib`."

        assert path.startswith("/"), "Paths must start with '/'"

        self.path = clean_path(path)
        self.services = services
        self.grpc_server = Server([service() for service in services])
        self.server_options = server_options
        self.http_methods = (
            [method.upper() for method in http_methods]
            if http_methods is not None
            else HTTP_ALLOWED_METHODS
        )

        if expose_http:
            self._register_http_endpoints()

        if "host" not in server_options:
            server_options["host"] = "127.0.0.1"

        if "port" not in server_options:
            server_options["port"] = 50051

    async def startup(self) -> None:
        """
        Starts the gRPC server asynchronously.

        This method creates an event loop task to start the server on `127.0.0.1` and listens on port `50051`.
        """
        loop = asyncio.get_event_loop()
        loop.create_task(self.grpc_server.start(**self.server_options))

    async def shutdown(self) -> None:
        """
        Shuts down the gRPC server asynchronously.

        This method ensures that the server closes properly when the application shuts down.
        """
        await self.grpc_server.close()  # type: ignore

    def _register_http_endpoints(self) -> Any:
        """
        Registers HTTP endpoints for each gRPC service method.

        For each service in `self.services`, this method dynamically generates HTTP routes and associates
        them with the corresponding gRPC service method. It uses Esmerald decorators to define the HTTP
        methods (`GET`, `POST`, etc.), maps them to gRPC methods, and defines a handler that wraps the
        gRPC method with HTTP request handling.

        This method assumes that each service has callable methods that should be exposed as HTTP routes.
        """
        for service in self.services:
            service_instance = service()

            for method_name in dir(service_instance):
                if method_name.startswith("_"):
                    continue  # Skip private methods

                method = getattr(service_instance, method_name)
                if callable(method):
                    route_path = clean_path(
                        f"/{self.path}/{service.__name__.lower()}/{method_name.lower()}"
                    )
                    name = route_path.replace("/", "_").replace(".", "_").replace("__", "_")

                    if name.startswith("_"):
                        name = name[1:]

                    # Define a dependency for the service instance
                    def service_dependency() -> Any:
                        return service_instance  # noqa

                    callable_fn = make_callable(method_name)

                    @route(  # type: ignore
                        path=route_path,
                        tags=["gRPC"],
                        methods=self.http_methods,
                        name=name,
                        dependencies={
                            "service": Inject(service_dependency),
                            "service_method": Inject(callable_fn),
                        },
                    )
                    async def http_wrapper(
                        request: Request,
                        service: Any = Injects(),
                        service_method: Any = Injects(),
                    ) -> Any:
                        """
                        HTTP handler that wraps the gRPC method. It receives HTTP requests, converts them into
                        data that can be processed by the gRPC method, and returns the result as an HTTP response.

                        Args:
                            request (Request): The HTTP request object containing input data.
                            service (Any): The gRPC service instance injected from dependencies.
                            service_method (Any): The gRPC method to be invoked, injected from dependencies.

                        Returns:
                            JSONResponse: The response that will be sent back to the client, wrapped as a JSON response.

                        Raises:
                            HTTPException: If an error occurs while invoking the gRPC method, this exception is raised
                            with the appropriate HTTP status code and error message.
                        """
                        method = getattr(service, service_method)
                        try:
                            data = await request.json()  # Extract request data
                            response = await method(data)  # Call the gRPC method
                            return JSONResponse(response)
                        except GRPCError as e:
                            raise HTTPException(
                                status_code=self.__grpc_to_http_status(e.status), detail=e.message
                            ) from e

                    # Yield the HTTP method, route, and handler for use by the framework
                    http_name = f"http_handler_{service_instance.__class__.__name__.lower()}_{method.__name__.lower()}"
                    http_wrapper.fn.__name__ = http_name
                    yield http_wrapper

    def __grpc_to_http_status(self, grpc_status: Status) -> int:
        """
        Converts gRPC status codes to HTTP status codes.

        This method maps common gRPC status codes to their corresponding HTTP status codes. This mapping is used
        to ensure that gRPC errors are communicated effectively as HTTP responses.

        Args:
            grpc_status (Status): The gRPC status code to be converted to an HTTP status code.

        Returns:
            int: The corresponding HTTP status code. Defaults to 500 (Internal Server Error) if the status code
                 is not mapped.
        """
        mapping = {
            Status.OK: 200,
            Status.CANCELLED: 499,
            Status.UNKNOWN: 500,
            Status.INVALID_ARGUMENT: 400,
            Status.DEADLINE_EXCEEDED: 504,
            Status.NOT_FOUND: 404,
            Status.ALREADY_EXISTS: 409,
            Status.PERMISSION_DENIED: 403,
            Status.UNAUTHENTICATED: 401,
            Status.RESOURCE_EXHAUSTED: 429,
            Status.FAILED_PRECONDITION: 400,
            Status.ABORTED: 409,
            Status.OUT_OF_RANGE: 400,
            Status.UNIMPLEMENTED: 501,
            Status.INTERNAL: 500,
            Status.UNAVAILABLE: 503,
            Status.DATA_LOSS: 500,
        }
        return mapping.get(grpc_status, 500)  # Default to 500 if the status code is unknown
