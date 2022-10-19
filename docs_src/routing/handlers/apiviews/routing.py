from esmerald import Esmerald, Gateway

from .views import UserAPIView

app = Esmerald(routes=[Gateway(handler=UserAPIView)])
