from ravyn import Gateway, WebSocketGateway

from .controllers import World, another, home, world_socket

my_urls = [
    Gateway(handler=update_product),
    Gateway(handler=home),
    Gateway(handler=another),
    Gateway(handler=World),
    WebSocketGateway(handler=world_socket),
]
