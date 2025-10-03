from ravyn import Ravyn, OpenAPIConfig
from ravyn.openapi.models import Contact

openapi_config = OpenAPIConfig(
    title="My Application",
    docs_url="/mydocs/swagger",
    redoc_url="/mydocs/redoc",
    stoplight_url="/mydocs/stoplight",
    contact=Contact(name="User", email="email@example.com"),
)

app = Ravyn(routes=[...], openapi_config=openapi_config)
