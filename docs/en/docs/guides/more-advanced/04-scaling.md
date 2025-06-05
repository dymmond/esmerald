# Scaling

Once your Esmerald application is in production, you may need to scale it for performance, reliability,
and high availability.

This guide outlines strategies for both vertical and horizontal scaling, load balancing, and caching.

---

## Vertical vs Horizontal Scaling

- **Vertical Scaling**: Increase CPU, memory, or I/O on a single server.
  - Pros: Simple
  - Cons: Expensive, limited

- **Horizontal Scaling**: Run multiple instances across machines or containers.
  - Pros: More resilient
  - Cons: Requires orchestration (e.g., Docker, Kubernetes)

---

## Running Multiple Instances

Use Gunicorn with multiple workers, or Docker containers behind a load balancer:

```bash
gunicorn myapp:app -k uvicorn.workers.UvicornWorker --workers 4
```

With Docker Compose:

```yaml
services:
  esmerald:
    build: .
    ports:
      - "8000:8000"
    deploy:
      replicas: 3
```

---

## Load Balancing

To distribute traffic evenly across multiple app instances:

### Nginx Example

```nginx
upstream esmerald_cluster {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://esmerald_cluster;
    }
}
```

---

## Using Kubernetes

Kubernetes makes horizontal scaling, deployment, and health checks easier.

Example `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: esmerald-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: esmerald
  template:
    metadata:
      labels:
        app: esmerald
    spec:
      containers:
        - name: esmerald
          image: my-esmerald-app:latest
          ports:
            - containerPort: 8000
```

---

## Caching

Use built-in or external caching to reduce database load and speed up requests:

- Memory: `InMemoryCache`
- Redis: `RedisCache`

Configure via `EsmeraldSettings`:

```python
from esmerald.conf import EsmeraldSettings
from esmerald.core.caches.redis import RedisCache

class Settings(EsmeraldSettings):
    cache_backend = RedisCache(url="redis://localhost:6379")
```

Use the `@cache` decorator:

```python
from esmerald import get, cache

@get("/slow")
@cache(ttl=60)
async def slow_view() -> dict:
    await asyncio.sleep(2)
    return {"status": "cached"}
```

---

## Health Checks

Expose a simple `/health` route:

```python
from esmerald import get

@get("/health")
def health() -> dict:
    return {"status": "ok"}
```

---

## Observability

Esmerald comes with a more detailed [observability](../../observables.md) section that goes into
more specific details.

Use logging, monitoring, and tracing tools:

- **Logging**: Customize Python logging
- **Monitoring**: Prometheus + Grafana
- **Tracing**: OpenTelemetry, Jaeger

---

## Summary

- ✅ Use Gunicorn or Uvicorn for workers
- ✅ Use Docker/Kubernetes for horizontal scaling
- ✅ Apply caching and health checks
- ✅ Monitor and trace in production

👉 Next: [architecture patterns](./05-architecture-patterns)
