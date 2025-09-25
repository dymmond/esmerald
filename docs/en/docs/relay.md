# Relay

Since Esmerald is built on top of Lilya, this means that Esmerald can use almost everything Lilya
has without too much of a trouble and out-of-the-box.

One of those things is the **Relay**.

A **mountable ASGI relay** for Esmerald that forwards HTTP **and optionally WebSocket** traffic to an upstream service.

It preserves **methods, headers, cookies, query parameters, and streaming bodies**, while supporting retries,
timeout handling, header policies, and structured logging.

Typical use case: you have **two Esmerald apps**:

- **App 1** (Authentication) handles login, logout, refresh, etc.
- **App 2** (Your main API) wants to expose `GET/POST /auth/...` publicly but **forward** to App 1 under the hood.

With `Relay`, you mount a single catch‑all route on App 2 (e.g., `/auth`) that **proxies everything** to App 1.

## Why a Proxy?

- **Single public surface**: Expose `/auth/**` from App 2; keep App 1 private.
- **No duplication**: Don't re-implement login/logout; just forward.
- **Transparent behaviour**: Requests/responses stream through without buffering.
- **Header controls**: Drop hop-by-hop headers, or use an allow-list mode.
- **Retries & timeouts**: Built-in retry policy with exponential backoff; maps timeouts to **504 Gateway Timeout**.
- **Cookie rewriting**: Adjust or strip `Domain` on `Set-Cookie`.
- **WebSocket proxying**: (optional) Proxy WS traffic bidirectionally.
- **Observability**: Structured logging hooks for retries, errors, and timeouts.
- **Test-friendly**: In-memory with `httpx.ASGITransport` or WS echo servers.

### Before continuing

Esmerald uses `httpx` to create the `Relay` object. This means, to work with it **you must**:

```shell
pip install httpx
```

## Quickstart

```python
# app.py
from esmerald import Esmerald, Include
from lilya.contrib.proxy.relay import Relay

proxy = Relay(
    target_base_url="http://auth-service:8000",  # internal service base URL
    upstream_prefix="/",  # map "/auth/<path>" -> "/<path>" upstream
    preserve_host=False,  # set Host to auth-service
    # Optional: drop the Domain attribute from Set-Cookie so it binds to current host
    rewrite_set_cookie_domain=lambda _original: "",
    max_retries=2,
    retry_backoff_factor=0.2,
)

# The Main Esmerald application
app = Esmerald(
    routes=[
        Include("/auth", app=proxy),  # Everything under /auth/** is proxied
    ],
    on_startup=[proxy.startup],  # start shared HTTP client (pool)
    on_shutdown=[proxy.shutdown],  # close it cleanly
)
```

**What you get:**

- `GET /auth/login`:  proxied as `GET http://auth-service:8000/login`
- `POST /auth/session?next=%2Fprofile`:  proxied to upstream with same query, headers, cookies, and body
- `Set-Cookie` from upstream is forwarded; domain rewrite is supported if needed.

## How it works (request lifecycle)

1. **Mounting**: You `Include("/auth", app=proxy)` to mount the proxy under `/auth`.
2. **Path & query**: The Esmerald router strips `/auth` and passes the remainder (e.g., `/login`) to the proxy. The proxy **joins** it with `upstream_prefix` and `target_base_url`. The **raw query string** is forwarded unchanged.
3. **Headers**:
    - **Drops hop‑by‑hop** headers on the inbound hop (e.g., `Connection`, `TE`, `Upgrade`, `Transfer-Encoding`).
    - Adds `X-Forwarded-For`, `X-Forwarded-Proto`, and `X-Forwarded-Host` (the **original** host seen by the proxy).
    - `Host` header: if `preserve_host=False`, sets `Host` to the upstream host; else preserves client host.
