# Routing

In this section, you'll learn how to organize your application using routes, include routers, and build modular APIs in
Esmerald.

---

## Basic Routes

You can define routes directly using decorators like `@get`, `@post`, `@put`, etc.

```python
from esmerald import get

@get("/hello")
def say_hello() -> dict:
    return {"message": "Hello, world!"}
```

---

## Path Parameters

Capture dynamic segments of the path with parameters:

```python
@get("/users/{user_id}")
def get_user(user_id: int) -> dict:
    return {"user_id": user_id}
```

You can specify types (int, str, float) for automatic validation.

---

## Query Parameters

Query strings like `?active=true` are handled as function arguments:

```python
@get("/search")
def search(term: str, active: bool = True) -> dict:
    return {"term": term, "active": active}
```

---

## Grouping Routes with Routers

Use `Include` to organize and group related endpoints:

```python
from esmerald import Esmerald, Include, get, Gateway

@get("/ping")
def ping() -> dict:
    return {"message": "pong"}


@get("/")
def users() -> dict:
    return {}

@get("/{user_id}")
def user_id(user_id: int) -> dict:
    return {"user_id": user_id}


users = [
    Gateway(handler=users),
    Gateway(handler=user_id),
]

app = Esmerald(
    routes=[
        Include("/users", routes=users),
        Include("/health", routes=[ping]),
    ]
)
```

- `/users/` lists users
- `/users/{user_id}` returns a specific user
- `/health/ping` responds with pong

---

## Nested Includes

You can nest `Include` for even deeper structure:

```python
@get("/")
def stats() -> dict:
    return {"status": "ok"}


admin_routes = [
    Gateway("/stats", handler=stats)
]

routes = [
    Include("/admin", routes=admin_routes),
    Include("/api", routes=[Include("/v1", routes=[...])])
]
```

---

## Tags for Documentation

Add `tags=[...]` to categorize endpoints in OpenAPI:

```python
@get("/users", tags=["Users"])
def list_users():
    return ["alice", "bob"]
```

---

## What's Next?

Now that you're comfortable structuring your app with routes and includes, it's time to learn about middlewares.

👉 Continue to [middlewares](06-middlewares.md) to handle things like logging, CORS, sessions, and more.
