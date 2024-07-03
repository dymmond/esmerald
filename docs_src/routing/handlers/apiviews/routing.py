from esmerald import Esmerald, Gateway

from .controllers import UserAPIView

app = Esmerald(routes=[Gateway(handler=UserAPIView)])
