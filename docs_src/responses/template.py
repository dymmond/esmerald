from esmerald import Cookie, Esmerald, Gateway, get
from esmerald.datastructures import ResponseHeader, Template


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
        headers={"response-header": "template-header"},
        cookies=[Cookie(key="template-cookie", value="template-cookie")],
    )


app = Esmerald(routes=[Gateway(handler=home)])
