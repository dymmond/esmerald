from esmerald import Esmerald, OpenAPIConfig
from myapp.openapi.views import MyOpenAPIView


class MyOpenAPIConfig(OpenAPIConfig):
    # Do you want to generate examples?
    openapi_apiview = MyOpenAPIView
    create_examples: bool = True
    title: str = ...
    version: str = ...


app = Esmerald(routes=[...], openapi_config=MyOpenAPIConfig)
