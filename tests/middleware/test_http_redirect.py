from lilya.middleware import DefineMiddleware

from ravyn import Gateway, Request, get
from ravyn.applications import Ravyn
from ravyn.middleware.https import HTTPSRedirectMiddleware
from ravyn.responses import PlainText


def test_https_redirect_middleware(test_client_factory):
    @get()
    def homepage(request: Request) -> PlainText:
        return PlainText("OK", status_code=200)

    app = Ravyn(
        routes=[Gateway("/", handler=homepage)],
        middleware=[DefineMiddleware(HTTPSRedirectMiddleware)],
    )

    client = test_client_factory(app, base_url="https://testserver")
    response = client.get("/")
    assert response.status_code == 200

    client = test_client_factory(app)
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://testserver/"

    client = test_client_factory(app, base_url="http://testserver:80")
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://testserver/"

    client = test_client_factory(app, base_url="http://testserver:443")
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://testserver/"

    client = test_client_factory(app, base_url="http://testserver:123")
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://testserver:123/"
