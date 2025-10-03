from ravyn import Gateway, Request, get
from ravyn.applications import Ravyn
from ravyn.middleware.https import HTTPSRedirectMiddleware
from ravyn.responses import PlainText
from ravyn.utils.middleware import wrap_middleware


def test_cors_allow_all(test_client_factory):
    @get()
    def homepage(request: Request) -> PlainText:
        return PlainText("Homepage", status_code=200)

    app = Ravyn(
        routes=[Gateway("/", handler=homepage)],
        middleware=[
            wrap_middleware(
                "ravyn.middleware.cors.CORSMiddleware",
                allow_origins=["*"],
                allow_headers=["*"],
                allow_methods=["*"],
                expose_headers=["X-Status"],
                allow_credentials=True,
            )
        ],
    )

    client = test_client_factory(app)

    # Test pre-flight response
    headers = {
        "Origin": "https://example.org",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "X-Example",
    }
    response = client.options("/", headers=headers)
    assert response.status_code == 200
    assert response.text == "OK"
    assert response.headers["access-control-allow-origin"] == "https://example.org"
    assert response.headers["access-control-allow-headers"] == "X-Example"
    assert response.headers["access-control-allow-credentials"] == "true"
    assert response.headers["vary"] == "Origin"

    # Test standard response
    headers = {"Origin": "https://example.org"}
    response = client.get("/", headers=headers)
    assert response.status_code == 200
    assert response.text == "Homepage"
    assert response.headers["access-control-allow-origin"] == "*"
    assert response.headers["access-control-expose-headers"] == "X-Status"
    assert response.headers["access-control-allow-credentials"] == "true"

    # Test standard credentialed response
    headers = {"Origin": "https://example.org", "Cookie": "star_cookie=sugar"}
    response = client.get("/", headers=headers)
    assert response.status_code == 200
    assert response.text == "Homepage"
    assert response.headers["access-control-allow-origin"] == "https://example.org"
    assert response.headers["access-control-expose-headers"] == "X-Status"
    assert response.headers["access-control-allow-credentials"] == "true"

    # Test non-CORS response
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "Homepage"
    assert "access-control-allow-origin" not in response.headers


def test_https_redirect_middleware(test_client_factory):
    @get()
    def homepage(request: Request) -> PlainText:
        return PlainText("OK", status_code=200)

    app = Ravyn(
        routes=[Gateway("/", handler=homepage)],
        middleware=[wrap_middleware(HTTPSRedirectMiddleware)],
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
