# Middlewares

In this section, you'll learn how to use middleware in Esmerald to modify requests and responses globally.

---

## What is Middleware?

Middleware is a function that runs before or after your route handlers. It can:

- Modify requests and responses
- Handle cross-cutting concerns like logging, authentication, CORS
- Add global behaviors

---

## Adding Middleware

To add middleware to your Esmerald application, use the `middleware` argument:

```python
from esmerald import Esmerald, Request
from esmerald.protocols import MiddlewareProtocol
from lilya.types import ASGIApp, Scope, Receive, Send
from lilya.middleware import DefineMiddleware

class LogMiddleware(MiddlewareProtocol):

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

        async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
            print(f"Incoming request: {request.method} {request.url}")
            await self.app(scope, receive, send)


app = Esmerald(
    routes=[],
    middleware=[DefineMiddleware(LogMiddleware)]
)
```

---

## Built-in Middleware Examples

### CORS Middleware

```python
from esmerald.middleware.cors import CORSMiddleware
from lilya.middleware import DefineMiddleware

app = Esmerald(
    routes=[],
    middleware=[
        DefineMiddleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"]
        )
    ]
)
```

### Trusted Hosts

```python
from esmerald.middleware.trustedhost import TrustedHostMiddleware

app = Esmerald(
    routes=[],
    middleware=[
        DefineMiddleware(TrustedHostMiddleware, allowed_hosts=["example.com", "localhost"])
    ]
)
```

---

## Custom Middleware with Classes

You can also use classes instead of functions:

```python
from lilya.middleware import DefineMiddleware

class MyMiddleware:
    async def __call__(self, request: Request, call_next):
        print("Middleware in action!")
        return await call_next(request)

app = Esmerald(
    routes=[],
    middleware=[DefineMiddleware(MyMiddleware)]
)
```

---

## Middleware Order

Middlewares are executed in the order they are added.

```python
middleware=[DefineMiddleware(A), DefineMiddleware(B)]
```

Order:
1. `A` before request
2. `B` before request
3. Route handler
4. `B` after response
5. `A` after response

---

## What's Next?

Now that you know how to work with middleware, it's time to explore background tasks.

👉 Continue to [background tasks](07-background-tasks.md) to run async jobs after sending responses.
