from esmerald.testclient import EsmeraldTestClient
from lilya.responses import HTMLResponse


async def app(scope, receive, send):
    assert scope["type"] == "http"
    response = HTMLResponse("<html><body>Hello, world!</body></html>")
    await response(scope, receive, send)


client = EsmeraldTestClient(app)

# Send a single file
with open("example.txt", "rb") as f:
    response = client.post("/form", files={"file": f})


# Send multiple files
with open("example.txt", "rb") as f1:
    with open("example.png", "rb") as f2:
        files = {"file1": f1, "file2": ("filename", f2, "image/png")}
        response = client.post("/form", files=files)
