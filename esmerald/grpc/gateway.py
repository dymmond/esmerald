from __future__ import annotations

import asyncio
from typing import Any

from esmerald import (
    HTTPException,
    Inject,
    Injects,
    Request,
    delete,
    get,
    options,
    patch,
    post,
    put,
    trace,
)
from esmerald.responses import JSONResponse

try:
    from grpclib.exceptions import GRPCError, Status
    from grpclib.server import Server
except ImportError:
    Server = None
    GRPCError = None
    Status = None

# Mapping HTTP methods to Esmerald decorators
HTTP_METHODS = {
    "get": get,
    "post": post,
    "put": put,
    "delete": delete,
    "patch": patch,
    "options": options,
    "trace": trace,
}


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

    def __init__(self, services: list[type], expose_http: bool = True, **kwargs: Any) -> None:
        """
        Initializes the GrpcGateway instance. Sets up the gRPC server and optionally exposes HTTP endpoints.

        Args:
            services (list[type]): List of gRPC service types that should be exposed over HTTP.
            expose_http (bool): Whether to automatically expose HTTP endpoints for the services. Default is True.
            **kwargs (Any): Additional keyword arguments (e.g., to customize path).

        Raises:
            AssertionError: If grpclib is not available.
        """
        assert (
            Server
        ), "grpclib is required for gRPC support. Install it with `pip install grpclib`."

        self.path = kwargs.get("path", "/grpc")
        self.services = services
        self.grpc_server = Server([service() for service in services])

        if expose_http:
            self._register_http_endpoints()

    async def startup(self) -> None:
        """
        Starts the gRPC server asynchronously.

        This method creates an event loop task to start the server on `127.0.0.1` and listens on port `50051`.
        """
        loop = asyncio.get_event_loop()
        loop.create_task(self.grpc_server.start("127.0.0.1", 50051))

    async def shutdown(self) -> None:
        """
        Shuts down the gRPC server asynchronously.

        This method ensures that the server closes properly when the application shuts down.
        """
        await self.grpc_server.close()  # type: ignore

    def _register_http_endpoints(self) -> None:
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
                    for http_method, decorator in HTTP_METHODS.items():
                        # Construct the HTTP route
                        route = f"/{self.path}/{service.__name__.lower()}/{method_name.lower()}"

                        # Define a dependency for the service instance
                        def service_dependency() -> Any:
                            return service_instance  # noqa

                        def get_method() -> Any:
                            return method  # noqa

                        @decorator(  # type: ignore
                            path=route,
                            tags=["gRPC"],
                            dependencies={
                                "service": Inject(service_dependency),
                                "method": Inject(get_method),
                            },
                        )
                        async def http_wrapper(
                            request: Request, service: Any = Injects(), method: Any = Injects()
                        ) -> JSONResponse:
                            """
                            HTTP handler that wraps the gRPC method. It receives HTTP requests, converts them into
                            data that can be processed by the gRPC method, and returns the result as an HTTP response.

                            Args:
                                request (Request): The HTTP request object containing input data.
                                service (Any): The gRPC service instance injected from dependencies.
                                method (Any): The gRPC method to be invoked, injected from dependencies.

                            Returns:
                                JSONResponse: The response that will be sent back to the client, wrapped as a JSON response.

                            Raises:
                                HTTPException: If an error occurs while invoking the gRPC method, this exception is raised
                                with the appropriate HTTP status code and error message.
                            """
                            try:
                                data = await request.json()  # Extract request data
                                response = await method(data)  # Call the gRPC method
                                return JSONResponse(response)
                            except GRPCError as e:
                                raise HTTPException(
                                    status_code=self.__grpc_to_http_status(e.status), detail=str(e)
                                ) from e

                        # Yield the HTTP method, route, and handler for use by the framework
                        yield http_method, route, http_wrapper

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
