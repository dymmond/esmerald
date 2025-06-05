from typing import List

from esmerald import Esmerald, EsmeraldSettings
from esmerald.middleware.clickjacking import XFrameOptionsMiddleware
from lilya.middleware import DefineMiddleware

routes = [...]

# Option one
middleware = [DefineMiddleware(XFrameOptionsMiddleware)]

app = Esmerald(routes=routes, middleware=middleware)


# Option two - Using the settings module
# Running the application with your custom settings -> ESMERALDS_SETTINGS_MODULE
class AppSettings(EsmeraldSettings):
    x_frame_options: str = "SAMEORIGIN"

    def middleware(self) -> List[DefineMiddleware]:
        return [
            DefineMiddleware(XFrameOptionsMiddleware),
        ]