4. **Body streaming**: For non `GET`/`HEAD`/`OPTIONS`, the request body is **streamed** to upstream, the upstream response body is **streamed back** to the client (no buffering).
5. **Response headers**: Drops hop‑by‑hop, forwards others. Multiple `Set-Cookie` headers are kept as **separate** header lines.
6. **Cookie rewrite** (optional): You can change/remove the `Domain` attribute in `Set-Cookie` (useful for auth across subdomains).
7. **Errors**:
    - Network/connection errors to upstream are returned as **`502 Bad Gateway`**.
    - (Optional) You can extend to detect timeouts and return **`504 Gateway Timeout`**.

## Installation & imports

You'll keep the proxy as part of your project's contrib code or ship it as `lilya.contrib.proxy`. The examples below assume a local module:

```python
from lilya.contrib.proxy.relay import Relay
```
## API reference

### `Relay(...)`

```python
Relay(
    target_base_url: str,
    *,
    upstream_prefix: str = "/",
    preserve_host: bool = False,
    rewrite_set_cookie_domain: Callable[[str], str] | None = None,
    timeout: httpx.Timeout | float = httpx.Timeout(10, connect=5, read=10, write=10),
    limits: httpx.Limits = httpx.Limits(max_connections=100, max_keepalive_connections=20),
    follow_redirects: bool = False,
    extra_request_headers: dict[str, str] | None = None,
    drop_request_headers: Iterable[str] = (),
    drop_response_headers: Iterable[str] = (),
    allow_request_headers: Iterable[str] | None = None,
    allow_response_headers: Iterable[str] | None = None,
    transport: httpx.BaseTransport | None = None,
    max_retries: int = 0,
    retry_backoff_factor: float = 0.2,
    retry_statuses: Sequence[int] = (502, 503, 504),
    retry_exceptions: tuple[type[Exception], ...] = (httpx.ConnectError, httpx.ReadTimeout),
    logger: logging.Logger | None = None,
)
```

**Parameters**:

- `target_base_url`: **Required.** Base URL of the upstream (e.g., `http://auth-service:8000`). The path part is used as the root to join.
- `upstream_prefix`: The prefix to prepend upstream (default `/`). Example: If you mount at `/auth` but need `/api/v1` upstream, set `upstream_prefix="/api/v1"`.
- `preserve_host`: Defaults to `False`. If `False`, sets outbound `Host` to the upstream's host; if `True`, forwards the client's `Host`.
- `rewrite_set_cookie_domain`: Callback for `Set-Cookie` Domain rewriting:
    - Return **`None`**:  no changes;
    - Return **`""`**:  **drop** the `Domain` attribute (binds cookie to current host);
    - Return **`"example.com"`**:  set `Domain=example.com`.
- `timeout`: `httpx.Timeout` or float. **Recommended**: keep connect/read/write specified.
- `limits`: `httpx.Limits` for connection pooling and keepalive.
- `follow_redirects`: Whether to follow upstream redirects or pass them through. Default: `False` (proxied as‑is).
- `extra_request_headers`: Dict to **add/override** headers sent to upstream (e.g., service auth token).
- `drop_request_headers`: Iterable of header names to **strip** from the inbound request.
- `drop_response_headers`: Iterable of header names to **strip** from the upstream response.
- `transport`: Inject an `httpx.BaseTransport` (e.g., `httpx.ASGITransport(app=upstream_app)`) for **in‑memory tests**.

**Lifecycle**:

- `await proxy.startup()` — creates a shared `httpx.AsyncClient`.
- `await proxy.shutdown()` — closes the client.

## WebSocket Support

If you install `websockets`:

```shell
pip install websockets
```

You can proxy WS endpoints too:

```python
proxy = Relay("http://chat-service.local")
app = Esmerald(routes=[Include("/ws", app=proxy)])
```

* Incoming `ws://proxy.local/ws/room`: Proxied to `ws://chat-service.local/room`
* Frames (text/binary) are streamed bidirectionally.
* On upstream close, the proxy emits `1000` (normal closure).
* On timeout/error, emits `1011` (internal error).

## Error handling

* **Connection errors**: `502 Bad Gateway`
* **Timeouts**: `504 Gateway Timeout`
* **Retryable statuses/exceptions**: Retries up to `max_retries`, with exponential backoff.
* **Structured logging**: Each error/retry/timeout is logged as `reverse_proxy.<event>` with context.

