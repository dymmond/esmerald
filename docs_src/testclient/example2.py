from starlette.responses import HTMLResponse

from esmerald.testclient import EsmeraldTestClient


async def app(scope, receive, send):
    assert scope["type"] == "http"
    response = HTMLResponse("<html><body>Hello, world!</body></html>")
    await response(scope, receive, send)


client = EsmeraldTestClient(app)

# Set headers on the client for future requests
client.headers = {"Authorization": "..."}
response = client.get("/")

# Set headers for each request separately
response = client.get("/", headers={"Authorization": "..."})
