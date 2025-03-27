# service.py
from __future__ import annotations

import grpc

from esmerald import Esmerald
from esmerald.grpc.gateway import GrpcGateway
from esmerald.grpc.register import register_grpc_http_routes

# Import generated classes
from tests.grpc.protocol import greeter_pb2, greeter_pb2_grpc


# -------------------------------
# gRPC Service Implementation
# -------------------------------
class GreeterService(greeter_pb2_grpc.GreeterServicer):
    async def SayHello(self, request, context):
        # Adapt to both dicts and protobuf messages.
        if isinstance(request, dict):
            name = request.get("name", "")
        else:
            name = request.name
        if name == "error":
            if hasattr(context, "set_code"):
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("Invalid request")
            return greeter_pb2.HelloReply()  # Return an empty reply.
        message = f"Hello, {name}!"
        if isinstance(request, dict):
            # Return a dict for HTTP mode.
            return {"message": message}
        else:
            # Return a protobuf message.
            return greeter_pb2.HelloReply(message=message)


# -------------------------------
# GRPC Gateway and HTTP Exposure
# -------------------------------
# Here we wrap our GreeterService in a GrpcGateway. This will expose HTTP endpoints
# that internally call the gRPC service.
# Attach the generated registration function as a class attribute.
GreeterService.__add_to_server__ = staticmethod(greeter_pb2_grpc.add_GreeterServicer_to_server)

grpc_gateway = GrpcGateway(path="/grpc", services=[GreeterService])
app = Esmerald(
    routes=[],
    on_startup=[grpc_gateway.startup],
    on_shutdown=[grpc_gateway.shutdown],
    enable_openapi=True,
)
# Register the HTTP endpoints – this creates REST endpoints that call the gRPC service.
register_grpc_http_routes(app=app, grpc_gateways=[grpc_gateway])

# For local testing, you can run the app directly:
if __name__ == "__main__":
    app.run()