## Header handling

* **Hop-by-hop headers dropped** (always):
  `Connection, Keep-Alive, Proxy-Authenticate, Proxy-Authorization, TE, Trailer, Transfer-Encoding, Upgrade`
* **Drop lists**: `drop_request_headers` and `drop_response_headers`
* **Allow lists**: Use `allow_request_headers` / `allow_response_headers` to only forward a whitelist.
* **Forwarded headers**: Always inject `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host`.
```
Connection, Keep-Alive, Proxy-Authenticate, Proxy-Authorization,
TE, Trailer, Transfer-Encoding, Upgrade
```

!!! Note
    The proxy or HTTP stack may set its **own** connection management header on the **outbound** hop (e.g., `connection: keep-alive`). This is correct behaviour and doesn't mean your client's hop‑by‑hop headers were forwarded.

**Forwarded headers added**:

- `X-Forwarded-For`: the client IP appended to any existing chain
- `X-Forwarded-Proto`: `http` or `https`
- `X-Forwarded-Host`: the **original** `Host` seen by the proxy

## Cookie handling

Upstream often sets cookies with `Domain=auth.example.com`. If your public host is `api.example.com` (or just `example.com`), the browser won't accept/send those cookies to your public domain.

**Solutions**:

- **Drop `Domain`** on `Set-Cookie` via `rewrite_set_cookie_domain=lambda _: ""`: Cookie binds to the **current host**.
- **Rewrite** to a specific domain: `rewrite_set_cookie_domain=lambda _: "example.com"`: Cookie becomes valid for that domain and subdomains.

!!! Tip
    Ensure correct `SameSite` and `Secure` flags for cross‑site cookies (e.g., `SameSite=None; Secure` if needed).

## Path rewriting

- `Include("/auth", app=proxy)` mounts the proxy at `/auth/**`.
- The outbound path is constructed by **joining** `upstream_prefix` and the mounted path remainder.

**Example**:

- Incoming: `/auth/login?next=%2Fprofile`
- `upstream_prefix="/"`:  Upstream request: `/<"login">?next=%2Fprofile`
- `upstream_prefix="/api/v1"`:  Upstream request: `/api/v1/login?next=%2Fprofile`

## Error mapping

Any `httpx.RequestError` (connect errors, DNS, refused, etc.) is returned as **`502 Bad Gateway`**.

You can extend the implementation to:

- Map **read/write/overall timeout** to **`504 Gateway Timeout`**.
- Map **TLS or protocol errors** to `502` with more granular logs.

### Retry behavior

- `max_retries=2, retry_backoff_factor=0.2`: delays: `0.2s, 0.4s`
- Retries triggered by:
    * Status codes in `retry_statuses`
    * Exceptions in `retry_exceptions`
- Timeout: Maps to `504` if retries exhausted

## CORS

When the browser calls only **App 2** (the proxy), and App 2 server‑side calls Upstream, **CORS is not needed** on the upstream service. Configure CORS **only** on the public proxy if your frontend origin differs.

## Security hardening

- **SSRF**: Never allow clients to influence the upstream URL. Keep `target_base_url` fixed and do not read URLs from request parameters.
- **Sensitive headers**:
    - Decide whether to forward `Authorization` and `Cookie`. For public proxies between trusted services, forwarding is typical.
    - You can **drop/allowlist** headers via `drop_request_headers` and `drop_response_headers`.
- **Rate limiting / abuse protection**: Consider enabling it on your public proxy route.
- **Request size limits**: If your ASGI server/framework offers max body size, enable it if appropriate.

## Real‑world recipes

### 1. Auth service under `/auth/**` with Domain drop

```python
proxy = Relay(
    "http://auth-service:8000",
    upstream_prefix="/",
    rewrite_set_cookie_domain=lambda _: "",  # drop Domain
)
app = Esmerald(
    routes=[Include("/auth", app=proxy)],
    on_startup=[proxy.startup],
    on_shutdown=[proxy.shutdown],
)
```

