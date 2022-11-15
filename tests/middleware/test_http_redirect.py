from esmerald.applications import Esmerald
from starlette.middleware import Middleware
from esmerald.middleware.https import HTTPSRedirectMiddleware
from esmerald.responses import PlainTextResponse
from esmerald import Gateway, get, Request


def test_https_redirect_middleware(test_client_factory):
    @get()
    def homepage(request: Request) -> PlainTextResponse:
        return PlainTextResponse("OK", status_code=200)

    app = Esmerald(
        routes=[Gateway("/", handler=homepage)],
        middleware=[Middleware(HTTPSRedirectMiddleware)],
    )

    client = test_client_factory(app, base_url="https://testserver")
    response = client.get("/")
    assert response.status_code == 200

    client = test_client_factory(app)
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://testserver/"

    client = test_client_factory(app, base_url="http://testserver:80")
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://testserver/"

    client = test_client_factory(app, base_url="http://testserver:443")
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://testserver/"

    client = test_client_factory(app, base_url="http://testserver:123")
    response = client.get("/", allow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://testserver:123/"
