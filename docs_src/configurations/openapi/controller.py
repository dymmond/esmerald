from ravyn import Ravyn

app = Ravyn(
    routes=[...],
    docs_url="/another-url/swagger",
    redoc_url="/another-url/redoc",
    stoplight_url="/another-url/stoplight",
)