**Why**: Cookies set by `auth-service` become host‑scoped to your public host (where the browser is talking).

### 2. Proxy a versioned API under `/billing/**`:  `/api/v1/**` upstream

```python
billing = Relay(
    "http://billing-service.internal",
    upstream_prefix="/api/v1",
)
app = Esmerald(
    routes=[Include("/billing", app=billing)],
    on_startup=[billing.startup],
    on_shutdown=[billing.shutdown],
)
```

**Why**: Your public path doesn't expose upstream's versioning scheme.

### 3. Inject a service‑to‑service token

```python
secret = os.getenv("INTERNAL_SERVICE_TOKEN")

proxy = Relay(
    "http://internal:9000",
    extra_request_headers={"X-Internal-Auth": secret},
    drop_request_headers=["x-forwarded-for"],  # example of additional drops
)
```

**Why**: Upstream can trust calls because they include a **shared secret** added by the proxy (not by clients).

### 4. Preserve the client `Host` header (rare, but occasionally required)

```python
proxy = Relay("http://upstream:8000", preserve_host=True)
```

**Why**: Some upstreams compute logic based on `Host`. Most setups prefer `preserve_host=False`.

### 5. Follow upstream redirects (opt‑in)

```python
proxy = Relay(
    "http://legacy:8080",
    follow_redirects=True,
)
```

**Why**: If upstream uses redirects internally, the proxy can follow them; otherwise, they pass through to the client.

## Testing guide

You can test the entire chain **in‑memory** (no sockets) with `httpx.ASGITransport`.

### Dummy upstream (ASGI app)

Use AnyIO primitives (not `asyncio.sleep`) so tests run on both asyncio and trio backends:

```python
# tests/conftest.py (excerpt)
import anyio
import json
import httpx
import pytest

from esmerald import Esmerald, Include
from lilya.contrib.proxy.relay import Relay


class DummyUpstream:
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self._text(send, 404, "Not Found");
            return

        method, path = scope["method"], scope["path"]
        qs = scope.get("query_string", b"").decode("latin-1")

        headers = {k.decode("latin-1"): v.decode("latin-1") for k, v in scope["headers"]}
        body = b""
        while True:
            event = await receive()
            if event["type"] == "http.request":
                body += event.get("body", b"")
                if not event.get("more_body", False):
                    break
            elif event["type"] == "http.disconnect":
                break

        if path.endswith("/echo"):
            return await self._json(send, 200, {
                "method": method,
                "path": path,
                "query": qs,
                "headers": {
                    "host": headers.get("host"),
                    "x-forwarded-for": headers.get("x-forwarded-for"),
                    "x-forwarded-proto": headers.get("x-forwarded-proto"),
                    "x-forwarded-host": headers.get("x-forwarded-host"),
                    "connection": headers.get("connection"),
                    "te": headers.get("te"),
                    "upgrade": headers.get("upgrade"),
                    "transfer-encoding": headers.get("transfer-encoding"),
                    "custom-header": headers.get("custom-header"),
                    "content-type": headers.get("content-type"),
                },
                "body_len": len(body),
            })

        if path.endswith("/set-cookie"):
            cookies = [
                "session=abc123; Path=/; HttpOnly; Domain=auth.local; SameSite=Lax",
                "refresh=zzz; Path=/; Secure; SameSite=None",
            ]
            return await self._text(send, 200, "ok",
                                    extra=[(b"set-cookie", c.encode("latin-1")) for c in cookies])

        if path.endswith("/large"):
            await send({"type": "http.response.start", "status": 200,
                        "headers": [(b"content-type", b"application/octet-stream")]})
            chunk = b"x" * 65536
            for _ in range(16):
                await send({"type": "http.response.body", "body": chunk, "more_body": True})
                await anyio.sleep(0)
            await send({"type": "http.response.body", "body": b"", "more_body": False})
            return

        await self._text(send, 404, "Not Found")

    async def _text(self, send, status, text, extra=None):
        headers = [(b"content-type", b"text/plain; charset=utf-8")]
        if extra: headers.extend(extra)
        await send({"type": "http.response.start", "status": status, "headers": headers})
        await send({"type": "http.response.body", "body": text.encode("utf-8")})

    async def _json(self, send, status, payload):
        data = json.dumps(payload).encode("utf-8")
        await send({"type": "http.response.start", "status": status,
                    "headers": [(b"content-type", b"application/json")]})
        await send({"type": "http.response.body", "body": data})


@pytest.fixture
def upstream_app():
    return DummyUpstream()


@pytest.fixture
def proxy_and_app(upstream_app):
    upstream_transport = httpx.ASGITransport(app=upstream_app)
    proxy = Relay(
        "http://auth-service.local",
        upstream_prefix="/",
        preserve_host=False,
        rewrite_set_cookie_domain=lambda _orig: "",
        transport=upstream_transport,  # in‑memory upstream
    )
    app = Esmerald(
        routes=[Include("/auth", app=proxy)],
        on_startup=[proxy.startup],
        on_shutdown=[proxy.shutdown],
    )
    return proxy, app, upstream_app


@pytest.fixture
async def client(proxy_and_app):
    proxy, app, _ = proxy_and_app
    await proxy.startup()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    await proxy.shutdown()
```

