from esmerald.testclient import EsmeraldTestClient
from lilya.responses import HTMLResponse


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
