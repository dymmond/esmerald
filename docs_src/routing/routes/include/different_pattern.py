from esmerald import Gateway, WebSocketGateway

from .views import World, another, home, world_socket

my_urls = [
    Gateway(handler=update_product),
    Gateway(handler=home),
    Gateway(handler=another),
    Gateway(handler=World),
    WebSocketGateway(handler=world_socket),
]