### Example tests

**Path & query**

```python
@pytest.mark.anyio
async def test_get_proxies_path_and_query(client):
    r = await client.get("/auth/echo?x=1&y=two", headers={"custom-header": "ok"})
    assert r.status_code == 200
    d = r.json()
    assert d["method"] == "GET"
    assert d["path"].endswith("/echo")
    assert d["query"] == "x=1&y=two"
    assert d["headers"]["custom-header"] == "ok"
```

**Body streaming**

```python
@pytest.mark.anyio
async def test_post_streams_body(client):
    payload = b"A" * 12345
    r = await client.post("/auth/echo", content=payload,
                          headers={"content-type": "application/octet-stream"})
    assert r.status_code == 200
    assert r.json()["body_len"] == len(payload)
```

**Hop‑by‑hop stripping**

```python
@pytest.mark.anyio
async def test_hbh_headers_not_forwarded(client):
    r = await client.get("/auth/echo", headers={
        "Connection": "chunky-monkey",
        "TE": "trailers",
        "Upgrade": "h2c",
        "Transfer-Encoding": "chunked",
    })
    h = r.json()["headers"]
    assert h["te"] is None
    assert h["upgrade"] is None
    assert h["transfer-encoding"] is None
    assert h["connection"] != "chunky-monkey"  # proxy may set its own policy
```

**Host handling**

```python
@pytest.mark.anyio
async def test_preserve_host_false_sets_upstream_host(proxy_and_app):
    proxy, app, _ = proxy_and_app
    await proxy.startup()
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://public.host") as c:
            r = await c.get("/auth/echo")
            assert r.json()["headers"]["host"] == "auth-service.local"
    finally:
        await proxy.shutdown()
```

**Set‑Cookie domain rewrite**

```python
def get_set_cookie_headers(response) -> list[str]:
    if hasattr(response.headers, "get_list"):
        return response.headers.get_list("set-cookie")
    if hasattr(response.headers, "getlist"):
        return response.headers.getlist("set-cookie")
    return [v.decode("latin-1") for (k,v) in response.headers.raw if k.lower() == b"set-cookie"]

@pytest.mark.anyio
async def test_cookie_domain_rewrite(client):
    r = await client.get("/auth/set-cookie")
    cookies = get_set_cookie_headers(r)
    assert len(cookies) == 2
    c1, c2 = cookies
    assert "session=abc123" in c1 and "Domain=" not in c1
    assert "refresh=zzz" in c2
```

**Upstream errors: 502**

