from esmerald.testclient import EsmeraldTestClient
from lilya.responses import HTMLResponse


async def app(scope, receive, send):
    assert scope["type"] == "http"
    response = HTMLResponse("<html><body>Hello, world!</body></html>")
    await response(scope, receive, send)


def test_application():
    client = EsmeraldTestClient(app)
    response = client.get("/")
    assert response.status_code == 200
