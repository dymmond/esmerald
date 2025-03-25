from lilya.types import ASGIApp

from esmerald.grpc.gateway import GrpcGateway


def register_grpc_http_routes(app: ASGIApp, grpc_gateway: GrpcGateway) -> None:
    """
    Registers HTTP routes corresponding to gRPC service methods to the Esmerald app.

    This function takes a gRPC gateway (GrpcGateway) instance that maps gRPC service
    methods to HTTP routes and registers these HTTP routes to the provided Esmerald app.

    The HTTP routes are dynamically created based on the service methods in the
    GrpcGateway instance, and the appropriate handler is attached for each HTTP method
    (GET, POST, PUT, DELETE, PATCH). The handler is a wrapper that invokes the
    corresponding gRPC method and returns the result as a JSON response.

    Args:
        app (ASGIApp): The Esmerald app instance where the HTTP routes will be registered.
        grpc_gateway (GrpcGateway): The GrpcGateway instance that contains the gRPC services
                                    and their method mappings to HTTP routes.

    Yields:
        None: This function does not return any values, but it registers routes in-place.
    """
    for http_method, route, handler in grpc_gateway._register_grpc_http_endpoints():
        # Registers the HTTP route with the corresponding method and handler
        app.add_route(http_method, route, handler)