```python
class RaiseOnEnter:
    def __init__(self, exc): self.exc = exc
    async def __aenter__(self): raise self.exc
    async def __aexit__(self, *_): return False

@pytest.mark.anyio
async def test_upstream_error_maps_to_502(proxy_and_app, monkeypatch):
    proxy, app, _ = proxy_and_app
    await proxy.startup()
    try:
        def stream_replace(*_a, **_k):
            req = httpx.Request("GET", "http://auth-service.local/echo")
            return RaiseOnEnter(httpx.ConnectError("boom", request=req))
        monkeypatch.setattr(proxy._client, "stream", stream_replace)

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as cli:
            r = await cli.get("/auth/echo")
        assert r.status_code == 502 and "Upstream error" in r.text
    finally:
        await proxy.shutdown()
```

**Large streaming**

```python
@pytest.mark.anyio
async def test_large_streaming_download(client):
    r = await client.get("/auth/large")
    assert r.status_code == 200
    size = 0
    async for chunk in r.aiter_bytes():
        size += len(chunk)
    assert size == 1024 * 1024
```

### Testing WS

Example with an echo server:

```python
import pytest, websockets, anyio

@pytest.mark.anyio
async def test_ws_proxy(proxy_and_app):
    async def echo(ws):
        async for msg in ws:
            await ws.send(msg)

    async with websockets.serve(echo, "127.0.0.1", 0) as server:
        uri = f"ws://{server.sockets[0].getsockname()[0]}:{server.sockets[0].getsockname()[1]}"
        proxy = Relay(uri)
        ...
```

## Troubleshooting

### Relay not started. Call startup() on app startup.

- **Cause**: App lifespan didn't run (common when using `httpx.ASGITransport(app=app)`).
- **Fix**:
    - Call `await proxy.startup()` in your test fixture, and `await proxy.shutdown()` on teardown; **or**
    - Use `ASGITransport(app=app)` and enable the lifespan (if supported by your httpx version).

### `TypeError: object _AsyncGeneratorContextManager can't be used in 'await' expression`

- **Cause**: Used `await client.stream(...)` instead of `async with client.stream(...)`.
- **Fix**: Always use `async with`.

### `TypeError: 'coroutine' object is not an async context manager`

- **Cause**: Monkeypatched `.stream` with an async function.
- **Fix**: Patch with a **regular function** that raises immediately, or return an object implementing `__aenter__/__aexit__`.

### Trio backend error about `asyncio` yields

- **Cause**: Using `asyncio.sleep()` in tests while running under Trio.
- **Fix**: Use `anyio.sleep()` in test doubles; or force `anyio_backend="asyncio"` in tests.

### Only one `Set-Cookie` header observed

- **Cause**: Reading cookies with `.get("set-cookie")` which joins values.
- **Fix**: Use `headers.get_list("set-cookie")` (httpx), `headers.getlist(...)`, or `headers.raw`.

## Performance & tuning

- **Connection pooling**: Tweak `httpx.Limits(max_connections=..., max_keepalive_connections=...)`.
- **Timeouts**: Set explicit `connect`, `read`, `write`, and total budgets based on upstream SLAs.
- **Streaming**: This proxy **streams** both request and response bodies to minimize memory. Avoid buffering large payloads.
- **Keep‑alive**: Default keep‑alive reduces latency under load.
- **Backpressure**: Streaming via `httpx.AsyncClient.stream` naturally applies backpressure across the ASGI boundary.

## Observability

- **Logging**: Log upstream URL, method, status, duration, and upstream errors. You can wrap the proxy or fork it to inject your logger.
- **Tracing**: Propagate trace headers (`traceparent`, `x-request-id`) via `extra_request_headers` or a custom header policy.
- **Metrics**: Count 2xx/4xx/5xx, upstream durations, retry/timeout events (if you implement retries).

```python
import logging

logger = logging.getLogger("proxy")
proxy = Relay("http://upstream", logger=logger)
```

Produces log lines like:

```
reverse_proxy.upstream_retryable_error url='http://upstream/echo' attempt=1 error='ConnectError(...)'
reverse_proxy.upstream_timeout url='http://upstream/echo' attempt=2 error='ReadTimeout(...)'
```