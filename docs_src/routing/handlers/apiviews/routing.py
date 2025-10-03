from ravyn import Ravyn, Gateway

from .controllers import UserAPIView

app = Ravyn(routes=[Gateway(handler=UserAPIView)])
