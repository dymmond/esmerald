# Observables

## **1. What Are Observables?**

Observables are a programming concept used to implement the **Observer Pattern**, where a function (or object) **reacts to events dynamically**. This means that:

- **An event is emitted** when something significant happens (e.g., a user registers, a payment is processed, etc.).
- **Subscribers (listeners) react to that event** without direct coupling to the emitter.
- This allows for a highly **flexible, decoupled, and scalable** event-driven architecture.

Observables can be thought of as a **stream of events**, much like how promises handle asynchronous data but **continuously** over time. Instead of handling a single future result, observables enable **reactive programming**, where parts of the system automatically respond to changes.

## **2. Benefits of Using Observables**

Using observables in an application, especially within Esmerald, comes with several advantages:

### ✅ **Decoupling & Maintainability**
Observables help separate **event producers (emitters)** from **event consumers (listeners)**. This **reduces dependencies** and makes the system **easier to maintain**.

### ✅ **Scalability & Extensibility**
By using observables, new features can be **added without modifying existing code**. Developers can subscribe to events dynamically instead of changing core logic.

### ✅ **Concurrency & Efficiency**
Using **async-based event dispatching**, Esmerald handles multiple listeners **without blocking execution**. This improves performance in real-time applications.

### ✅ **Code Reusability**
Once an observable event is defined, it can be **reused across multiple parts** of the application, reducing redundant logic.

### ✅ **Better Error Handling**
Observables allow for centralized error handling on emitted events, making debugging more manageable.

## **3. Why Should You Use Observables?**

Observables are useful in scenarios where **something happens** and multiple parts of the system need to react **independently**.

For example:

- **User Registration Events** → Send a welcome email, log activity, and assign default roles.
- **Payment Processing** → Notify the user, update the database, and trigger order fulfillment.
- **Live Data Streaming** → Real-time notifications, stock updates, or WebSocket messages.
- **Background Tasks** → Perform long-running operations (e.g., data processing, cleanup).
- **Logging & Monitoring** → Collect application metrics without affecting request performance.

In **Esmerald**, observables allow for an **efficient and scalable event-driven** approach, making it ideal for high-performance applications.

---

## **4. How Observables Are Applied in Esmerald**

Esmerald provides **built-in support for observables** through the `@observable` decorator and `EventDispatcher`.

### **🔹 Key Components**

1. **`@observable` Decorator**
   - Defines functions that can **emit** and/or **listen** for events.
2. **`EventDispatcher`**
   - Manages event subscriptions and emissions asynchronously.
3. **Async and Sync Support**
   - Supports both **asynchronous** and **synchronous** event handlers.
4. **Concurrency Handling**
   - Uses `anyio.create_task_group()` to handle multiple listeners in parallel.

---

## **5. Real-World Examples Using Esmerald**

### **Example 1: User Registration with Multiple Side Effects**
A user registers, and multiple actions occur **without coupling the logic together**.

```python
{!> ../../../docs_src/observables/registration.py !}
```
**What Happens Here?**
✅ A **user registers** → Event `"user_registered"` is **emitted**.
✅ The system **automatically triggers listeners** → **Email is sent, roles are assigned.**
✅ No direct dependency → Can **easily add more listeners** in the future.

---

### **Example 2: Payment Processing**
When a payment is made, multiple systems react to the event.

```python
{!> ../../../docs_src/observables/payment.py !}
```

✅ **One event triggers multiple independent processes.**
✅ **Fully decoupled logic for better maintainability.**

---

### **Example 3: Logging User Activity**

```python
{!> ../../../docs_src/observables/logging.py !}
```

✅ **Logs login activity without modifying authentication logic.**

---

### **Example 4: Real-Time Notifications**

```python
{!> ../../../docs_src/observables/realtime.py !}
```

✅ **Users get notified immediately after a comment is posted.**

---

### **Example 5: Background Data Processing**

```python
{!> ../../../docs_src/observables/background.py !}
```

✅ **Heavy file processing runs asynchronously, without blocking the request.**

---

### **Example 6: Scheduled Tasks & Cleanup Jobs**

```python
{!> ../../../docs_src/observables/scheduler.py !}
```

✅ **Scheduled task runs automatically** → **Triggers multiple cleanup tasks.**

---

## **Conclusion**

Observables in Esmerald allow developers to build **efficient, scalable, and maintainable** event-driven applications. By leveraging `@observable` and `EventDispatcher`:

✔️ **Events are decoupled from logic, improving maintainability.**
✔️ **Asynchronous execution improves performance.**
✔️ **Easily extend functionality without modifying existing code.**
✔️ **Ensures a clean, modular architecture.**

Whether you're handling **user events, background jobs, notifications, or real-time updates**, **observables empower you to build dynamic and reactive applications.** 🚀
