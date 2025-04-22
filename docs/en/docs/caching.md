# Caching

## **1. What is Caching?**

### **1.1 Definition**

Caching is a technique that temporarily stores frequently accessed data in a fast storage layer (such as memory)
to reduce retrieval time and improve application performance. Instead of recalculating or reloading the same data
repeatedly from a slow source (e.g., a database or an API), the system can fetch it from a cache,
significantly speeding up responses.

### **1.2 Real-World Analogy**

Imagine a busy coffee shop. If a customer orders the same drink repeatedly, instead of preparing it from scratch each
time, the barista might pre-make a batch and serve it instantly when someone orders it. This is how caching works—storing
results for quick retrieval instead of performing the same task repeatedly.

### **1.3 Basic Example of Caching in Python**

```python
{!> ../../../docs_src/caching/basic.py !}
```

####  Explanation

1. We use a dictionary `cache_store` to store computed results.
2. If the result exists in the cache, it is returned instantly.
3. If not, the function performs a slow operation and caches the result for future use.
4. The second call avoids recomputation, making it much faster.

---

## **2. Benefits of Caching**

### **2.1 Faster Response Times**

Caching speeds up data retrieval by serving precomputed or preloaded results instead of performing expensive operations.

### **2.2 Reduced Load on Databases & APIs**

Fetching data from cache reduces the number of database queries or API calls, minimizing load and costs.

### **2.3 Improved Scalability**

With caching, applications handle more users efficiently without overwhelming the database or backend services.

### **2.4 Example: Database Query Without vs. With Caching**

#### **Without Caching (Slow Execution)**

```python
{!> ../../../docs_src/caching/without_caching.py !}
```

#### **With Caching (Fast Execution)**

```python
{!> ../../../docs_src/caching/with_caching.py !}
```

### Explanation

- **Without caching**, every call queries the database, making repeated calls slow.
- **With caching**, the first call fetches from the database, but subsequent calls retrieve the stored value instantly.

---

## **3. What is Caching in Esmerald?**

Esmerald provides a built-in caching system to speed up responses, reduce redundant processing, and optimize performance.
It supports multiple backends, including:

2. **In-Memory Caching** (default)
2. **Redis Caching**
3. **Custom Backends**

Esmerald’s caching system integrates seamlessly with request handlers using the `@cache` decorator.

---

## **4. How to Use Caching in Esmerald**

### **4.1 Using the `@cache` Decorator**

The `@cache` decorator allows caching responses for a defined `ttl` (time-to-live) and a chosen backend.

```python
from esmerald.utils.decorators import cache
```

#### **Basic Example**

```python
{!> ../../../docs_src/caching/simple_dec.py !}
```
✅ **First request is computed, subsequent requests are served instantly from cache.**

---

### **4.2 Specifying a Cache Backend**

#### **Using Redis as a Backend**

```python
{!> ../../../docs_src/caching/esmerald_decorator.py !}
```
✅ **The response is stored in Redis and remains available for 30 seconds.**

---

## **5. Customizing Caching in Esmerald**

### **5.1 Using Esmerald Settings to Set a Default Cache Backend**

Instead of specifying the backend every time, we can configure a global cache backend using `EsmeraldAPISettings`.

#### **Example: Setting Redis as the Default Backend**

```python
{!> ../../../docs_src/caching/settings.py !}
```

✅ **Now, all `@cache` decorators without a specified backend will use Redis.**

!!! Tip
    You can set the default backend to any supported backend, including custom ones.
    This allows you to maintain a consistent caching strategy across your application.

    The default cache backend is the InMemoryCache, which is used if no backend is specified.

---

## **6. Building Custom Caching Backends**

You can extend Esmerald’s caching system by creating your own backend.

### **6.1 Custom File-Based Cache Backend**

To create a custom backend, you need to implement the `CacheBackend` interface.

That can be imported from:

```python
from esmerald.core.protocols.cache import CacheBackend
```

### Example

```python
{!> ../../../docs_src/caching/custom_backend.py !}
```

✅ **This custom backend caches data in files instead of memory or Redis.**

### **6.2 Using the Custom Backend in Esmerald**

Now you can use the custom backend in your Esmerald application.

```python
{!> ../../../docs_src/caching/usage.py !}
```

✅ **Data is now cached in files instead of memory or Redis.**

---

## Recap

✅ **Esmerald provides an easy-to-use caching system with multiple backends.**
✅ **You can use the `@cache` decorator to cache responses.**
✅ **You can set a global cache backend via `EsmeraldAPISettings`.**
✅ **You can create custom caching backends to store data in different ways.**
