from typing import Any, Callable, Dict, List

import anyio
from lilya.compat import is_async_callable


class EventDispatcher:
    """
    A lightweight event dispatcher implementing an observable pattern.

    - Allows functions to subscribe to specific events.
    - Emits events and notifies all registered listeners asynchronously.
    - Ensures thread safety for event subscriptions and emissions.
    """

    _listeners: Dict[str, List[Callable]] = {}
    _lock = anyio.Lock()  # Ensures thread-safe modifications of listeners

    @classmethod
    async def subscribe(cls, event: str, func: Callable) -> None:
        """
        Registers a function as a listener for a given event.

        - If the event does not exist, it is initialized.
        - The function is added to the list of listeners for that event.
        - Ensures safe concurrent access with a lock.

        Args:
            event (str): The name of the event to subscribe to.
            func (Callable): The function that will be triggered when the event is emitted.

        Example:
            ```python
            async def on_user_registered():
                print("User registered!")

            await EventDispatcher.subscribe("user_registered", on_user_registered)
            ```
        """
        async with cls._lock:
            if event not in cls._listeners:
                cls._listeners[event] = []
            cls._listeners[event].append(func)

    @classmethod
    async def emit(cls, event: str, *args: Any, **kwargs: Any) -> None:
        """
        Emits an event, triggering all registered listeners asynchronously.

        - Collects all listeners for the specified event.
        - Uses `anyio.create_task_group()` to execute them concurrently.
        - Supports both synchronous and asynchronous listeners.

        Args:
            event (str): The event name to emit.
            *args (Any): Positional arguments to pass to listeners.
            **kwargs (Any): Keyword arguments to pass to listeners.

        Example:
            ```python
            async def handle_event(data):
                print(f"Received event with data: {data}")

            await EventDispatcher.subscribe("data_received", handle_event)
            await EventDispatcher.emit("data_received", {"id": 1})
            ```

        Notes:
            - Asynchronous listeners will be awaited.
            - Synchronous listeners will run in a separate thread using `anyio.to_thread.run_sync`.
        """
        async with cls._lock:
            listeners = cls._listeners.get(
                event, []
            ).copy()  # Copy to prevent modification during iteration

        async with anyio.create_task_group() as tg:
            for listener in listeners:
                if is_async_callable(listener):
                    tg.start_soon(listener, *args, **kwargs)  # Run async function
                else:
                    tg.start_soon(
                        anyio.to_thread.run_sync, listener, *args, **kwargs
                    )  # Run sync function in a separate thread
