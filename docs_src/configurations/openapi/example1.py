from esmerald import Esmerald, OpenAPIConfig
from esmerald.openapi.models import Contact

openapi_config = OpenAPIConfig(
    title="My Application",
    docs_url="/mydocs/swagger",
    redoc_url="/mydocs/redoc",
    redoc_url="/mydocs/stoplight",
    contact=Contact(name="User", email="email@example.com"),
)

app = Esmerald(routes=[...], openapi_config=openapi_config)
