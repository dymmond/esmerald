from lilya.middleware import DefineMiddleware

from esmerald import Gateway, Request, get
from esmerald.applications import Esmerald
from esmerald.middleware.trustedhost import TrustedHostMiddleware
from esmerald.responses import PlainText


def test_trusted_host_middleware_settings(test_client_factory):
    @get()
    def homepage(request: Request) -> PlainText:
        return PlainText("OK", status_code=200)

    app = Esmerald(
        routes=[Gateway("/", handler=homepage)],
        allowed_hosts=["testserver", "*.testserver"],
    )

    client = test_client_factory(app)
    response = client.get("/")
    assert response.status_code == 200

    client = test_client_factory(app, base_url="http://subdomain.testserver")
    response = client.get("/")
    assert response.status_code == 200

    client = test_client_factory(app, base_url="http://invalidhost")
    response = client.get("/")
    assert response.status_code == 400


def test_trusted_host_middleware(test_client_factory):
    @get()
    def homepage(request: Request) -> PlainText:
        return PlainText("OK", status_code=200)

    app = Esmerald(
        routes=[Gateway("/", handler=homepage)],
        middleware=[
            DefineMiddleware(TrustedHostMiddleware, allowed_hosts=["testserver", "*.testserver"])
        ],
    )

    client = test_client_factory(app)
    response = client.get("/")
    assert response.status_code == 200

    client = test_client_factory(app, base_url="http://subdomain.testserver")
    response = client.get("/")
    assert response.status_code == 200

    client = test_client_factory(app, base_url="http://invalidhost")
    response = client.get("/")
    assert response.status_code == 400


def test_default_allowed_hosts():
    app = Esmerald()
    middleware = TrustedHostMiddleware(app)
    assert middleware.allowed_hosts == ["*"]


def test_www_redirect(test_client_factory):
    @get()
    def homepage(request: Request) -> PlainText:
        return PlainText("OK", status_code=200)

    app = Esmerald(
        routes=[Gateway("/", handler=homepage)],
        middleware=[DefineMiddleware(TrustedHostMiddleware, allowed_hosts=["www.example.com"])],
    )

    client = test_client_factory(app, base_url="https://example.com")
    response = client.get("/")
    assert response.status_code == 200
    assert response.url == "https://www.example.com/"
