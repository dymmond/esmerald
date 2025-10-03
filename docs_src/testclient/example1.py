from ravyn.testclient import RavynTestClient
from lilya.responses import HTMLResponse


async def app(scope, receive, send):
    assert scope["type"] == "http"
    response = HTMLResponse("<html><body>Hello, world!</body></html>")
    await response(scope, receive, send)


def test_application():
    client = RavynTestClient(app)
    response = client.get("/")
    assert response.status_code == 200
