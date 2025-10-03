from ravyn import Ravyn, Gateway, Template, get
from ravyn.core.datastructures import Cookie, ResponseHeader


@get(
    path="/home",
    response_headers={"local-header": ResponseHeader(value="my-header")},
    response_cookies=[
        Cookie(key="redirect-cookie", value="redirect-cookie"),
        Cookie(key="general-cookie", value="general-cookie"),
    ],
)
def home() -> Template:
    return Template(
        name="my-tem",
        context={"user": "me"},
        alternative_template=...,
    )


app = Ravyn(routes=[Gateway(handler=home)])
