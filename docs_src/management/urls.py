from esmerald import Gateway

from .views import home

route_patterns = [Gateway(path="/home", handler=home)]
