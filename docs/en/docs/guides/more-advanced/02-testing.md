# Testing Esmerald Applications

Testing is essential to ensure your Esmerald application behaves as expected.
Esmerald provides powerful testing capabilities out of the box using `EsmeraldTestClient`, which is compatible with
pytest and async workflows.

---

## Using `EsmeraldTestClient`

The `EsmeraldTestClient` allows you to interact with your application as if it were running, without needing to start a real server.

```python
from esmerald import Esmerald, get
from esmerald.testclient import EsmeraldTestClient

@get("/ping")
def ping() -> dict:
    return {"message": "pong"}

app = Esmerald(routes=[ping])
client = EsmeraldTestClient(app)


def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}
```

---

## Using Pytest Fixtures

You can define a pytest fixture to reuse the client across multiple test functions.

```python
import pytest

@pytest.fixture
def client():
    return EsmeraldTestClient(app)


def test_ping(client):
    response = client.get("/ping")
    assert response.status_code == 200
```

---

## Testing with Authentication

If your route depends on an authenticated user, include the token or mocked credentials:

```python
from esmerald import Inject, Injects, get, HTTPException

async def get_current_user():
    return {"username": "admin"}

@get("/me", dependencies={"user": Inject(get_current_user)})
async def get_me(user: dict[str, str] = Injects()) -> dict:
    return user


def test_authenticated():
    client = EsmeraldTestClient(Esmerald(routes=[get_me]))
    response = client.get("/me")
    assert response.status_code == 200
    assert response.json() == {"username": "admin"}
```

---

## Testing Error Responses

You can test how your application handles errors:

```python
from esmerald import get, HTTPException

@get("/fail")
def fail() -> None:
    raise HTTPException(status_code=418, detail="I'm a teapot")


def test_custom_error():
    client = EsmeraldTestClient(Esmerald(routes=[fail]))
    response = client.get("/fail")
    assert response.status_code == 418
    assert response.json()["detail"] == "I'm a teapot"
```

---

## Testing Lifespan Events (Startup/Shutdown)

You can test lifecycle hooks by defining handlers and asserting side effects:

```python
called = {"startup": False, "shutdown": False}

async def on_startup():
    called["startup"] = True

async def on_shutdown():
    called["shutdown"] = True

app = Esmerald(routes=[], on_startup=[on_startup], on_shutdown=[on_shutdown])


def test_lifespan():
    with EsmeraldTestClient(app):
        assert called["startup"] is True
    assert called["shutdown"] is True
```

---

## What's Next?

Now that you know how to test Esmerald APIs:

- ✅ Use fixtures to isolate tests
- ✅ Mock dependencies like users or databases
- ✅ Validate lifecycle events and exceptions

👉 Up next: [deployment](./03-deployment) — learn how to deploy your Esmerald app into production.
