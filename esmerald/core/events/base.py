from typing import Any, Callable, Dict, List, Optional

import anyio
from lilya.compat import is_async_callable


class EventDispatcher:
    """
    A thread-safe event dispatcher that allows registering event listeners and emitting events asynchronously.

    - Uses an internal lock to ensure thread safety when modifying the listener registry.
    - Supports both synchronous and asynchronous event listeners.
    - Uses `anyio.create_task_group()` to handle multiple event listeners concurrently.

    This enables a flexible event-driven system where functions can subscribe to and react to events.
    """

    _listeners: Dict[str, List[Callable]] = {}
    _lock = anyio.Lock()  # Ensures thread safety when modifying listeners

    @classmethod
    async def register(cls, func: Callable, listen: Optional[List[str]] = None) -> None:
        """
        Registers a function as a listener for specific events.

        - If an event does not exist in `_listeners`, it will be created.
        - The function will be added to the list of listeners for each specified event.
        - Ensures thread safety using an `anyio.Lock`.

        Args:
            func (Callable): The function to register as an event listener.
            listen (Optional[List[str]]): A list of event names to listen for.

        Example:
            ```python
            async def on_user_created():
                print("User created event received")

            await EventDispatcher.register(on_user_created, ["user_created"])
            ```
        """
        if not listen:
            return

        async with cls._lock:
            for event in listen:
                if event not in cls._listeners:
                    cls._listeners[event] = []
                cls._listeners[event].append(func)

    @classmethod
    async def emit(cls, event: str, *args: Any, **kwargs: Any) -> None:
        """
        Emits an event and triggers all registered listeners for that event.

        - Listeners are retrieved in a thread-safe manner.
        - Uses `anyio.create_task_group()` to run multiple listeners concurrently.
        - Both synchronous and asynchronous listeners are supported.

        Args:
            event (str): The event name to trigger.
            *args (Any): Positional arguments to pass to the listeners.
            **kwargs (Any): Keyword arguments to pass to the listeners.

        Example:
            ```python
            async def send_email():
                print("Email sent")

            await EventDispatcher.register(send_email, ["email_sent"])
            await EventDispatcher.emit("email_sent")
            ```

        Notes:
            - Asynchronous functions will be awaited.
            - Synchronous functions will be executed in a separate thread using `anyio.to_thread.run_sync`.
        """
        async with cls._lock:
            listeners = cls._listeners.get(event, []).copy()  # Copy to avoid mutation issues

        async with anyio.create_task_group() as tg:
            for listener in listeners:
                if is_async_callable(listener):
                    tg.start_soon(listener, *args, **kwargs)  # Async listener
                else:
                    tg.start_soon(
                        anyio.to_thread.run_sync, listener, *args, **kwargs
                    )  # Sync listener
