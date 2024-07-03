from esmerald import Gateway

from .controllers import home

route_patterns = [Gateway(path="/home", handler=home)]
